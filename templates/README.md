# templates/

All HTML templates for DCRS. Django is configured to look here first (`DIRS = [BASE_DIR / "templates"]`).

## Layout

```
templates/
├── base.html                   # Root layout — three shells
├── partials/
│   ├── sidebar.html            # Staff left navigation
│   ├── navbar.html             # Staff top bar with user menu
│   ├── messages.html           # Django flash message renderer
│   └── pagination.html         # Reusable pagination controls
├── accounts/
│   ├── login.html              # Login page (public)
│   ├── otp_verify.html         # OTP entry page (stub)
│   ├── password_reset.html     # Password reset request form
│   └── password_reset_email.txt # Plain-text reset email body
├── citizens/
│   ├── home.html               # Public landing page
│   ├── portal.html             # Citizen portal (logged-in CITIZEN)
│   ├── register.html           # Citizen registration form
│   ├── citizen_list.html       # Staff — paginated citizen list
│   ├── citizen_detail.html     # Staff — full citizen profile
│   └── citizen_status.html     # Staff — status summary card
├── issues/
│   ├── issue_submit.html       # Log a new issue
│   ├── issue_list.html         # Issue table with filters
│   ├── issue_detail.html       # Full issue with comments
│   └── issue_update.html       # Change status / assign officer
├── notifications/
│   ├── sms_compose.html        # Compose SMS to individual
│   ├── sms_broadcast.html      # Broadcast to ward
│   └── sms_log.html            # Delivery log table
└── reports/
    ├── dashboard.html          # Main staff dashboard
    ├── registration_report.html # Filterable citizen report
    └── audit_log.html          # Paginated audit trail
```

## base.html — three shells

`base.html` renders a different outer layout depending on the authenticated state and role of the current user:

| Condition | Shell rendered |
|---|---|
| `user.is_authenticated` and `user.role == 'CITIZEN'` | **Citizen shell** — simple header with logo and sign-out button, no sidebar |
| `user.is_authenticated` (ADMIN or OFFICER) | **Staff shell** — full sidebar + top navbar |
| Not authenticated | **Public shell** — minimal header with DCRS logo and Officer Login link |

All three shells share the same `{% block content %}` so individual templates do not need to know which shell they are in.

## Partials

### `sidebar.html`
Staff-only left navigation. Sections: Main (Dashboard, Citizens, Issues), Communications (Compose SMS, Broadcast, SMS Log), Analytics (Reports, Audit Trail). Includes user name and role in the footer.

### `navbar.html`
Top bar for staff shell. Shows breadcrumb, page title (`{% block page_title %}`), theme toggle, role badge, and user dropdown with sign-out.

### `messages.html`
Renders Django's `messages` framework alerts (success, warning, error, info) using Bootstrap alert classes.

### `pagination.html`
Include this partial in any list view that uses Django's `Paginator`:
```html
{% include 'partials/pagination.html' with page_obj=page_obj %}
```

## Extending base.html

Every page template should start with:

```html
{% extends 'base.html' %}
{% block title %}Page Title — DCRS{% endblock %}
{% block page_title %}Page Title{% endblock %}  {# staff navbar only #}

{% block content %}
  ... your content ...
{% endblock %}
```
