# apps/reports/

Provides the analytics and accountability layer — a real-time operations dashboard, filterable registration reports, and a full audit trail of every action taken in the system.

## Model: `AuditLog`

Every significant CREATE, UPDATE, or SEND action in DCRS writes an audit entry.

| Field | Type | Notes |
|---|---|---|
| `actor` | ForeignKey → User (nullable) | Who performed the action |
| `action` | CharField | `CREATE`, `UPDATE`, `DELETE`, `SEND`, etc. |
| `entity_type` | CharField | What was affected (`User`, `Citizen`, `Issue`, `SMS`) |
| `entity_id` | CharField | The ID or name of the affected record |
| `summary` | CharField | Human-readable description of what changed |
| `metadata` | JSONField | Optional extra context (e.g. old/new values) |
| `created_at` | DateTimeField | When the action occurred |

## Views

### `DashboardView` — `/portal/reports/dashboard/`

The main staff landing page after login. Shows live counts and recent activity:

- Total citizens registered
- Pending approvals
- Open/active issues
- SMS sent today
- 5 most recent citizen registrations
- 5 most recent issues
- 8 most recent audit log entries

### `RegistrationReportView` — `/portal/reports/`

Filterable table of all citizen registrations. URL parameters:

| Param | Effect |
|---|---|
| `?ward=sinza` | Filter citizens by ward name (case-insensitive contains) |
| `?status=PENDING` | Filter by approval status |

Both filters can be combined: `?ward=kariakoo&status=APPROVED`

### `AuditLogView` — `/portal/reports/audit/`

Paginated (15 per page) list of all audit entries, newest first. Shows actor, action, entity type, entity ID, summary, and timestamp.

## Who writes audit logs?

Currently audit entries are written manually in the seed command. To wire real-time audit logging:

1. Add a post-save signal in each app's `signals.py`
2. Or use a third-party package like `django-auditlog` or `django-simple-history`
3. Call `AuditLog.objects.create(...)` from any view that changes data
