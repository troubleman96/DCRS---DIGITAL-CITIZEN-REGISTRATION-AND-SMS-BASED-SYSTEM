# apps/issues/

Manages community issues reported by or on behalf of citizens. Supports full lifecycle tracking from open to closed, with officer assignment, internal notes, district escalation, and comments.

## Models

### `Issue`

| Field | Type | Notes |
|---|---|---|
| `reference_no` | CharField (auto) | `ISS-XXXXXXXXXX` — generated on first save |
| `citizen` | ForeignKey → Citizen | Who reported the issue |
| `title` | CharField | Short description (max 180 chars) |
| `description` | TextField | Full details |
| `category` | CharField (choices) | `SANITATION`, `ROAD`, `WATER`, `LIGHTING`, `SECURITY`, `OTHER` |
| `priority` | CharField (choices) | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `status` | CharField (choices) | See lifecycle below |
| `ward` | ForeignKey → Ward | Where the issue is located |
| `assigned_officer` | ForeignKey → User (nullable) | Officer handling the issue |
| `internal_notes` | TextField | Staff-only notes (not shown to citizens) |
| `escalated_to_district` | BooleanField | True when escalated beyond ward level |
| `closed_at` | DateTimeField | Set when status becomes CLOSED |

### `IssueComment`

| Field | Type | Notes |
|---|---|---|
| `issue` | ForeignKey → Issue | Parent issue |
| `author` | ForeignKey → User | Officer who wrote the comment |
| `body` | TextField | Comment text |
| `is_internal` | BooleanField | If True, only staff can see it |

## Status lifecycle

```
OPEN
 │
 ├──► IN_PROGRESS   (assigned to officer, work started)
 │       │
 │       ├──► ESCALATED    (sent to district, beyond ward scope)
 │       │
 │       └──► RESOLVED     (problem fixed, pending citizen confirmation)
 │                │
 │                └──► CLOSED    (confirmed resolved, record sealed)
 └──► CLOSED  (admin can force-close directly)
```

## Priority levels

| Priority | Meaning |
|---|---|
| LOW | Minor inconvenience, no urgency |
| MEDIUM | Affects some residents, should be addressed within weeks |
| HIGH | Significant impact, address within days |
| CRITICAL | Danger to life or property, immediate response required |

## Views

| View | URL | Access |
|---|---|---|
| `IssueListView` | `/issues/` | Staff — all issues, paginated |
| `IssueCreateView` | `/issues/submit/` | Staff — log a new issue |
| `IssueDetailView` | `/issues/<pk>/` | Staff — full issue with comments |
| `IssueUpdateView` | `/issues/<pk>/update/` | Staff — change status, assign officer |

## Signals

`signals.py` is available for post-save hooks (e.g. auto-SMS when an issue status changes to RESOLVED). Check the file for active hooks.
