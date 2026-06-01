# apps/notifications/

Handles all SMS communication in DCRS — composing messages to individual citizens, broadcasting to entire wards, managing reusable Kiswahili templates, and logging delivery status.

## Models

### `SMSTemplate`

Reusable message templates with placeholder variables.

| Field | Type | Notes |
|---|---|---|
| `name` | CharField (unique) | Human-readable name |
| `slug` | SlugField (unique) | Machine key (e.g. `registration_approved`) |
| `body` | TextField | Message body with `{variable}` placeholders |
| `is_active` | BooleanField | Only active templates appear in compose UI |

#### Seeded templates

| Slug | Purpose |
|---|---|
| `registration_approved` | Sent when a citizen's registration is approved |
| `registration_rejected` | Sent when a citizen's registration is rejected |
| `issue_received` | Sent when a new issue is logged |
| `issue_resolved` | Sent when an issue is marked resolved |
| `broadcast_general` | General ward-wide announcement |

### `SMSLog`

A record of every SMS sent or attempted.

| Field | Type | Notes |
|---|---|---|
| `recipient` | CharField | Phone number (e.g. `+255710001001`) |
| `message_body` | TextField | Actual text sent |
| `status` | CharField (choices) | `QUEUED`, `SENT`, `DELIVERED`, `FAILED` |
| `provider` | CharField | Gateway name (currently `Internal Simulator`) |
| `reference_id` | CharField | Provider's message ID for delivery tracking |
| `error_message` | TextField | Populated on FAILED status |
| `sent_at` | DateTimeField | When the message was dispatched |

## Views

| View | URL | What it does |
|---|---|---|
| `SMSComposeView` | `/portal/sms/compose/` | Send a message to a single recipient |
| `SMSBroadcastView` | `/portal/sms/broadcast/` | Send a message to all citizens in a ward |
| `SMSLogView` | `/portal/sms/log/` | Paginated delivery history |

## Service layer

`services.py` contains the SMS sending logic. Currently uses an **Internal Simulator** that logs the message to the database without hitting a real gateway. To integrate a real provider (e.g. Beem Africa, Africa's Talking, Twilio):

1. Add the provider's SDK to `requirements/base.txt`
2. Replace the simulator logic in `services.py` with the provider API call
3. Store API credentials in environment variables, not in `settings.py`
