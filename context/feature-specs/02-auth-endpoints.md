Read `progress-tracker.md`, `architecture-context.md`, `api-context.md`, and `code-standards.md` before starting.

# 02 — Auth Endpoints

Wire up and verify every authentication endpoint end to end. The models, views, and URLs for `features/auth` are already written. This spec makes them fully functional and manually tested.

Do not rebuild anything from scratch. Only fix gaps, add missing pieces, and verify each endpoint works with real HTTP calls.

---

## Endpoints To Verify

All endpoints live under `/api/v1/auth/`. Every response must use the standard envelope:

```json
{
  "success": true,
  "data": { ... },
  "message": "OK",
  "errors": null,
  "meta": null
}
```

---

### POST `/api/v1/auth/login/`

**Auth required:** No

**Request:**
```json
{
  "username": "admin",
  "password": "adminpass"
}
```

**Success response `200`:**
```json
{
  "success": true,
  "data": {
    "access": "eyJ...",
    "refresh": "eyJ...",
    "user": {
      "id": 1,
      "username": "admin",
      "full_name": "Admin User",
      "email": "admin@girinka.rw",
      "role": "ADMIN",
      "district": null,
      "is_active": true,
      "is_verified": false,
      "created_at": "2026-05-02T10:00:00+02:00"
    }
  }
}
```

**Error `400` — wrong credentials:**
```json
{
  "success": false,
  "message": "Invalid credentials.",
  "errors": { "non_field_errors": ["Invalid credentials."] }
}
```

**Error `400` — deactivated account:**
```json
{
  "success": false,
  "message": "Account is deactivated.",
  "errors": { "non_field_errors": ["Account is deactivated."] }
}
```

**Verify:**
- `curl -X POST http://localhost:8000/api/v1/auth/login/ -H "Content-Type: application/json" -d '{"username":"admin","password":"adminpass"}'`
- Response contains `access` and `refresh` tokens
- `last_login` is updated in the database after successful login

---

### POST `/api/v1/auth/logout/`

**Auth required:** Yes

**Request:**
```json
{ "refresh": "eyJ..." }
```

**Success response `200`:**
```json
{ "success": true, "data": { "detail": "Logged out successfully." } }
```

**Verify:**
- Token is blacklisted — using it again for refresh must return `401`

---

### POST `/api/v1/auth/token/refresh/`

**Auth required:** No

**Request:**
```json
{ "refresh": "eyJ..." }
```

**Success `200`:** Returns new `access` and new `refresh` tokens.

**Error `401`:** When refresh token is expired, blacklisted, or invalid.

**Verify:**
- Use the new `access` token in a protected request — it must work
- Use the old `refresh` token again — it must return `401` (rotation enforced)

---

### POST `/api/v1/auth/password/reset/`

**Auth required:** No

**Request:**
```json
{ "email": "admin@girinka.rw" }
```

**Success `200`** (always, regardless of whether email exists):
```json
{ "success": true, "data": { "detail": "If this email is registered, a reset code has been sent." } }
```

**What happens internally:**
1. Look up user by email (case-insensitive)
2. If found: generate 6-digit OTP, create `OTPCode` record with `expires_at = now() + 10 minutes`
3. Call `send_password_reset_email(to, user_name, otp_code)` from `features/notifications/utils.py`
4. If not found: do nothing — still return 200

**Verify:**
- After calling this, check `OTPCode` table — a record must exist for the user
- `is_used = False`, `expires_at` is ~10 minutes in the future

---

### POST `/api/v1/auth/password/confirm/`

**Auth required:** No

**Request:**
```json
{
  "email": "admin@girinka.rw",
  "otp_code": "482951",
  "new_password": "NewSecurePass@2026"
}
```

**Success `200`:**
```json
{ "success": true, "data": { "detail": "Password reset successful." } }
```

**Error `400` — wrong or expired OTP:**
```json
{
  "success": false,
  "message": "Invalid or expired OTP.",
  "errors": { "detail": "Invalid or expired OTP." }
}
```

**What happens internally:**
1. Find user by email
2. Find `OTPCode` where `user=user`, `code=otp_code`, `is_used=False`, `expires_at > now()`
3. If found: set new password, mark `OTPCode.is_used = True`
4. If not found: return 400

**Verify:**
- After success, old password no longer works for login
- New password works for login
- The same OTP cannot be used twice (returns 400 on second attempt)

---

### POST `/api/v1/auth/password/change/`

**Auth required:** Yes

**Request:**
```json
{
  "old_password": "adminpass",
  "new_password": "NewSecurePass@2026"
}
```

**Success `200`:**
```json
{ "success": true, "data": { "detail": "Password changed successfully." } }
```

**Error `400` — wrong current password:**
```json
{ "success": false, "message": "Wrong password." }
```

**Verify:**
- Only authenticated user can change their own password
- Wrong `old_password` returns 400, not 401

---

### GET `/api/v1/auth/me/`

**Auth required:** Yes

**Success `200`:** Returns the authenticated user's full profile.

```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "admin",
    "full_name": "Admin User",
    "email": "admin@girinka.rw",
    "phone_number": null,
    "role": "ADMIN",
    "district": null,
    "national_id": null,
    "is_active": true,
    "is_verified": false,
    "last_login": "2026-05-02T10:30:00+02:00",
    "created_at": "2026-05-02T10:00:00+02:00"
  }
}
```

**Error `401`:** No token or expired token.

---

### PATCH `/api/v1/auth/me/`

**Auth required:** Yes

**Request** (all fields optional):
```json
{
  "full_name": "Admin User Updated",
  "email": "admin.updated@girinka.rw",
  "phone_number": "+250788123456"
}
```

**Success `200`:** Returns full updated profile.

**Cannot change:** `role`, `district`, `username` — these fields are ignored if sent.

**Verify:**
- Sending `role: "FARMER"` in the body does not change the user's role

---

## Missing Pieces To Check For

Before calling this spec complete, verify these are in place:

### `features/auth/urls.py` routes all 8 endpoints

```python
urlpatterns = [
    path("login/",            LoginView.as_view()),
    path("logout/",           LogoutView.as_view()),
    path("token/refresh/",    TokenRefreshView.as_view()),
    path("password/reset/",   PasswordResetRequestView.as_view()),
    path("password/confirm/", PasswordResetConfirmView.as_view()),
    path("password/change/",  PasswordChangeView.as_view()),
    path("me/",               MeView.as_view()),
]
```

### `girinka/urls.py` includes auth

```python
path(f"{API_PREFIX}auth/", include("features.auth.urls")),
```

### `.env` has `RESEND_API_KEY` and `FROM_EMAIL`

Without these, `send_password_reset_email` will log a warning and silently skip sending. This is acceptable for local development but must be logged clearly.

---

## Completion Criteria

- [ ] `POST /auth/login/` returns access + refresh tokens for valid credentials
- [ ] `POST /auth/login/` returns `400` for wrong credentials
- [ ] `POST /auth/logout/` blacklists the refresh token
- [ ] `POST /auth/token/refresh/` returns new tokens and old refresh is invalidated
- [ ] `POST /auth/password/reset/` creates an OTPCode record in the database
- [ ] `POST /auth/password/confirm/` changes the password and marks OTP as used
- [ ] `POST /auth/password/confirm/` returns `400` if OTP is reused
- [ ] `POST /auth/password/change/` requires correct current password
- [ ] `GET /auth/me/` returns the authenticated user's profile
- [ ] `PATCH /auth/me/` updates allowed fields and ignores role/district
- [ ] `progress-tracker.md` updated with session notes
