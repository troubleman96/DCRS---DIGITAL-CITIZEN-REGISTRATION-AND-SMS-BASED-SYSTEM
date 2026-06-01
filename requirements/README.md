# requirements/

Python dependency files split by environment.

## Files

### `base.txt` — production dependencies

```
Django>=5.0,<5.3   # Web framework
Pillow>=10         # Image processing for citizen profile photos
```

### `development.txt` — development dependencies

Includes everything in `base.txt` via `-r base.txt`, plus any dev-only packages (linters, test runners, debug tools) as they are added.

## Installing

```bash
# Development (recommended for local work)
pip install -r requirements/development.txt

# Production only
pip install -r requirements/base.txt
```

## Adding PostgreSQL support

```bash
pip install psycopg2-binary
```

Add `psycopg2-binary` to `requirements/base.txt` when targeting a PostgreSQL production server.

## Adding a real SMS gateway

When replacing the Internal Simulator with a real provider, add the gateway's Python SDK here. For example:

```
# Beem Africa
beem-client>=1.0

# Africa's Talking
africastalking>=1.0

# Twilio
twilio>=8.0
```

Then update `apps/notifications/services.py` to call the provider API.
