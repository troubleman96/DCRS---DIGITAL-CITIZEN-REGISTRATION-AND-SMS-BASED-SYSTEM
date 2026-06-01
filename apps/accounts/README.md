# apps/accounts/

Handles authentication and the custom User model for all DCRS users.

## Model: `User`

Extends Django's `AbstractUser` with the following extra fields:

| Field | Type | Purpose |
|---|---|---|
| `role` | CharField (choices) | `ADMIN`, `OFFICER`, or `CITIZEN` |
| `phone_number` | CharField (unique) | Used for SMS and OTP |
| `national_id` | CharField (unique) | Officer/admin identity verification |
| `ward` | ForeignKey → Ward | The ward an officer is responsible for |
| `is_phone_verified` | BooleanField | Whether OTP has been confirmed |
| `failed_login_attempts` | PositiveSmallIntegerField | Brute-force tracking |
| `locked_until` | DateTimeField | Null until account is temporarily locked |

### Role behaviour

```python
user.is_officer      # True if role is ADMIN or OFFICER (or is_staff)
user.is_citizen_profile  # True if role is CITIZEN
```

## Views

| View | URL | What it does |
|---|---|---|
| `OfficerLoginPageView` | `/accounts/login/` | Renders login form; redirects CITIZEN to portal, staff to dashboard |
| `OfficerLogoutView` | `/accounts/logout/` | Clears session, redirects to public home |
| `OTPVerifyView` | `/accounts/otp-verify/` | Stub page for future OTP verification flow |
| `OfficerPasswordResetView` | `/accounts/password-reset/` | Django built-in password reset with custom template |

### Role-based redirect after login

`OfficerLoginPageView.get_success_url()` checks `user.role`:
- `CITIZEN` → `citizens:portal`
- Anything else → `reports:dashboard`

## Forms

- `OfficerLoginForm` — extends `AuthenticationForm` with Bootstrap-styled widgets
- `OTPVerificationForm` — single 6-character OTP input (UI only, not yet wired to a provider)

## Settings used

```python
AUTH_USER_MODEL = "accounts.User"
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "reports:dashboard"   # fallback; overridden per role in view
LOGOUT_REDIRECT_URL = "citizens:home"
SESSION_COOKIE_AGE = 1800                  # 30-minute idle timeout
```
