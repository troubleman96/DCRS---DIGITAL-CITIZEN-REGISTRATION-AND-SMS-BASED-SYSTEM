# apps/notifications/

Handles all SMS and in-app notification communication in DCRS — real outbound SMS via **SendAfrica**, delivery-status tracking, staff-relayed two-way SMS on issues, and the bell-icon notification inbox used by both staff and citizens.

## SMS delivery: SendAfrica integration

`services.py::send_sms(recipient, message_body, reference_id="")` is the single entry point every part of the app calls to send an SMS. It has two modes, chosen automatically:

- **`SENDAFRICA_API_KEY` set** → calls `POST {SENDAFRICA_BASE_URL}/v1/sms/` with an `X-API-Key` header. On success, stores the returned `message_id` in `SMSLog.reference_id` and sets `status=SENT`. On any SendAfrica error (`invalid_phone`, `insufficient_credits`, `rate_limit_exceeded`, etc.) or network exception, sets `status=FAILED` with `error_message` populated — the caller never has to handle exceptions itself.
- **No API key configured** → falls back to an "Internal Simulator" that creates the `SMSLog` as `SENT` instantly, with no network call. This is the default for local dev/demo — no SendAfrica account required to run the app.

```python
# .env
SENDAFRICA_BASE_URL=https://api.sendafrica.online
SENDAFRICA_API_KEY=                 # blank = simulator mode
SENDAFRICA_SENDER_ID=                # optional sender ID shown on the recipient's phone
```

### Delivery webhook

`SMSCallbackView` (CSRF-exempt, `POST /portal/sms/callback/`) receives SendAfrica's delivery-status push — `{"message_id": ..., "status": "delivered"|"failed"|"sent"}` — and updates the matching `SMSLog.status` by `reference_id`. Register this URL in the SendAfrica dashboard under **SMS → Settings → Callback URLs**, pointed at your deployed domain (it can't be `localhost`):

```
https://<your-domain>/portal/sms/callback/
```

Until that's configured, every send still shows `SENT` (accepted by the network) but never automatically flips to `DELIVERED`.

### Phone number format

SendAfrica accepts Tanzania numbers in `07XXXXXXXX`, `+2557XXXXXXXX`, or `2557XXXXXXXX` form and normalises automatically. In practice, `06XX`-prefixed numbers (Airtel/Halotel ranges outside the documented `071`–`078` list) have also been confirmed to work against the live API.

## Models

### `SMSTemplate`

Reusable message templates with placeholder variables (not currently auto-applied — available for compose UI convenience).

| Field | Type | Notes |
|---|---|---|
| `name` | CharField (unique) | Human-readable name |
| `slug` | SlugField (unique) | Machine key (e.g. `registration_approved`) |
| `body` | TextField | Message body with `{variable}` placeholders |
| `is_active` | BooleanField | Only active templates appear in compose UI |

### `SMSLog`

A record of every SMS sent, attempted, or staff-logged as received.

| Field | Type | Notes |
|---|---|---|
| `recipient` | CharField | Phone number |
| `message_body` | TextField | Actual text sent/received |
| `status` | CharField (choices) | `QUEUED`, `SENT`, `DELIVERED`, `FAILED` |
| `provider` | CharField | `SendAfrica`, `Internal Simulator`, or `Staff-logged (phone)` |
| `reference_id` | CharField | SendAfrica's `message_id`, used to match delivery webhook callbacks |
| `error_message` | TextField | Populated on FAILED status |
| `sent_at` | DateTimeField | When the message was dispatched |
| `direction` | CharField (choices) | `OUTBOUND` (default) or `INBOUND` — staff-relayed two-way SMS |
| `issue` | ForeignKey → Issue (nullable) | Threads this log entry onto an issue's SMS Conversation card |
| `logged_by` | ForeignKey → User (nullable) | Staff member who manually logged an inbound message |

### `Notification`

The web notification inbox — bell icon, read/unread.

| Field | Type | Notes |
|---|---|---|
| `recipient` | ForeignKey → User | Who sees this in their bell dropdown/inbox |
| `message` | CharField | The notification text |
| `related_issue` | ForeignKey → Issue (nullable) | Deep-links the notification to an issue when relevant |
| `related_citizen` | ForeignKey → Citizen (nullable) | Deep-links the notification to a citizen record (e.g. new registrations) |
| `is_read` | BooleanField | Toggled via the mark-read endpoints |
| `created_at` | DateTimeField | |

Created by signals in `apps/citizens/signals.py` and `apps/issues/signals.py` (see those apps' READMEs) — not created directly by this app. This includes an admin/ward-officer alert on every new citizen registration (`notify_officers_of_new_registration`): the matching ward officer(s) **and every admin** (admins aren't ward-filtered — they oversee the whole system) get both the web notification and a real SMS to their own phone number.

## Views

| View | URL | What it does |
|---|---|---|
| `ComposeSMSView` | `/portal/sms/compose/` | Send a message to a single recipient. Accepts `?recipient=` and `?issue=` query params to pre-fill and thread the send onto an issue |
| `BroadcastSMSView` | `/portal/sms/broadcast/` | Send a message to all citizens in a ward (or everyone if left blank) |
| `SMSLogListView` | `/portal/sms/log/` | Paginated delivery history with stat counts |
| `LogIncomingSMSView` | `/portal/sms/log-incoming/` (POST only) | **Staff-relayed two-way SMS** — since SendAfrica has no inbound webhook/shortcode, staff manually log what a citizen said over a phone call here. Creates an `INBOUND` `SMSLog`; if "send reply" is checked, also sends a real outbound SMS via `send_sms()` and threads both onto the same issue |
| `SMSCallbackView` | `/portal/sms/callback/` (POST only, CSRF-exempt) | SendAfrica delivery webhook receiver |
| `NotificationListView` | `/portal/sms/inbox/` | The logged-in user's full notification history |
| `NotificationMarkReadView` | `/portal/sms/inbox/read-all/` and `/portal/sms/inbox/<pk>/read/` (POST only) | Marks one or all of the user's notifications as read |

## Context processor

`context_processors.py::notifications` is registered in `config/settings.py` and injects `unread_notifications` (latest 6) and `unread_notifications_count` into every template for authenticated users — this is what powers the bell dropdown in both the staff navbar (`templates/partials/navbar.html`) and the citizen shell header (`templates/base.html`).

## Two-way SMS — an honest limitation

SendAfrica's API is outbound-send + delivery-webhook only; it does not provide a shared inbound shortcode or reply-parsing endpoint. "Two-way SMS" in DCRS is therefore **staff-relayed**: a citizen calls or texts the officer's published phone number directly (outside the app), and the officer logs what was said via `LogIncomingSMSView`, optionally sending a reply in the same action. The issue detail page's "SMS Conversation" card threads inbound and outbound messages together and is labelled accordingly — this is not automated inbound parsing.
