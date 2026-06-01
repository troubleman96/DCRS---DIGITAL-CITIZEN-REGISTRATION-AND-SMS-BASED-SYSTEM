# apps/

This directory contains every Django application in the DCRS project. Each app is a self-contained module with its own models, views, URLs, forms, admin registration, and templates.

## App summary

| App | Responsibility |
|---|---|
| `accounts` | Custom User model, login/logout, OTP stub, password reset |
| `localities` | Geographic hierarchy: Region → District → Ward → Mtaa |
| `citizens` | Citizen registration, profiles, approval workflow, citizen portal |
| `issues` | Community issue logging, assignment, escalation, resolution |
| `notifications` | SMS templates, compose to individual, broadcast to ward, delivery log |
| `reports` | Real-time dashboard, registration reports, audit trail |

## App load order

Apps are registered in `config/settings.py` in this order:

```
accounts → localities → citizens → issues → notifications → reports
```

The order matters because `citizens` has a ForeignKey to `localities`, and `issues` has ForeignKeys to both `citizens` and `localities`. Django resolves these at migration time, but the order avoids circular import surprises.

## Adding a new app

```bash
python manage.py startapp myapp apps/myapp
```

Then add `"apps.myapp"` to `INSTALLED_APPS` in `config/settings.py` and create `apps/myapp/urls.py`, then wire it into `config/urls.py`.
