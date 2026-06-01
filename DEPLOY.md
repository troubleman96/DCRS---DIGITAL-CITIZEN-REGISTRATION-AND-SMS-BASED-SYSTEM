# DCRS — Deployment Guide

> **Target:** Ubuntu 22.04 LTS VPS  
> **Domain:** `dcrs.simamia.online`  
> **Internal port:** `8077`  
> **Stack:** Django 5 · Gunicorn · Nginx · PostgreSQL · Let's Encrypt SSL

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [DNS Setup](#dns-setup)
3. [Server Preparation](#server-preparation)
4. [PostgreSQL Setup](#postgresql-setup)
5. [Application Setup](#application-setup)
6. [Environment Variables](#environment-variables)
7. [Django Production Config](#django-production-config)
8. [Gunicorn Setup](#gunicorn-setup)
9. [Systemd Service](#systemd-service)
10. [Nginx Configuration](#nginx-configuration)
11. [SSL Certificate (Let's Encrypt)](#ssl-certificate-lets-encrypt)
12. [Firewall](#firewall)
13. [First Deploy Checklist](#first-deploy-checklist)
14. [Updating the App](#updating-the-app)
15. [Useful Commands](#useful-commands)
16. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- A VPS running Ubuntu 22.04 LTS (minimum 1 vCPU, 1 GB RAM)
- Root or sudo access
- Domain `dcrs.simamia.online` you control (manage DNS records)
- SSH access to the server

---

## DNS Setup

In your domain registrar or DNS panel, add an **A record** pointing to your server's public IP:

| Type | Name | Value | TTL |
|---|---|---|---|
| A | `dcrs` | `YOUR_SERVER_IP` | 300 |

Wait for DNS to propagate (usually 5–15 minutes) before requesting an SSL certificate.

Verify propagation:
```bash
dig dcrs.simamia.online +short
# Should return your server IP
```

---

## Server Preparation

### 1. Update the system

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install system dependencies

```bash
sudo apt install -y \
    python3.12 \
    python3.12-venv \
    python3-pip \
    python3.12-dev \
    libpq-dev \
    postgresql \
    postgresql-contrib \
    nginx \
    certbot \
    python3-certbot-nginx \
    git \
    curl \
    ufw
```

### 3. Create a dedicated system user

```bash
sudo useradd --system --shell /bin/bash --home /var/www/dcrs --create-home dcrs
```

---

## PostgreSQL Setup

```bash
sudo -u postgres psql
```

Inside the PostgreSQL shell:

```sql
CREATE DATABASE dcrs_db;
CREATE USER dcrs_user WITH PASSWORD 'CHANGE_THIS_STRONG_PASSWORD';
ALTER ROLE dcrs_user SET client_encoding TO 'utf8';
ALTER ROLE dcrs_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE dcrs_user SET timezone TO 'Africa/Dar_es_Salaam';
GRANT ALL PRIVILEGES ON DATABASE dcrs_db TO dcrs_user;
\q
```

> Replace `CHANGE_THIS_STRONG_PASSWORD` with a strong random password. Save it — you will need it in the `.env` file.

---

## Application Setup

### 1. Clone the repository

```bash
sudo -u dcrs git clone git@github.com:troubleman96/DCRS---DIGITAL-CITIZEN-REGISTRATION-AND-SMS-BASED-SYSTEM.git /var/www/dcrs/app
cd /var/www/dcrs/app
```

### 2. Create and activate virtual environment

```bash
sudo -u dcrs python3.12 -m venv /var/www/dcrs/venv
source /var/www/dcrs/venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install --upgrade pip
pip install -r requirements/base.txt
pip install gunicorn psycopg2-binary
```

### 4. Create directories for media and static files

```bash
sudo -u dcrs mkdir -p /var/www/dcrs/app/media
sudo -u dcrs mkdir -p /var/www/dcrs/app/staticfiles
```

---

## Environment Variables

Create the `.env` file — **never commit this file to git**:

```bash
sudo -u dcrs nano /var/www/dcrs/app/.env
```

Paste and fill in all values:

```env
# Django core
SECRET_KEY=replace-with-a-50-plus-char-random-string
DEBUG=False
ALLOWED_HOSTS=dcrs.simamia.online,www.dcrs.simamia.online

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=dcrs_db
DB_USER=dcrs_user
DB_PASSWORD=CHANGE_THIS_STRONG_PASSWORD
DB_HOST=localhost
DB_PORT=5432

# Email (update when you have a real SMTP provider)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@dcrs.simamia.online

# Static / Media
STATIC_ROOT=/var/www/dcrs/app/staticfiles
MEDIA_ROOT=/var/www/dcrs/app/media
```

Generate a secure `SECRET_KEY`:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(60))"
```

---

## Django Production Config

Update `config/settings.py` to read from environment variables.

Open the file:
```bash
sudo -u dcrs nano /var/www/dcrs/app/config/settings.py
```

Replace the top section with:

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file if present (development convenience)
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass

SECRET_KEY = os.environ["SECRET_KEY"]
DEBUG = os.getenv("DEBUG", "False") == "True"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost").split(",")
```

Replace the `DATABASES` block with:

```python
DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME":   os.getenv("DB_NAME", BASE_DIR / "db.sqlite3"),
        "USER":   os.getenv("DB_USER", ""),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST":   os.getenv("DB_HOST", ""),
        "PORT":   os.getenv("DB_PORT", ""),
    }
}
```

Install `python-dotenv` for the `.env` loader:
```bash
pip install python-dotenv
echo "python-dotenv" >> /var/www/dcrs/app/requirements/base.txt
```

---

## Gunicorn Setup

Test that Gunicorn can serve the app on port 8077:

```bash
cd /var/www/dcrs/app
source /var/www/dcrs/venv/bin/activate

# Run migrations and seed first
python manage.py migrate
python manage.py seed
python manage.py collectstatic --noinput

# Test Gunicorn manually
gunicorn config.wsgi:application \
    --bind 0.0.0.0:8077 \
    --workers 3 \
    --timeout 60
```

If the app responds at `http://YOUR_SERVER_IP:8077`, Gunicorn is working. Press `Ctrl+C` to stop.

---

## Systemd Service

Create a systemd unit so Gunicorn starts automatically on boot and restarts on failure.

```bash
sudo nano /etc/systemd/system/dcrs.service
```

Paste:

```ini
[Unit]
Description=DCRS — District Citizen Response System (Gunicorn)
After=network.target postgresql.service
Requires=postgresql.service

[Service]
User=dcrs
Group=www-data
WorkingDirectory=/var/www/dcrs/app
EnvironmentFile=/var/www/dcrs/app/.env
ExecStart=/var/www/dcrs/venv/bin/gunicorn \
          config.wsgi:application \
          --bind 127.0.0.1:8077 \
          --workers 3 \
          --worker-class sync \
          --timeout 60 \
          --access-logfile /var/log/dcrs/access.log \
          --error-logfile /var/log/dcrs/error.log \
          --log-level info
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Create the log directory:

```bash
sudo mkdir -p /var/log/dcrs
sudo chown dcrs:www-data /var/log/dcrs
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable dcrs
sudo systemctl start dcrs
sudo systemctl status dcrs
```

The output should show **active (running)**. Gunicorn is now bound to `127.0.0.1:8077` — it is not exposed to the internet yet. Nginx will be the only public entry point.

---

## Nginx Configuration

Create the Nginx site config:

```bash
sudo nano /etc/nginx/sites-available/dcrs
```

Paste:

```nginx
server {
    listen 80;
    server_name dcrs.simamia.online www.dcrs.simamia.online;

    # Redirect all HTTP to HTTPS (Certbot will fill this in)
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name dcrs.simamia.online www.dcrs.simamia.online;

    # SSL — managed by Certbot
    ssl_certificate     /etc/letsencrypt/live/dcrs.simamia.online/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/dcrs.simamia.online/privkey.pem;
    include             /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam         /etc/letsencrypt/ssl-dhparams.pem;

    # Security headers
    add_header X-Frame-Options           "SAMEORIGIN"   always;
    add_header X-Content-Type-Options    "nosniff"      always;
    add_header Referrer-Policy           "strict-origin" always;
    add_header X-XSS-Protection          "1; mode=block" always;

    client_max_body_size 10M;

    # Static files — served directly by Nginx (no Django involved)
    location /static/ {
        alias /var/www/dcrs/app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files — user uploads
    location /media/ {
        alias /var/www/dcrs/app/media/;
        expires 7d;
    }

    # Everything else → Gunicorn on port 8077
    location / {
        proxy_pass         http://127.0.0.1:8077;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
        proxy_connect_timeout 10s;
    }
}
```

Enable the site and test:

```bash
sudo ln -s /etc/nginx/sites-available/dcrs /etc/nginx/sites-enabled/dcrs
sudo nginx -t        # must say "syntax is ok"
sudo systemctl reload nginx
```

---

## SSL Certificate (Let's Encrypt)

Make sure DNS is already pointing to your server, then:

```bash
sudo certbot --nginx -d dcrs.simamia.online -d www.dcrs.simamia.online
```

Certbot will:
1. Verify domain ownership via HTTP challenge
2. Issue a free 90-day certificate
3. Automatically edit your Nginx config to add the SSL block
4. Set up auto-renewal via a systemd timer

Test auto-renewal:
```bash
sudo certbot renew --dry-run
```

After Certbot finishes, reload Nginx:
```bash
sudo systemctl reload nginx
```

Visit `https://dcrs.simamia.online` — you should see the DCRS landing page over HTTPS.

---

## Firewall

Only allow SSH, HTTP, and HTTPS. Block direct access to port 8077 from the internet.

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'    # opens 80 and 443
# Do NOT allow 8077 — it is internal only (Nginx → Gunicorn)
sudo ufw enable
sudo ufw status
```

Expected output:
```
Status: active
To                         Action      From
--                         ------      ----
OpenSSH                    ALLOW       Anywhere
Nginx Full                 ALLOW       Anywhere
```

Port `8077` is intentionally absent — it is only accessible from `127.0.0.1` (localhost).

---

## First Deploy Checklist

Run through this in order on a fresh server:

- [ ] Server provisioned and SSH access confirmed
- [ ] A record `dcrs.simamia.online` → server IP added and propagated
- [ ] System packages installed
- [ ] PostgreSQL running, `dcrs_db` and `dcrs_user` created
- [ ] Repository cloned to `/var/www/dcrs/app`
- [ ] Virtual environment created and dependencies installed
- [ ] `.env` file created with all values filled in
- [ ] `settings.py` updated to read from environment variables
- [ ] `python manage.py migrate` completed successfully
- [ ] `python manage.py seed` completed successfully
- [ ] `python manage.py collectstatic --noinput` completed successfully
- [ ] Gunicorn manual test passed (`http://IP:8077` responds)
- [ ] `dcrs.service` created, enabled, and showing **active (running)**
- [ ] Nginx site config created and `nginx -t` passes
- [ ] Certbot certificate issued successfully
- [ ] `https://dcrs.simamia.online` loads the app
- [ ] Login with `admin_user` / `test1234` works
- [ ] Firewall enabled with only SSH + Nginx Full allowed

---

## Updating the App

Every time you push new code, run these steps on the server:

```bash
# 1. Switch to app user
sudo -u dcrs bash

# 2. Pull latest code
cd /var/www/dcrs/app
git pull origin master

# 3. Activate venv and install any new dependencies
source /var/www/dcrs/venv/bin/activate
pip install -r requirements/base.txt

# 4. Apply any new migrations
python manage.py migrate

# 5. Collect static files
python manage.py collectstatic --noinput

# 6. Restart Gunicorn (zero-downtime reload)
exit   # back to sudo user
sudo systemctl reload dcrs

# 7. Confirm the service is still running
sudo systemctl status dcrs
```

---

## Useful Commands

| Task | Command |
|---|---|
| Check Gunicorn status | `sudo systemctl status dcrs` |
| Restart Gunicorn | `sudo systemctl restart dcrs` |
| Reload Gunicorn (no downtime) | `sudo systemctl reload dcrs` |
| View Gunicorn error log | `sudo tail -f /var/log/dcrs/error.log` |
| View Gunicorn access log | `sudo tail -f /var/log/dcrs/access.log` |
| View Nginx error log | `sudo tail -f /var/log/nginx/error.log` |
| Test Nginx config | `sudo nginx -t` |
| Reload Nginx | `sudo systemctl reload nginx` |
| Check SSL certificate expiry | `sudo certbot certificates` |
| Force SSL renewal | `sudo certbot renew --force-renewal` |
| Django shell on server | `sudo -u dcrs /var/www/dcrs/venv/bin/python /var/www/dcrs/app/manage.py shell` |
| Re-seed database | `sudo -u dcrs /var/www/dcrs/venv/bin/python /var/www/dcrs/app/manage.py seed` |
| Wipe and re-seed | `sudo -u dcrs /var/www/dcrs/venv/bin/python /var/www/dcrs/app/manage.py seed --flush` |
| Check PostgreSQL | `sudo systemctl status postgresql` |
| Connect to DB | `sudo -u postgres psql dcrs_db` |

---

## Troubleshooting

### 502 Bad Gateway from Nginx

Nginx can reach the server but Gunicorn is not responding.

```bash
sudo systemctl status dcrs         # is it running?
sudo tail -20 /var/log/dcrs/error.log  # check for Python errors
sudo journalctl -u dcrs -n 50      # systemd logs
```

Common causes:
- `.env` file missing or has wrong values
- Database is down or credentials are wrong
- `SECRET_KEY` not set (Django raises `ImproperlyConfigured`)

### Static files return 404

```bash
sudo -u dcrs /var/www/dcrs/venv/bin/python /var/www/dcrs/app/manage.py collectstatic --noinput
sudo nginx -t && sudo systemctl reload nginx
```

Check the `alias` path in the Nginx config matches `STATIC_ROOT` in `.env`.

### SSL certificate errors

```bash
sudo certbot renew --dry-run     # test renewal
sudo certbot certificates        # check expiry date
```

If the domain no longer resolves to the server IP, Certbot cannot renew. Fix the DNS A record first.

### Database connection refused

```bash
sudo systemctl status postgresql
sudo systemctl start postgresql
```

Check `.env` has the correct `DB_PASSWORD`, `DB_HOST=localhost`, and `DB_PORT=5432`.

### Permission denied on media or static files

```bash
sudo chown -R dcrs:www-data /var/www/dcrs/app/staticfiles
sudo chown -R dcrs:www-data /var/www/dcrs/app/media
sudo chmod -R 755 /var/www/dcrs/app/staticfiles
sudo chmod -R 755 /var/www/dcrs/app/media
```

### App shows DEBUG error page in production

`DEBUG=True` is set in `.env`. Change it to `DEBUG=False` and restart:
```bash
sudo systemctl restart dcrs
```

### Port 8077 accessible from the internet

This should not happen if UFW is configured correctly. Check:
```bash
sudo ufw status
```

`8077` must not appear in the allowed rules. If it does:
```bash
sudo ufw delete allow 8077
```
