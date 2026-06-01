# apps/citizens/

Manages citizen records — the core entity of the DCRS system. Handles registration, profile storage, approval workflow, and the citizen-facing portal.

## Model: `Citizen`

| Field | Type | Notes |
|---|---|---|
| `citizen_id` | CharField (auto) | `CIT-XXXXXXXXXX` — hex UUID prefix, generated on first save |
| `user` | OneToOneField → User | Optional link to a DCRS user account (`related_name="citizen_profile"`) |
| `full_name` | CharField | Full legal name |
| `national_id` | CharField (unique) | Tanzania national ID number |
| `phone_number` | CharField (unique) | Mobile number for SMS |
| `gender` | CharField (choices) | `FEMALE`, `MALE`, `OTHER` |
| `date_of_birth` | DateField | Optional |
| `region` | ForeignKey → Region | Top-level geography |
| `district` | ForeignKey → District | Sub-region |
| `ward` | ForeignKey → Ward | Local ward |
| `mtaa` | ForeignKey → Mtaa | Street/neighbourhood (optional) |
| `profile_photo` | ImageField | Uploaded to `media/citizens/photos/` |
| `registration_notes` | TextField | Officer notes on the record |
| `status` | CharField (choices) | `PENDING` → `APPROVED` / `REJECTED` / `SUSPENDED` |

## Status workflow

```
PENDING (default on registration)
   │
   ├──► APPROVED   (officer review passes)
   ├──► REJECTED   (duplicate ID, fraud, incomplete docs)
   └──► SUSPENDED  (post-approval account action)
```

## Views

| View | URL | Access |
|---|---|---|
| `CitizenHomeView` | `/` | Public — landing page with system stats |
| `CitizenPortalView` | `/portal/` | CITIZEN only — shows own profile + their issues |
| `CitizenRegistrationView` | `/register/` | Public — create a new citizen record |
| `CitizenListView` | `/list/` | Staff — paginated list of all citizens |
| `CitizenDetailView` | `/<pk>/` | Staff — full citizen profile |
| `CitizenStatusView` | `/<pk>/status/` | Staff — status summary card |

## Management command: `seed`

Located at `management/commands/seed.py`. Populates the database with realistic Tanzanian test data covering all roles and features. Safe to run multiple times (uses `get_or_create`).

```bash
python manage.py seed              # seed, skip existing rows
python manage.py seed --flush      # wipe all seeded tables first, then re-seed
```

### What gets seeded

1. Localities — 3 regions, 5 districts, 6 wards, 5 mitaa
2. Users — admin, 2 officers, 1 citizen (all password: `test1234`)
3. Citizens — 8 records across different wards and statuses
4. Issues — 10 issues with varying priorities and statuses, plus 5 comments
5. SMS templates — 5 Kiswahili templates; 7 SMS log entries
6. Audit logs — 12 entries covering all action types

## Signals

`signals.py` is present for post-save hooks (e.g. auto-sending an SMS on status change). Check the file for what is currently wired up.
