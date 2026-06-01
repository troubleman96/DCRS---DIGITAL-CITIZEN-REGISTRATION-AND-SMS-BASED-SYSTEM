# DCRS — District Citizen Response System

A Django web application built for Tanzanian local government to manage citizen registrations, community issue tracking, and ward-level SMS communications. Designed for district offices operating under the **Dar es Salaam Region** administrative structure.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Project Structure](#project-structure)
5. [Prerequisites](#prerequisites)
6. [Installation](#installation)
7. [Database Setup](#database-setup)
8. [Running the App](#running-the-app)
9. [Test Credentials](#test-credentials)
10. [Switching to PostgreSQL](#switching-to-postgresql)
11. [User Roles](#user-roles)
12. [URL Reference](#url-reference)
13. [Key Settings](#key-settings)
14. [Production Checklist](#production-checklist)

---

## Overview

DCRS gives district officers a single command centre to:

- **Register and approve citizens** with full national ID, ward, and demographic records
- **Track community issues** (water, roads, sanitation, security, lighting) from open to resolved
- **Send SMS notifications** to individuals or broadcast to entire wards
- **Generate reports** on registrations and audit every action taken in the system

Citizens get a separate lightweight portal where they can check their registration status and view issues they have reported.

---

## Features

| Module | What it does |
|---|---|
| Citizen Registration | Full citizen profiles with national ID, gender, DOB, region/district/ward/mtaa, photo, and approval status |
| Issue Tracking | Log, prioritise (LOW→CRITICAL), assign to officers, escalate to district, resolve |
| SMS Communications | Compose to individual, broadcast to ward, template library, full delivery log |
| Role-Based Access | ADMIN, OFFICER, and CITIZEN roles with separate UIs |
| Reports & Analytics | Real-time dashboard, registration reports filterable by ward/status |
| Audit Trail | Every CREATE/UPDATE/SEND action logged with actor, entity, and summary |
| Geographic Hierarchy | Region → District → Ward → Mtaa mirroring Tanzania's official boundaries |

---

## Architecture

```
Browser
  │
  ▼
Django (views + templates)
  │
  ├── apps/accounts      ← custom User model, login/logout, OTP stub
  ├── apps/localities    ← Region / District / Ward / Mtaa
  ├── apps/citizens      ← Citizen model, registration, status
  ├── apps/issues        ← Issue + IssueComment, assignment, escalation
  ├── apps/notifications ← SMSTemplate, SMSLog, compose/broadcast views
  └── apps/reports       ← Dashboard, RegistrationReport, AuditLog
  │
  ▼
Database (SQLite for dev / PostgreSQL for production)
```

Templates extend `templates/base.html` which renders three different shells depending on authentication state:

- **Public shell** — unauthenticated visitors (landing page, register, login)
- **Citizen shell** — logged-in CITIZEN role (simple header, citizen portal)
- **Staff shell** — logged-in ADMIN/OFFICER (full sidebar with all modules)

---

## Project Structure

```
DCRS/
├── apps/                          # All Django applications
│   ├── accounts/                  # Custom user model & auth views
│   ├── citizens/                  # Citizen registration & management
│   │   └── management/commands/   # seed management command
│   ├── issues/                    # Issue tracking
│   ├── localities/                # Geographic hierarchy
│   ├── notifications/             # SMS compose, broadcast, log
│   └── reports/                   # Dashboard, reports, audit log
├── config/                        # Django project config (settings, urls, wsgi)
├── media/                         # User-uploaded files (gitignored)
├── requirements/
│   ├── base.txt                   # Production dependencies
│   └── development.txt            # Dev dependencies (includes base)
├── static/
│   ├── css/app.css                # All custom styles
│   └── js/app.js                  # Theme toggle, sidebar, interactions
├── templates/                     # All HTML templates
│   ├── base.html                  # Root layout with three shells
│   ├── partials/                  # Sidebar, navbar, messages, pagination
│   ├── accounts/                  # Login, OTP, password reset
│   ├── citizens/                  # Home, register, list, detail, portal
│   ├── issues/                    # Submit, list, detail, update
│   ├── notifications/             # Compose, broadcast, SMS log
│   └── reports/                   # Dashboard, registration report, audit log
├── db.sqlite3                     # SQLite database (gitignored)
├── manage.py                      # Django management entry point
├── seed.py                        # Legacy seed script (use manage.py seed instead)
└── .gitignore
```

---

## Prerequisites

- Python 3.10 or higher
- pip
- (Optional for production) PostgreSQL 14+

---

## Installation

### 1. Clone the repository

```bash
git clone <repo-url>
cd DCRS
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements/development.txt
```

---

## Database Setup

### SQLite (default — zero config required)

```bash
python manage.py migrate
python manage.py seed
```

### PostgreSQL (production)

1. Create a database:

```sql
CREATE DATABASE dcrs_db;
CREATE USER dcrs_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE dcrs_db TO dcrs_user;
```

2. Install the adapter:

```bash
pip install psycopg2-binary
```

3. Update `config/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'dcrs_db',
        'USER': 'dcrs_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

4. Run migrations and seed:

```bash
python manage.py migrate
python manage.py seed
```

---

## Running the App

```bash
python manage.py runserver
```

Visit: `http://127.0.0.1:8000`

---

## Test Credentials

All accounts use the password **`test1234`**.

| Role | Username | Email | Portal |
|---|---|---|---|
| Superuser / Officer | `admin` | admin@gmail.com | Staff dashboard |
| Admin | `admin_user` | admin@dcrs.go.tz | Staff dashboard |
| Officer | `officer_kinondoni` | juma.mwalimu@dcrs.go.tz | Staff dashboard |
| Officer | `officer_ilala` | fatuma.salehe@dcrs.go.tz | Staff dashboard |
| Citizen | `citizen_user` | amina.hassan@example.com | Citizen portal |

Login page: `http://127.0.0.1:8000/accounts/login/`

### Re-seeding

```bash
# Skip existing rows (safe to run anytime)
python manage.py seed

# Wipe all seeded data and start fresh
python manage.py seed --flush
```

---

## Switching to PostgreSQL

Only `config/settings.py` needs to change — the seed command and all app code are database-agnostic. After updating `DATABASES`, run `migrate` then `seed` as shown above.

---

## User Roles

### ADMIN
Full access to every module. Can create/edit users, approve citizens, manage SMS templates, and view all reports and audit logs.

### OFFICER
Can register and approve citizens, log and update issues, compose SMS, view reports. Cannot manage other users.

### CITIZEN
Restricted to the citizen portal. Can view their own registration status and the issues they have reported. Cannot access any staff screens.

---

## URL Reference

| URL | View | Access |
|---|---|---|
| `/` | Public landing page | Public |
| `/register/` | Citizen registration form | Public |
| `/portal/` | Citizen portal | CITIZEN |
| `/accounts/login/` | Login | Public |
| `/accounts/logout/` | Logout | Authenticated |
| `/portal/reports/dashboard/` | Staff dashboard | Staff |
| `/list/` | Citizen list | Staff |
| `/<pk>/` | Citizen detail | Staff |
| `/<pk>/status/` | Citizen status card | Staff |
| `/issues/` | Issue list | Staff |
| `/issues/submit/` | Submit new issue | Staff |
| `/issues/<pk>/` | Issue detail | Staff |
| `/issues/<pk>/update/` | Update issue status | Staff |
| `/portal/sms/compose/` | Compose SMS | Staff |
| `/portal/sms/broadcast/` | SMS broadcast | Staff |
| `/portal/sms/log/` | SMS delivery log | Staff |
| `/portal/reports/` | Registration report | Staff |
| `/portal/reports/audit/` | Audit trail | Staff |
| `/api/localities/` | Locality API (cascading dropdowns) | Staff |
| `/admin/` | Django admin | Superuser |

---

## Key Settings

| Setting | Value | Notes |
|---|---|---|
| `AUTH_USER_MODEL` | `accounts.User` | Custom user with role + phone |
| `LOGIN_URL` | `accounts:login` | Redirects unauthenticated requests |
| `LOGIN_REDIRECT_URL` | `reports:dashboard` | Default post-login (overridden per role in view) |
| `LOGOUT_REDIRECT_URL` | `citizens:home` | After logout |
| `SESSION_COOKIE_AGE` | `1800` | 30-minute session timeout |
| `TIME_ZONE` | `Africa/Dar_es_Salaam` | Tanzania local time |
| `EMAIL_BACKEND` | Console backend | Prints emails to terminal in dev |

---

## Production Checklist

- [ ] Set `DEBUG = False`
- [ ] Replace `SECRET_KEY` with a random 50+ character string (use `django-environ` or environment variables)
- [ ] Set `ALLOWED_HOSTS` to your actual domain
- [ ] Switch `DATABASES` to PostgreSQL
- [ ] Run `python manage.py collectstatic`
- [ ] Configure a real `EMAIL_BACKEND` (e.g. SMTP or SendGrid)
- [ ] Serve media files via nginx or object storage (S3)
- [ ] Enable HTTPS and set `SECURE_SSL_REDIRECT = True`
- [ ] Integrate a real SMS gateway (replace the Internal Simulator in `notifications/services.py`)
