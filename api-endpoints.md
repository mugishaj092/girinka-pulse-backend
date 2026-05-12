# 🐄 Girinka Pulse — Complete API Endpoint Reference

> **Base URL:** `http://localhost:8000/api/v1/`
> **Interactive Docs:** `http://localhost:8000/api/v1/docs/`
> **Total Endpoints:** 80+

---

## Authentication

All protected endpoints require:
```
Authorization: Bearer <access_token>
```

Get a token from `POST /api/v1/auth/login/`

---

## Standard Response Format

Every response is wrapped in:

```json
{
  "success": true,
  "data": {},
  "message": "OK",
  "errors": null,
  "meta": {
    "count": 100,
    "next": "http://localhost:8000/api/v1/cows/?page=2",
    "previous": null
  }
}
```

---

## Error Codes

| Code | HTTP Status | Meaning |
|------|-------------|---------|
| `INSUFFICIENT_MILK_DATA` | 422 | LSTM needs at least 7 days of milk records |
| `COW_ALREADY_DECEASED` | 422 | Cannot update a deceased cow |
| `BENEFICIARY_INACTIVE` | 422 | Beneficiary is deregistered |
| `PASSON_PENDING` | 422 | Cannot deregister while a pass-on transfer is pending |
| `DUPLICATE_TAG_NUMBER` | 409 | Cow tag number already registered |
| `DUPLICATE_NATIONAL_ID` | 409 | National ID already registered |
| `INVALID_UBUDEHE` | 400 | Only Ubudehe categories 1 and 2 qualify for Girinka |
| `MODEL_NOT_DEPLOYED` | 503 | No active ML model for this prediction type |
| `PREDICTION_FAILED` | 503 | ML service returned an error |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

---

## Role Reference

| Role | Code | Description |
|------|------|-------------|
| Farmer | `FARMER` | Own cows and milk records only |
| Cell Leader | `CELL_LEADER` | All cows and beneficiaries in their district |
| Veterinarian | `VETERINARIAN` | Health records and disease predictions |
| District Leader | `DISTRICT_LEADER` | Read-only access across full district |
| Admin | `ADMIN` | Full national access |

---

## Table of Contents

- [🔑 Authentication](#-authentication-apiapiv1auth)
- [👥 Users](#-users-apiapiv1users)
- [🗺️ Districts](#️-districts-apiapiv1districts)
- [🏠 Beneficiaries](#-beneficiaries-apiapiv1beneficiaries)
- [🐮 Cows](#-cows-apiapiv1cows)
- [🩺 Health Records](#-health-records-apiapiv1health)
- [🥛 Milk Production](#-milk-production-apiapiv1milk)
- [🚨 Alerts](#-alerts-apiapiv1alerts)
- [🤖 Predictions](#-predictions-apiapiv1predictions)
- [🔄 Pass-On Registry](#-pass-on-registry-apiapiv1passon)
- [🧬 Lineage](#-lineage-apiapiv1lineage)
- [📊 Reports](#-reports-apiapiv1reports)
- [🌤️ Weather](#️-weather-apiapiv1weather)
- [🔔 Notifications](#-notifications-apiapiv1notifications)

---

## 🔑 Authentication — `/api/v1/auth/`

### `POST /api/v1/auth/login/`

Login with username and password. Returns JWT access and refresh tokens.

**Auth required:** ❌ Public

**Request body:**
```json
{
  "username": "mugisha_joseph",
  "password": "securepass123"
}
```

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3NDYxODAwMDB9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3NDY3ODAwMDB9...",
    "user": {
      "id": 1,
      "username": "mugisha_joseph",
      "full_name": "MUGISHA Joseph",
      "email": "joseph@girinka.rw",
      "role": "CELL_LEADER",
      "district": 3,
      "is_verified": true
    }
  }
}
```

**Response `400` — Wrong credentials:**
```json
{
  "success": false,
  "message": "Invalid credentials.",
  "errors": { "non_field_errors": ["Invalid credentials."] }
}
```

---

### `POST /api/v1/auth/logout/`

Blacklist the refresh token to invalidate the session.

**Auth required:** ✅ Any role

**Request body:**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response `200`:**
```json
{
  "success": true,
  "data": { "detail": "Logged out successfully." }
}
```

---

### `POST /api/v1/auth/token/refresh/`

Exchange a valid refresh token for a new access token. The refresh token is rotated on each use.

**Auth required:** ❌ Public

**Request body:**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.NEW...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.NEW..."
  }
}
```

**Response `401` — Expired or invalid refresh token:**
```json
{
  "success": false,
  "message": "Token is invalid or expired"
}
```

---

### `POST /api/v1/auth/password/reset/`

Send a 6-digit OTP to the user's registered email via Resend. OTP expires in 10 minutes.

**Auth required:** ❌ Public

**Request body:**
```json
{
  "email": "jean.baptiste@example.com"
}
```

**Response `200`** *(always returns 200 — does not reveal if email exists):*
```json
{
  "success": true,
  "data": {
    "detail": "If this email is registered, a reset code has been sent."
  }
}
```

---

### `POST /api/v1/auth/password/confirm/`

Submit the OTP received by email along with the new password to complete the reset.

**Auth required:** ❌ Public

**Request body:**
```json
{
  "email": "jean.baptiste@example.com",
  "otp_code": "482951",
  "new_password": "NewSecurePass@2026"
}
```

**Response `200`:**
```json
{
  "success": true,
  "data": { "detail": "Password reset successful." }
}
```

**Response `400` — OTP invalid or expired:**
```json
{
  "success": false,
  "message": "Invalid or expired OTP.",
  "errors": { "detail": "Invalid or expired OTP." }
}
```

---

### `POST /api/v1/auth/password/change/`

Change password for the currently authenticated user. Requires current password.

**Auth required:** ✅ Any role

**Request body:**
```json
{
  "old_password": "OldPass@123",
  "new_password": "NewSecurePass@2026"
}
```

**Response `200`:**
```json
{
  "success": true,
  "data": { "detail": "Password changed successfully." }
}
```

**Response `400` — Wrong current password:**
```json
{
  "success": false,
  "message": "Wrong password.",
  "errors": { "detail": "Wrong password." }
}
```

---

### `GET /api/v1/auth/me/`

Get the full profile of the currently authenticated user.

**Auth required:** ✅ Any role

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "mugisha_joseph",
    "email": "joseph@girinka.rw",
    "full_name": "MUGISHA Joseph",
    "phone_number": "+250788123456",
    "role": "CELL_LEADER",
    "district": 3,
    "national_id": "1199070123456789",
    "is_active": true,
    "is_verified": true,
    "last_login": "2026-05-02T08:30:00+02:00",
    "created_at": "2026-01-15T10:00:00+02:00"
  }
}
```

---

### `PATCH /api/v1/auth/me/`

Update own profile. Cannot change own role or district.

**Auth required:** ✅ Any role

**Request body** *(all fields optional):*
```json
{
  "full_name": "MUGISHA Joseph Emmanuel",
  "email": "joseph.new@girinka.rw",
  "phone_number": "+250722987654"
}
```

**Response `200`:** *(returns updated user profile)*

---

## 👥 Users — `/api/v1/users/`

> **All endpoints in this section require Admin role.**

---

### `GET /api/v1/users/`

List all user accounts in the system.

**Auth required:** ✅ Admin only

**Query parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `role` | string | Filter by role: `FARMER`, `CELL_LEADER`, `VETERINARIAN`, `DISTRICT_LEADER`, `ADMIN` |
| `district` | integer | Filter by district ID |
| `is_active` | boolean | `true` or `false` |
| `search` | string | Search by username or full name |
| `page` | integer | Page number |
| `page_size` | integer | Results per page (max 100) |

**Response `200`:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "username": "mugisha_joseph",
      "email": "joseph@girinka.rw",
      "full_name": "MUGISHA Joseph",
      "phone_number": "+250788123456",
      "role": "CELL_LEADER",
      "district": 3,
      "is_active": true,
      "is_verified": true,
      "created_at": "2026-01-15T10:00:00+02:00"
    }
  ],
  "meta": { "count": 1240, "next": "...", "previous": null }
}
```

---

### `POST /api/v1/users/`

Create a new user account.

**Auth required:** ✅ Admin only

**Request body:**
```json
{
  "username": "uwimana_claudine",
  "password": "SecurePass@2026",
  "full_name": "UWIMANA Claudine",
  "email": "claudine@girinka.rw",
  "phone_number": "+250788901234",
  "role": "CELL_LEADER",
  "district": 7,
  "national_id": "1199080123456789"
}
```

**Response `201`:**
```json
{
  "success": true,
  "data": {
    "id": 2,
    "username": "uwimana_claudine",
    "full_name": "UWIMANA Claudine",
    "role": "CELL_LEADER",
    "district": 7,
    "is_active": true,
    "created_at": "2026-05-02T10:00:00+02:00"
  }
}
```

---

### `GET /api/v1/users/{id}/`

Get full details of a specific user.

**Auth required:** ✅ Admin only

**Response `200`:** *(returns full user object)*

---

### `PATCH /api/v1/users/{id}/`

Update a user account (name, email, role, district).

**Auth required:** ✅ Admin only

**Request body** *(all fields optional):*
```json
{
  "full_name": "UWIMANA Claudine Marie",
  "role": "DISTRICT_LEADER",
  "district": 3,
  "is_active": true
}
```

**Response `200`:** *(returns updated user object)*

---

### `DELETE /api/v1/users/{id}/`

Soft-deactivate a user account. Sets `is_active=false`. Does not delete from database.

**Auth required:** ✅ Admin only

**Response `204`:** No content

---

### `GET /api/v1/users/{id}/activity/`

View the last 50 audit log entries for a user — all their CREATE, UPDATE, DELETE, and LOGIN actions.

**Auth required:** ✅ Admin only

**Response `200`:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "action": "CREATE",
      "resource_type": "Cow",
      "resource_id": 42,
      "old_values": null,
      "new_values": { "tag_number": "RW-GAS-001", "breed": "FRIESIAN_CROSS" },
      "ip_address": "197.243.12.45",
      "created_at": "2026-05-02T09:15:00+02:00"
    }
  ]
}
```

---

## 🗺️ Districts — `/api/v1/districts/`

---

### `GET /api/v1/districts/`

List all Rwanda districts with GPS coordinates.

**Auth required:** ✅ Any role

**Response `200`:**
```json
{
  "success": true,
  "data": [
    {
      "id": 3,
      "district_name": "Gasabo",
      "province": "Kigali",
      "sector": "Kimironko",
      "cell": "Bibare",
      "latitude": -1.9441,
      "longitude": 30.0619,
      "is_remote": false,
      "created_at": "2026-01-01T00:00:00+02:00"
    },
    {
      "id": 7,
      "district_name": "Bugesera",
      "province": "Eastern",
      "sector": "Rilima",
      "cell": "Kamabuye",
      "latitude": -2.1500,
      "longitude": 30.1167,
      "is_remote": false,
      "created_at": "2026-01-01T00:00:00+02:00"
    }
  ]
}
```

---

### `POST /api/v1/districts/`

Create a new district record.

**Auth required:** ✅ Admin only

**Request body:**
```json
{
  "district_name": "Nyarugenge",
  "province": "Kigali",
  "sector": "Nyamirambo",
  "cell": "Cyimana",
  "latitude": -1.9500,
  "longitude": 30.0588,
  "is_remote": false
}
```

**Response `201`:** *(returns created district object)*

---

### `GET /api/v1/districts/{id}/`

Get a single district's full details.

**Auth required:** ✅ Any role

**Response `200`:** *(returns district object)*

---

### `PATCH /api/v1/districts/{id}/`

Update district name, province, sector, cell, or GPS coordinates.

**Auth required:** ✅ Admin only

**Request body** *(all fields optional):*
```json
{
  "sector": "Remera",
  "latitude": -1.9600,
  "longitude": 30.1100
}
```

**Response `200`:** *(returns updated district object)*

---

### `DELETE /api/v1/districts/{id}/`

Delete a district. Only succeeds if no cows or beneficiaries are attached.

**Auth required:** ✅ Admin only

**Response `204`:** No content

---

### `GET /api/v1/districts/{id}/stats/`

Get live statistics for a district. Cached for 1 hour.

**Auth required:** ✅ Cell Leader and above

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "total_cows": 1240,
    "at_risk_cows": 87,
    "avg_milk": 11.3,
    "total_beneficiaries": 980
  }
}
```

---

### `GET /api/v1/districts/{id}/weather/`

Get the latest weather reading for a district.

**Auth required:** ✅ Any role

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "id": 145,
    "district": 3,
    "district_name": "Gasabo",
    "temperature": 21.4,
    "humidity": 72.0,
    "rainfall": 2.5,
    "wind_speed": 8.0,
    "reading_time": "2026-05-02T05:00:00+02:00",
    "data_source": "OpenMeteo",
    "forecast_day": 0
  }
}
```

---

## 🏠 Beneficiaries — `/api/v1/beneficiaries/`

---

### `GET /api/v1/beneficiaries/`

List farmers enrolled in the Girinka program.

- **Farmer** → own profile only
- **Cell Leader / Vet** → all in their district
- **Admin** → all nationally

**Auth required:** ✅ Any role

**Query parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `is_active` | boolean | Filter by active/inactive status |
| `district` | integer | Filter by district ID |
| `ubudehe_category` | integer | Filter by category (1 or 2) |
| `ml_risk_profile` | string | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `search` | string | Search by name or national ID |
| `page` | integer | Page number |

**Response `200`:**
```json
{
  "success": true,
  "data": [
    {
      "id": 12,
      "national_id": "1199080123456789",
      "full_name": "UWIMANA Claudine",
      "ubudehe_category": 1,
      "district": 7,
      "district_name": "Bugesera",
      "phone_number": "+250788901234",
      "gender": "FEMALE",
      "ml_risk_profile": "LOW",
      "is_active": true,
      "active_cows": 2,
      "registration_date": "2026-01-20",
      "created_at": "2026-01-20T09:00:00+02:00"
    }
  ],
  "meta": { "count": 980, "next": "...", "previous": null }
}
```

---

### `POST /api/v1/beneficiaries/`

Register a new farmer in the Girinka program. Ubudehe category must be **1 or 2**.

**Auth required:** ✅ Cell Leader, Admin

**Request body:**
```json
{
  "national_id": "1199080123456789",
  "full_name": "UWIMANA Claudine",
  "ubudehe_category": 1,
  "district": 7,
  "phone_number": "+250788901234",
  "date_of_birth": "1985-06-20",
  "gender": "FEMALE",
  "registration_date": "2026-05-02"
}
```

**Response `201`:** *(returns created beneficiary object)*

**Response `400` — Invalid Ubudehe:**
```json
{
  "success": false,
  "error_code": "INVALID_UBUDEHE",
  "message": "Only Ubudehe category 1 or 2 qualifies for Girinka."
}
```

**Response `409` — Duplicate national ID:**
```json
{
  "success": false,
  "error_code": "DUPLICATE_NATIONAL_ID",
  "message": "This national ID is already registered."
}
```

---

### `GET /api/v1/beneficiaries/{id}/`

Full beneficiary profile including district, Ubudehe category, active cow count, and ML risk profile.

**Auth required:** ✅ Any role

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "id": 12,
    "national_id": "1199080123456789",
    "full_name": "UWIMANA Claudine",
    "ubudehe_category": 1,
    "district": 7,
    "district_name": "Bugesera",
    "phone_number": "+250788901234",
    "date_of_birth": "1985-06-20",
    "gender": "FEMALE",
    "ml_risk_profile": "LOW",
    "is_active": true,
    "active_cows": 2,
    "registration_date": "2026-01-20",
    "deregistered_at": null,
    "deregister_reason": null,
    "created_at": "2026-01-20T09:00:00+02:00"
  }
}
```

---

### `PATCH /api/v1/beneficiaries/{id}/`

Update beneficiary details such as phone number, category, or district.

**Auth required:** ✅ Cell Leader, Admin

**Request body** *(all fields optional):*
```json
{
  "phone_number": "+250722456789",
  "ubudehe_category": 2
}
```

**Response `200`:** *(returns updated beneficiary object)*

---

### `POST /api/v1/beneficiaries/{id}/deregister/`

Remove a farmer from the Girinka program. Blocked if a pass-on transfer is pending.

**Auth required:** ✅ Cell Leader, Admin

**Request body:**
```json
{
  "reason": "RELOCATED",
  "notes": "Farmer moved to Kigali city permanently"
}
```

**Reason options:** `NO_LONGER_ELIGIBLE` · `COW_DIED` · `RULE_VIOLATION` · `RELOCATED` · `VOLUNTARY` · `DECEASED` · `LAND_LOSS`

**Response `200`:**
```json
{
  "success": true,
  "data": { "detail": "Beneficiary deregistered." }
}
```

**Response `422` — Pending pass-on:**
```json
{
  "success": false,
  "error_code": "PASSON_PENDING",
  "message": "Cannot deregister while a pass-on transfer is pending."
}
```

---

### `POST /api/v1/beneficiaries/{id}/reregister/`

Reactivate a previously deregistered farmer. Clears deregistration date and reason.

**Auth required:** ✅ Admin only

**Request body:** None

**Response `200`:** *(returns updated beneficiary object with `is_active: true`)*

---

### `GET /api/v1/beneficiaries/{id}/cows/`

List all living cows owned by this beneficiary.

**Auth required:** ✅ Any role

**Response `200`:** *(returns list of cow objects)*

---

### `GET /api/v1/beneficiaries/{id}/alerts/`

List all unresolved AI alerts for this beneficiary's cows.

**Auth required:** ✅ Any role

**Response `200`:** *(returns list of alert objects)*

---

### `GET /api/v1/beneficiaries/{id}/history/`

Full program history and timeline for this beneficiary.

**Auth required:** ✅ Cell Leader and above

**Response `200`:** *(returns beneficiary object with extended history fields)*

---

### `POST /api/v1/beneficiaries/bulk-import/`

Upload a CSV to bulk-register many farmers at once. Processed asynchronously via Celery.

**Auth required:** ✅ Admin only

**Content-Type:** `multipart/form-data`

**Required CSV columns:** `national_id`, `full_name`, `ubudehe_category`, `district`, `phone_number`

**Request:** Upload a file with key `file`

**Response `202`:**
```json
{
  "success": true,
  "data": { "detail": "Import queued. You will be notified when complete." }
}
```

---

## 🐮 Cows — `/api/v1/cows/`

---

### `GET /api/v1/cows/`

List cows filtered by role scope.

- **Farmer** → own cows only
- **Cell Leader / Vet** → all cows in their district
- **District Leader / Admin** → all cows nationally

**Auth required:** ✅ Any role

**Query parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `breed` | string | `FRIESIAN`, `JERSEY`, `ANKOLE`, `ANKOLE_CROSS`, `FRIESIAN_CROSS`, `JERSEY_CROSS`, `OTHER` |
| `health_status` | string | `HEALTHY`, `AT_RISK`, `HIGH_RISK`, `UNDER_TREATMENT`, `CRITICAL`, `EMERGENCY`, `DECEASED` |
| `is_alive` | boolean | `true` = living cows only |
| `district` | integer | Filter by district ID |
| `beneficiary` | integer | Filter by beneficiary ID |
| `risk_min` | float | Minimum mortality risk score (0.0–1.0) |
| `risk_max` | float | Maximum mortality risk score (0.0–1.0) |
| `search` | string | Search by tag number or farmer name |
| `ordering` | string | Sort field: `created_at`, `mortality_risk_score`, `health_status` |
| `page` | integer | Page number |
| `page_size` | integer | Results per page (max 100) |

**Response `200`:**
```json
{
  "success": true,
  "data": [
    {
      "id": 42,
      "tag_number": "RW-GAS-2026-001",
      "breed": "FRIESIAN_CROSS",
      "dob": "2022-03-15",
      "age_months": 50,
      "health_status": "HEALTHY",
      "mortality_risk_score": 0.12,
      "origin_type": "DIRECT_PROGRAM",
      "is_alive": true,
      "death_date": null,
      "lactation_number": 2,
      "days_in_milk": 95,
      "beneficiary": 12,
      "beneficiary_name": "UWIMANA Claudine",
      "district": 3,
      "district_name": "Gasabo",
      "created_at": "2026-01-20T09:00:00+02:00"
    }
  ],
  "meta": { "count": 1240, "next": "...", "previous": null }
}
```

---

### `POST /api/v1/cows/`

Register a new cow and assign it to a beneficiary. Tag number must be unique.

**Auth required:** ✅ Cell Leader, Admin

**Request body:**
```json
{
  "tag_number": "RW-GAS-2026-001",
  "breed": "FRIESIAN_CROSS",
  "dob": "2022-03-15",
  "beneficiary": 12,
  "district": 3,
  "origin_type": "DIRECT_PROGRAM"
}
```

**Origin type options:** `DIRECT_PROGRAM` · `BORN_ON_FARM` · `PASS_ON_RECEIVED`

**Response `201`:** *(returns created cow object)*

**Response `409` — Duplicate tag:**
```json
{
  "success": false,
  "error_code": "DUPLICATE_TAG_NUMBER",
  "message": "This cow tag number already exists in the system."
}
```

---

### `GET /api/v1/cows/{id}/`

Full cow profile including breed, health status, mortality risk score, lactation info, and owner.

**Auth required:** ✅ Any role

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "id": 42,
    "tag_number": "RW-GAS-2026-001",
    "breed": "FRIESIAN_CROSS",
    "dob": "2022-03-15",
    "age_months": 50,
    "health_status": "HEALTHY",
    "mortality_risk_score": 0.12,
    "origin_type": "DIRECT_PROGRAM",
    "is_alive": true,
    "death_date": null,
    "death_cause": null,
    "lactation_number": 2,
    "days_in_milk": 95,
    "beneficiary": 12,
    "beneficiary_name": "UWIMANA Claudine",
    "district": 3,
    "district_name": "Gasabo",
    "created_at": "2026-01-20T09:00:00+02:00",
    "updated_at": "2026-05-01T06:30:00+02:00"
  }
}
```

---

### `PATCH /api/v1/cows/{id}/`

Update cow details. Cannot change tag number or beneficiary directly (use transfer).

**Auth required:** ✅ Cell Leader, Veterinarian, Admin

**Request body** *(all fields optional):*
```json
{
  "breed": "FRIESIAN",
  "lactation_number": 3,
  "days_in_milk": 45
}
```

**Response `200`:** *(returns updated cow object)*

**Response `422` — Cow is deceased:**
```json
{
  "success": false,
  "error_code": "COW_ALREADY_DECEASED",
  "message": "Cannot update a deceased cow."
}
```

---

### `POST /api/v1/cows/{id}/death/`

Record the death of a cow. Sets `is_alive=false`, records date and cause. **Irreversible.**

**Auth required:** ✅ Cell Leader, Veterinarian, Admin

**Request body:**
```json
{
  "cause": "Severe respiratory illness — ECF suspected"
}
```

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "id": 42,
    "tag_number": "RW-GAS-2026-001",
    "is_alive": false,
    "health_status": "DECEASED",
    "death_date": "2026-05-02",
    "death_cause": "Severe respiratory illness — ECF suspected"
  }
}
```

**Response `422` — Already dead:**
```json
{
  "success": false,
  "error_code": "COW_ALREADY_DECEASED",
  "message": "Cannot update a deceased cow."
}
```

---

### `POST /api/v1/cows/{id}/upload_photo/`

Upload a cow photo. Stored on Cloudinary under `girinka/cows/`, auto-resized to 800×600.

**Auth required:** ✅ Cell Leader, Admin

**Content-Type:** `multipart/form-data`

**Request:** Upload an image with key `photo`

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "photo_url": "https://res.cloudinary.com/dhforyx1s/image/upload/v1746000000/girinka/cows/cow_RW-GAS-2026-001.jpg"
  }
}
```

---

### `GET /api/v1/cows/{id}/health/`

Get the last 20 veterinary health records for this cow, newest first.

**Auth required:** ✅ Any role

**Response `200`:** *(returns list of health record objects)*

---

### `GET /api/v1/cows/{id}/milk/`

Get the last 30 daily milk production records for this cow.

**Auth required:** ✅ Any role

**Response `200`:** *(returns list of milk production objects)*

---

### `GET /api/v1/cows/{id}/alerts/`

Get all unresolved AI alerts for this cow.

**Auth required:** ✅ Any role

**Response `200`:** *(returns list of alert objects)*

---

### `GET /api/v1/cows/{id}/lineage/`

Get the cow's lineage record — mother, generation number, birth weight, birth health.

**Auth required:** ✅ Any role

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "id": 18,
    "cow": 42,
    "mother": 15,
    "mother_tag": "RW-GAS-2020-015",
    "father_id": null,
    "birth_date": "2022-03-15",
    "birth_weight": 32.5,
    "birth_health": "GOOD",
    "generation_number": 2,
    "genetic_notes": "Strong milk genes from Friesian line"
  }
}
```

**Response `404`:** Lineage record not found

---

### `GET /api/v1/cows/{id}/predictions/`

Get the last 20 AI prediction logs for this cow (mortality, milk, disease, birth).

**Auth required:** ✅ Cell Leader and above

**Response `200`:**
```json
{
  "success": true,
  "data": [
    {
      "id": 301,
      "prediction_type": "MORTALITY_RISK",
      "input_features": { "disease_cases": 3, "vet_coverage_rate": 0.45 },
      "output_values": { "mortality_risk_score": 0.72, "risk_level": "HIGH" },
      "confidence_score": 0.72,
      "predicted_at": "2026-05-02T06:30:00+02:00"
    }
  ]
}
```

---

### `POST /api/v1/cows/{id}/predict_risk/`

Trigger a live CatBoost mortality risk prediction. Updates the cow's `mortality_risk_score` and `health_status`. Creates an alert if risk ≥ 0.50. Sends email if risk ≥ 0.60.

**Auth required:** ✅ Cell Leader and above

**Request body:** None

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "cow_id": 42,
    "mortality_risk_score": 0.7155,
    "risk_level": "HIGH",
    "alert_triggered": true,
    "alert_severity": "URGENT",
    "sms_required": false,
    "sms_recipients": [],
    "recommended_action": "🔶 Urgent vet consultation within 24 hours. Monitor closely.",
    "model_version": "v1.0.0"
  }
}
```

---

### `POST /api/v1/cows/{id}/predict_milk/`

Trigger a live LSTM 7-day milk forecast. Requires at least 7 days of milk records.

**Auth required:** ✅ Any role

**Request body:** None

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "cow_id": 42,
    "forecast_days": 7,
    "forecasts": [
      { "day": 1, "predicted_yield_litres": 12.3, "confidence": "high" },
      { "day": 2, "predicted_yield_litres": 12.1, "confidence": "high" },
      { "day": 3, "predicted_yield_litres": 11.9, "confidence": "high" },
      { "day": 4, "predicted_yield_litres": 11.8, "confidence": "high" },
      { "day": 5, "predicted_yield_litres": 11.7, "confidence": "high" },
      { "day": 6, "predicted_yield_litres": 11.6, "confidence": "high" },
      { "day": 7, "predicted_yield_litres": 11.4, "confidence": "high" }
    ],
    "avg_predicted_yield_litres": 11.97,
    "total_predicted_litres": 83.8,
    "data_quality": "sufficient",
    "note": "Forecast based on ≥15 days of data — high confidence.",
    "model_version": "v1.0.0"
  }
}
```

**Response `422`:**
```json
{
  "success": false,
  "error_code": "INSUFFICIENT_MILK_DATA",
  "message": "LSTM requires at least 7 days of milk records."
}
```

---

### `GET /api/v1/cows/at_risk/`

List all living cows with status AT_RISK, HIGH_RISK, CRITICAL, or EMERGENCY. Sorted by risk score descending.

**Auth required:** ✅ Cell Leader, Veterinarian, Admin

**Response `200`:** *(returns paginated list of at-risk cow objects, sorted by `mortality_risk_score` descending)*

---

## 🩺 Health Records — `/api/v1/health/`

---

### `GET /api/v1/health/`

List health records filtered by district for Cell Leaders and Vets.

**Auth required:** ✅ Cell Leader and above

**Query parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `cow` | integer | Filter by cow ID |
| `vet` | integer | Filter by vet ID |
| `date_after` | date | Records from this date (`YYYY-MM-DD`) |
| `date_before` | date | Records up to this date |
| `page` | integer | Page number |

**Response `200`:**
```json
{
  "success": true,
  "data": [
    {
      "id": 88,
      "cow": 42,
      "cow_tag": "RW-GAS-2026-001",
      "vet": 5,
      "vet_name": "Dr. HABIMANA Eric",
      "diagnosis": "Mild respiratory infection",
      "treatment_given": "Oxytetracycline 20mg/kg IM injection",
      "symptoms": "Nasal discharge, mild fever, reduced appetite",
      "temperature": 39.8,
      "weight": 380.5,
      "mortality_risk_score": 0.45,
      "next_visit_date": "2026-05-16",
      "date_recorded": "2026-05-02T10:30:00+02:00",
      "created_at": "2026-05-02T10:45:00+02:00"
    }
  ]
}
```

---

### `POST /api/v1/health/`

Create a new veterinary health record for a cow.

**Auth required:** ✅ Veterinarian, Admin

**Request body:**
```json
{
  "cow": 42,
  "vet": 5,
  "diagnosis": "Mild respiratory infection",
  "treatment_given": "Oxytetracycline 20mg/kg IM injection",
  "symptoms": "Nasal discharge, mild fever, reduced appetite",
  "temperature": 39.8,
  "weight": 380.5,
  "next_visit_date": "2026-05-16",
  "date_recorded": "2026-05-02T10:30:00+02:00"
}
```

**Response `201`:** *(returns created health record object)*

---

### `GET /api/v1/health/{id}/`

Get full details of a single health record.

**Auth required:** ✅ Any role

**Response `200`:** *(returns full health record object)*

---

### `PATCH /api/v1/health/{id}/`

Update a health record — add treatment notes or update next visit date.

**Auth required:** ✅ Veterinarian, Admin

**Request body** *(all fields optional):*
```json
{
  "treatment_given": "Oxytetracycline 20mg/kg IM. Follow-up with vitamins.",
  "next_visit_date": "2026-05-20"
}
```

**Response `200`:** *(returns updated health record)*

---

### `GET /api/v1/health/schedule/`

List all upcoming scheduled vet visits ordered by date.

**Auth required:** ✅ Veterinarian, Cell Leader and above

**Response `200`:**
```json
{
  "success": true,
  "data": [
    {
      "id": 88,
      "cow": 42,
      "cow_tag": "RW-GAS-2026-001",
      "vet_name": "Dr. HABIMANA Eric",
      "next_visit_date": "2026-05-16",
      "diagnosis": "Mild respiratory infection"
    }
  ]
}
```

---

### `POST /api/v1/health/schedule/`

Schedule a new vet visit for a cow.

**Auth required:** ✅ Veterinarian, Admin

**Request body:**
```json
{
  "cow": 42,
  "vet": 5,
  "next_visit_date": "2026-05-16",
  "diagnosis": "Routine follow-up after respiratory treatment",
  "date_recorded": "2026-05-02T10:30:00+02:00"
}
```

**Response `201`:** *(returns created health record)*

---

## 🥛 Milk Production — `/api/v1/milk/`

---

### `GET /api/v1/milk/`

List daily milk production records filtered by role scope.

**Auth required:** ✅ Any role

**Query parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `cow` | integer | Filter by cow ID |
| `date_after` | date | Records from this date |
| `date_before` | date | Records up to this date |
| `page` | integer | Page number |

**Response `200`:**
```json
{
  "success": true,
  "data": [
    {
      "id": 204,
      "cow": 42,
      "cow_tag": "RW-GAS-2026-001",
      "collection_date": "2026-05-02",
      "morning_yield": 6.8,
      "evening_yield": 5.7,
      "daily_yield": 12.5,
      "feed_amount": 6.0,
      "water_intake": 35.0,
      "lstm_forecast": 11.97,
      "notes": "Cow looked healthy and calm during milking.",
      "created_at": "2026-05-02T18:00:00+02:00"
    }
  ]
}
```

---

### `POST /api/v1/milk/`

Log a daily milk entry. `daily_yield` must equal `morning_yield + evening_yield` (within 0.5L tolerance).

**Auth required:** ✅ Farmer, Cell Leader

**Request body:**
```json
{
  "cow": 42,
  "collection_date": "2026-05-02",
  "morning_yield": 6.8,
  "evening_yield": 5.7,
  "daily_yield": 12.5,
  "feed_amount": 6.0,
  "water_intake": 35.0,
  "notes": "Cow looked healthy and calm during milking."
}
```

**Response `201`:** *(returns created milk production record)*

**Response `400` — Yield mismatch:**
```json
{
  "success": false,
  "message": "daily_yield must equal morning_yield + evening_yield.",
  "errors": { "non_field_errors": ["daily_yield must equal morning_yield + evening_yield."] }
}
```

---

### `GET /api/v1/milk/{id}/`

Get details of a single milk record.

**Auth required:** ✅ Any role

**Response `200`:** *(returns full milk record object)*

---

### `PATCH /api/v1/milk/{id}/`

Correct a mistakenly entered yield value.

**Auth required:** ✅ Farmer, Cell Leader

**Request body** *(all fields optional):*
```json
{
  "daily_yield": 13.0,
  "morning_yield": 7.2,
  "evening_yield": 5.8,
  "notes": "Corrected — initial entry had wrong morning yield"
}
```

**Response `200`:** *(returns updated milk record)*

---

### `DELETE /api/v1/milk/{id}/`

Delete a milk record.

**Auth required:** ✅ Admin only

**Response `204`:** No content

---

### `GET /api/v1/milk/forecast/?cow_id={id}`

Trigger the LSTM 7-day milk forecast for a cow. Requires `cow_id` query parameter and at least 7 days of records.

**Auth required:** ✅ Any role

**Query parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `cow_id` | integer | ✅ Yes | The cow ID to forecast |

**Response `200`:** *(returns 7-day LSTM forecast — same format as `cows/{id}/predict_milk/`)*

**Response `422`:**
```json
{
  "success": false,
  "error_code": "INSUFFICIENT_MILK_DATA",
  "message": "LSTM requires at least 7 days of milk records."
}
```

---

### `GET /api/v1/milk/summary/`

Returns aggregate production stats for the current user's scope.

**Auth required:** ✅ Any role

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "total_records": 4820,
    "avg_daily_yield": 10.74,
    "total_yield": 51765.8
  }
}
```

---

## 🚨 Alerts — `/api/v1/alerts/`

---

### `GET /api/v1/alerts/`

List alerts scoped by role. Filter by severity and resolved status.

- **Farmer** → alerts for own cows
- **Cell Leader / Vet** → all alerts in their district
- **Admin** → all nationally

**Auth required:** ✅ Any role

**Query parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `is_resolved` | boolean | `false` = active alerts only |
| `severity` | string | `INFO`, `WARNING`, `URGENT`, `CRITICAL` |
| `alert_type` | string | `MORTALITY_RISK`, `LOW_MILK`, `DISEASE_OUTBREAK`, `WEATHER_RISK`, `VET_VISIT_DUE`, `PASS_ON_DUE` |
| `cow` | integer | Filter by cow ID |
| `page` | integer | Page number |

**Response `200`:**
```json
{
  "success": true,
  "data": [
    {
      "id": 87,
      "cow": 42,
      "cow_tag": "RW-GAS-2026-001",
      "beneficiary": 12,
      "beneficiary_name": "UWIMANA Claudine",
      "alert_type": "MORTALITY_RISK",
      "severity": "URGENT",
      "risk_score": 0.72,
      "message": "Mortality risk score: 0.72 — HIGH",
      "recommendation": "🔶 Urgent vet consultation within 24 hours. Monitor closely.",
      "sent_via_sms": false,
      "sms_sent_at": null,
      "is_resolved": false,
      "resolved_at": null,
      "resolved_by": null,
      "resolution_notes": null,
      "alert_timestamp": "2026-05-02T06:30:00+02:00"
    }
  ],
  "meta": { "count": 14, "next": null, "previous": null }
}
```

---

### `POST /api/v1/alerts/`

Manually create an alert for a cow.

**Auth required:** ✅ Veterinarian, Admin

**Request body:**
```json
{
  "cow": 42,
  "beneficiary": 12,
  "alert_type": "VET_VISIT_DUE",
  "severity": "WARNING",
  "message": "Scheduled vet visit is overdue by 2 weeks.",
  "recommendation": "Contact veterinarian Dr. HABIMANA to schedule a visit."
}
```

**Response `201`:** *(returns created alert object)*

---

### `GET /api/v1/alerts/{id}/`

Full alert details including risk score, recommendation, email status, and resolution history.

**Auth required:** ✅ Any role

**Response `200`:** *(returns full alert object)*

---

### `POST /api/v1/alerts/{id}/resolve/`

Mark an alert as resolved. Records resolver, timestamp, and optional notes.

**Auth required:** ✅ Cell Leader, Veterinarian, Admin

**Request body:**
```json
{
  "notes": "Vet visited on 03/05. Cow given antibiotics. Risk reduced to 0.21."
}
```

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "id": 87,
    "is_resolved": true,
    "resolved_at": "2026-05-03T09:15:00+02:00",
    "resolved_by": 1,
    "resolution_notes": "Vet visited on 03/05. Cow given antibiotics. Risk reduced to 0.21."
  }
}
```

---

### `POST /api/v1/alerts/{id}/escalate/`

Escalate alert severity one level: `INFO` → `WARNING` → `URGENT` → `CRITICAL`.

**Auth required:** ✅ Cell Leader and above

**Request body:** None

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "id": 87,
    "severity": "CRITICAL",
    "alert_type": "MORTALITY_RISK"
  }
}
```

---

### `GET /api/v1/alerts/unread_count/`

Count of unresolved alerts in the current user's scope. Useful for notification badges in the frontend.

**Auth required:** ✅ Any role

**Response `200`:**
```json
{
  "success": true,
  "data": { "unread_count": 14 }
}
```

---

### `POST /api/v1/alerts/bulk_resolve/`

Resolve multiple alerts at once by providing a list of IDs.

**Auth required:** ✅ Cell Leader and above

**Request body:**
```json
{
  "alert_ids": [1, 3, 7, 12, 18]
}
```

**Response `200`:**
```json
{
  "success": true,
  "data": { "resolved": 5 }
}
```

---

## 🤖 Predictions — `/api/v1/predictions/`

---

### `POST /api/v1/predictions/mortality/`

Run CatBoost mortality risk prediction for a specific cow. Calls the ML FastAPI service.

**Side effects:** Updates cow's `mortality_risk_score` and `health_status`. Creates alert if risk ≥ 0.50. Sends email if risk ≥ 0.60.

**Auth required:** ✅ Cell Leader and above

**Request body:**
```json
{
  "cow_id": 42
}
```

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "cow_id": 42,
    "mortality_risk_score": 0.7155,
    "risk_level": "HIGH",
    "alert_triggered": true,
    "alert_severity": "URGENT",
    "sms_required": false,
    "sms_recipients": [],
    "recommended_action": "🔶 Urgent vet consultation within 24 hours. Monitor closely.",
    "model_version": "v1.0.0"
  }
}
```

**Risk levels:**

| Score | Level | Action |
|-------|-------|--------|
| 0.90–1.00 | `EMERGENCY` | Immediate vet + email to farmer |
| 0.80–0.89 | `VERY_HIGH` | Critical alert + email |
| 0.60–0.79 | `HIGH` | Urgent vet within 24 hours |
| 0.50–0.59 | `MEDIUM` | Schedule vet within 48 hours |
| 0.30–0.49 | `MEDIUM_LOW` | Monitor weekly |
| 0.00–0.29 | `LOW` | Routine monitoring |

---

### `POST /api/v1/predictions/milk/`

Run LSTM 7-day milk yield forecast for a specific cow. Requires at least 7 days of records.

**Auth required:** ✅ Any role

**Request body:**
```json
{
  "cow_id": 42
}
```

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "cow_id": 42,
    "forecast_days": 7,
    "forecasts": [
      { "day": 1, "predicted_yield_litres": 12.3, "confidence": "high" },
      { "day": 2, "predicted_yield_litres": 12.1, "confidence": "high" },
      { "day": 3, "predicted_yield_litres": 11.9, "confidence": "high" },
      { "day": 4, "predicted_yield_litres": 11.8, "confidence": "high" },
      { "day": 5, "predicted_yield_litres": 11.7, "confidence": "high" },
      { "day": 6, "predicted_yield_litres": 11.6, "confidence": "high" },
      { "day": 7, "predicted_yield_litres": 11.4, "confidence": "high" }
    ],
    "avg_predicted_yield_litres": 11.97,
    "total_predicted_litres": 83.8,
    "data_quality": "sufficient",
    "note": "Forecast based on ≥15 days of data — high confidence.",
    "model_version": "v1.0.0"
  }
}
```

---

### `POST /api/v1/predictions/disease/`

Run Random Forest disease risk detection. Returns probability for 7 disease classes.

**Auth required:** ✅ Veterinarian and above

**Request body:**
```json
{
  "cow_id": 12,
  "breed": "Ankole_Cross",
  "age_months": 48,
  "body_temperature_c": 40.5,
  "weight_kg": 310.0,
  "feeding_type": "Adequate",
  "water_access": true,
  "disease_cases_last_90d": 1,
  "outbreak_flag_last_30d": false,
  "nearest_outbreak_km": 50.0,
  "avg_temperature_c": 22.0,
  "avg_rainfall_mm": 850.0,
  "humidity_pct": 72.0,
  "fever": true,
  "lameness": true,
  "nasal_discharge": true,
  "skin_lesions": false,
  "reduced_appetite": true,
  "weight_loss": false,
  "swollen_lymph_nodes": false,
  "diarrhea": false,
  "labored_breathing": false,
  "mastitis_signs": false
}
```

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "cow_id": 12,
    "top_prediction": "FMD",
    "top_probability": 0.9708,
    "all_disease_probabilities": {
      "FMD": 0.9708,
      "ECF": 0.012,
      "Mastitis": 0.008,
      "Respiratory": 0.005,
      "Nutritional_Deficiency": 0.003,
      "Brucellosis": 0.001,
      "LSD": 0.001
    },
    "triggered_alerts": [
      {
        "disease": "FMD",
        "probability": 0.9708,
        "threshold_used": 0.60,
        "alert_triggered": true,
        "recommended_action": "Isolate cow immediately. Notify RAB and district vet. No contact with other animals."
      }
    ],
    "emergency": true,
    "total_symptoms_observed": 4,
    "model_version": "v1.0.0"
  }
}
```

**Disease alert thresholds:**

| Disease | Threshold | Emergency? |
|---------|-----------|-----------|
| FMD | 0.60 | ✅ Yes |
| ECF | 0.55 | ❌ |
| Mastitis | 0.50 | ❌ |
| Respiratory | 0.55 | ❌ |
| Nutritional Deficiency | 0.65 | ❌ |
| Brucellosis | 0.70 | ✅ Yes |
| LSD | 0.60 | ❌ |

---

### `POST /api/v1/predictions/passon/`

Run Logistic Regression birth success probability for a pregnant cow. Score ≥ 0.86 auto-flags the calf as Pass-On eligible.

**Auth required:** ✅ Cell Leader and above

**Request body:**
```json
{
  "cow_id": 5,
  "breed": "Friesian",
  "cow_age_months": 48,
  "lactation_number": 3,
  "initial_health_status": "Good",
  "feeding_type": "Good",
  "water_access": true,
  "disease_cases_last_180d": 0,
  "vet_access": true,
  "avg_temperature_last_trim": 20.5,
  "days_until_expected_birth": 14
}
```

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "cow_id": 5,
    "birth_success_probability": 0.923,
    "prognosis_label": "Excellent",
    "pass_on_eligible": true,
    "recommended_action": "✅ Auto-flag calf for Pass-On program after birth.",
    "model_version": "v1.0.0"
  }
}
```

**Prognosis levels:**

| Score | Label | Action |
|-------|-------|--------|
| 0.86–1.00 | `Excellent` | Auto-flag calf for Pass-On |
| 0.66–0.85 | `Good` | Routine check 1 week before birth |
| 0.41–0.65 | `Moderate` | Vet visit within 2 weeks |
| 0.00–0.40 | `High Risk` | Urgent pre-birth vet exam |

---

### `GET /api/v1/predictions/history/`

List all prediction logs. Filter by cow to see a specific cow's AI history.

**Auth required:** ✅ Cell Leader and above

**Query parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `cow_id` | integer | Filter by cow ID |
| `prediction_type` | string | `MORTALITY_RISK`, `MILK_FORECAST`, `DISEASE_RISK`, `BIRTH_PROBABILITY` |
| `page` | integer | Page number |

**Response `200`:** *(returns paginated list of prediction log objects)*

---

### `GET /api/v1/predictions/history/{id}/`

Get full detail of a single prediction log including input features and output values.

**Auth required:** ✅ Cell Leader and above

**Response `200`:** *(returns full prediction log object)*

---

### `GET /api/v1/predictions/models/`

List all AI model versions registered in the system.

**Auth required:** ✅ Admin only

**Response `200`:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "model_type": "CATBOOST",
      "version": "v1.0.0",
      "accuracy_metric": 0.9812,
      "r2_score": 0.9282,
      "mae": 0.0372,
      "rmse": 0.0479,
      "is_deployed": true,
      "training_samples": 4000,
      "last_training_date": "2026-04-30T02:00:00+02:00"
    },
    {
      "id": 2,
      "model_type": "LSTM",
      "version": "v1.0.0",
      "mae": 0.0776,
      "rmse": 0.0940,
      "is_deployed": true,
      "training_samples": 13440
    }
  ]
}
```

---

### `GET /api/v1/predictions/models/{id}/`

Get full details of a specific AI model version.

**Auth required:** ✅ Admin only

**Response `200`:** *(returns full AI model object)*

---

### `POST /api/v1/predictions/models/{id}/deploy/`

Deploy this model version. Automatically deactivates the current deployed model of the same type.

**Auth required:** ✅ Admin only

**Request body:** None

**Response `200`:**
```json
{
  "success": true,
  "data": { "detail": "CATBOOST v1.1.0 deployed." }
}
```

---

### `GET /api/v1/predictions/models/performance/`

View accuracy metrics for all currently deployed models.

**Auth required:** ✅ Admin only

**Response `200`:** *(returns list of deployed AI model objects with metrics)*

---

### `POST /api/v1/predictions/models/retrain/`

Queue a full ML model retrain pipeline on the ML service. Runs asynchronously via Celery.

**Auth required:** ✅ Admin only

**Request body:** None

**Response `202`:**
```json
{
  "success": true,
  "data": { "detail": "Retrain pipeline queued." }
}
```

---

### `GET /api/v1/predictions/models/health_check/`

Check if the Girinka ML FastAPI service is reachable and all 4 models are loaded.

**Auth required:** ✅ Admin only

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "status": "ok",
    "models": {
      "catboost": true,
      "lstm": true,
      "random_forest": true,
      "logistic": true
    }
  }
}
```

**Response `503` — ML service down:**
```json
{
  "success": false,
  "data": { "status": "down", "error": "Connection refused" }
}
```

---

## 🔄 Pass-On Registry — `/api/v1/passon/`

---

### `GET /api/v1/passon/`

List all calf pass-on transfers. Cell Leaders see their district only.

**Auth required:** ✅ Cell Leader and above

**Query parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | `PENDING`, `APPROVED`, `COMPLETED`, `REJECTED`, `CANCELLED` |
| `district` | integer | Filter by district ID |
| `page` | integer | Page number |

**Response `200`:**
```json
{
  "success": true,
  "data": [
    {
      "id": 14,
      "calf": 58,
      "calf_tag": "RW-BUG-2025-058",
      "donor_farmer": 12,
      "donor_name": "UWIMANA Claudine",
      "recipient_farmer": 31,
      "recipient_name": "NKURUNZIZA Pierre",
      "district": 7,
      "eligibility_score": 0.87,
      "transfer_date": "2026-05-15",
      "cell_leader_approval": false,
      "status": "PENDING",
      "notes": null,
      "certificate_url": null,
      "created_at": "2026-05-02T11:00:00+02:00"
    }
  ]
}
```

---

### `POST /api/v1/passon/`

Initiate a new calf pass-on transfer.

**Auth required:** ✅ Cell Leader, Admin

**Request body:**
```json
{
  "calf": 58,
  "donor_farmer": 12,
  "recipient_farmer": 31,
  "district": 7,
  "transfer_date": "2026-05-15",
  "notes": "Calf is healthy. Recipient household has been verified and approved."
}
```

**Response `201`:** *(returns created transfer object with `status: PENDING`)*

---

### `GET /api/v1/passon/{id}/`

Full transfer details including donor, recipient, calf, eligibility score, approval status, and certificate URL.

**Auth required:** ✅ Any role

**Response `200`:** *(returns full pass-on registry object)*

---

### `PATCH /api/v1/passon/{id}/`

Update transfer details such as notes or transfer date.

**Auth required:** ✅ Cell Leader, Admin

**Request body:**
```json
{
  "transfer_date": "2026-05-20",
  "notes": "Transfer date moved — recipient unavailable on original date."
}
```

**Response `200`:** *(returns updated transfer object)*

---

### `POST /api/v1/passon/{id}/approve/`

Cell Leader approves the transfer. Sets `cell_leader_approval=true` and status to `APPROVED`.

**Auth required:** ✅ Cell Leader, Admin

**Request body:** None

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "id": 14,
    "status": "APPROVED",
    "cell_leader_approval": true,
    "approved_by": 1,
    "approval_date": "2026-05-03T10:00:00+02:00"
  }
}
```

---

### `POST /api/v1/passon/{id}/complete/`

Mark the transfer as complete. Changes calf ownership in the database. Triggers certificate generation on Cloudinary and emails both parties via Resend.

**Auth required:** ✅ Cell Leader, Admin

**Request body:** None

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "id": 14,
    "status": "COMPLETED",
    "calf_tag": "RW-BUG-2025-058"
  }
}
```

---

### `POST /api/v1/passon/{id}/reject/`

Reject a transfer with a reason. Sets status to `REJECTED`.

**Auth required:** ✅ Cell Leader, Admin

**Request body:**
```json
{
  "notes": "Recipient household failed land verification check."
}
```

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "id": 14,
    "status": "REJECTED",
    "notes": "Recipient household failed land verification check."
  }
}
```

---

### `GET /api/v1/passon/{id}/certificate/`

Get the Cloudinary URL of the transfer certificate. Available only after transfer is COMPLETED.

**Auth required:** ✅ Any role

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "certificate_url": "https://res.cloudinary.com/dhforyx1s/raw/upload/girinka/certificates/certificate_14.html"
  }
}
```

**Response `404` — Certificate not yet generated:**
```json
{
  "success": false,
  "message": "Certificate not yet generated."
}
```

---

## 🧬 Lineage — `/api/v1/lineage/`

---

### `GET /api/v1/lineage/`

List all cow lineage records.

**Auth required:** ✅ Any role

**Query parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `cow_id` | integer | Get lineage for a specific cow |
| `page` | integer | Page number |

**Response `200`:**
```json
{
  "success": true,
  "data": [
    {
      "id": 18,
      "cow": 42,
      "mother": 15,
      "mother_tag": "RW-GAS-2020-015",
      "father_id": null,
      "birth_date": "2022-03-15",
      "birth_weight": 32.5,
      "birth_health": "GOOD",
      "generation_number": 2,
      "genetic_notes": "Strong milk genes from Friesian line",
      "created_at": "2022-03-16T08:00:00+02:00"
    }
  ]
}
```

---

### `GET /api/v1/lineage/{id}/`

Get a specific lineage record.

**Auth required:** ✅ Any role

**Response `200`:** *(returns full lineage record object)*

---

### `GET /api/v1/lineage/?cow_id={id}`

Get lineage for a specific cow using the `cow_id` filter.

**Auth required:** ✅ Any role

**Response `200`:** *(returns list with the matching lineage record)*

---

## 📊 Reports — `/api/v1/reports/`

---

### `GET /api/v1/reports/`

List generated reports. Cell Leaders see their district only.

**Auth required:** ✅ Cell Leader and above

**Query parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | `PENDING`, `GENERATING`, `READY`, `FAILED` |
| `report_type` | string | `FARMER_SUMMARY`, `DISTRICT_WEEKLY`, `NATIONAL_MONTHLY`, etc. |
| `page` | integer | Page number |

**Response `200`:**
```json
{
  "success": true,
  "data": [
    {
      "id": 7,
      "report_type": "DISTRICT_WEEKLY",
      "report_period": "WEEKLY",
      "district": 3,
      "period_start": "2026-04-25",
      "period_end": "2026-05-02",
      "status": "READY",
      "file_url": "https://res.cloudinary.com/dhforyx1s/raw/upload/girinka/reports/report_7_DISTRICT_WEEKLY.html",
      "generated_at": "2026-05-02T08:15:00+02:00",
      "created_at": "2026-05-02T08:00:00+02:00"
    }
  ]
}
```

---

### `POST /api/v1/reports/generate/`

Queue a new report for generation. Uploaded to Cloudinary and emailed when ready.

**Auth required:** ✅ Cell Leader and above

**Request body:**
```json
{
  "report_type": "DISTRICT_WEEKLY",
  "report_period": "WEEKLY",
  "district": 3,
  "period_start": "2026-04-25",
  "period_end": "2026-05-02"
}
```

**Report type options:** `FARMER_SUMMARY` · `DISTRICT_WEEKLY` · `NATIONAL_MONTHLY` · `VET_PRIORITY` · `PASS_ON_AUDIT` · `AI_PERFORMANCE`

**Response `202`:**
```json
{
  "success": true,
  "data": {
    "id": 8,
    "status": "PENDING",
    "report_type": "DISTRICT_WEEKLY",
    "created_at": "2026-05-02T14:00:00+02:00"
  }
}
```

---

### `GET /api/v1/reports/{id}/`

Get report status, data snapshot, and metadata.

**Auth required:** ✅ Cell Leader and above

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "id": 7,
    "report_type": "DISTRICT_WEEKLY",
    "status": "READY",
    "data_snapshot": {
      "total_cows": 1240,
      "total_beneficiaries": 980,
      "at_risk_cows": 87,
      "critical_cows": 12,
      "deceased_cows": 3,
      "unresolved_alerts": 14
    },
    "file_url": "https://res.cloudinary.com/dhforyx1s/raw/upload/girinka/reports/report_7_DISTRICT_WEEKLY.html",
    "generated_at": "2026-05-02T08:15:00+02:00"
  }
}
```

---

### `GET /api/v1/reports/{id}/download/`

Get the Cloudinary signed URL to download the report file.

**Auth required:** ✅ Cell Leader and above

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "download_url": "https://res.cloudinary.com/dhforyx1s/raw/upload/girinka/reports/report_7_DISTRICT_WEEKLY.html"
  }
}
```

**Response `404` — Not ready:**
```json
{
  "success": false,
  "message": "Report not ready."
}
```

---

### `GET /api/v1/reports/national/`

Get live national statistics without generating a report.

**Auth required:** ✅ District Leader, Admin

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "total_cows": 398420,
    "total_beneficiaries": 496380,
    "at_risk_cows": 24310,
    "critical_cows": 3820,
    "deceased_cows": 1240,
    "unresolved_alerts": 8920
  }
}
```

---

## 🌤️ Weather — `/api/v1/weather/`

---

### `GET /api/v1/weather/`

List recent weather readings. Auto-fetched daily at 05:00 AM from Open-Meteo.

**Auth required:** ✅ Any role

**Query parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `district_id` | integer | Filter by district ID |
| `page` | integer | Page number |

**Response `200`:**
```json
{
  "success": true,
  "data": [
    {
      "id": 145,
      "district": 3,
      "district_name": "Gasabo",
      "temperature": 21.4,
      "humidity": 72.0,
      "rainfall": 2.5,
      "wind_speed": 8.0,
      "reading_time": "2026-05-02T05:00:00+02:00",
      "data_source": "OpenMeteo",
      "forecast_day": 0
    }
  ]
}
```

---

### `GET /api/v1/weather/{id}/`

Get a single weather reading.

**Auth required:** ✅ Any role

**Response `200`:** *(returns full weather data object)*

---

### `GET /api/v1/weather/forecast/`

Get the 7-day weather forecast for a district.

**Auth required:** ✅ Any role

**Query parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `district_id` | integer | Filter by district ID |

**Response `200`:**
```json
{
  "success": true,
  "data": [
    { "district": 3, "district_name": "Gasabo", "forecast_day": 1, "temperature": 22.1, "rainfall": 0.0, "humidity": 68.0, "reading_time": "2026-05-03T05:00:00+02:00" },
    { "district": 3, "district_name": "Gasabo", "forecast_day": 2, "temperature": 23.5, "rainfall": 5.2, "humidity": 78.0, "reading_time": "2026-05-04T05:00:00+02:00" },
    { "district": 3, "district_name": "Gasabo", "forecast_day": 3, "temperature": 20.8, "rainfall": 12.1, "humidity": 85.0, "reading_time": "2026-05-05T05:00:00+02:00" },
    { "district": 3, "district_name": "Gasabo", "forecast_day": 4, "temperature": 19.5, "rainfall": 8.4, "humidity": 82.0, "reading_time": "2026-05-06T05:00:00+02:00" },
    { "district": 3, "district_name": "Gasabo", "forecast_day": 5, "temperature": 21.0, "rainfall": 1.0, "humidity": 71.0, "reading_time": "2026-05-07T05:00:00+02:00" },
    { "district": 3, "district_name": "Gasabo", "forecast_day": 6, "temperature": 22.3, "rainfall": 0.0, "humidity": 66.0, "reading_time": "2026-05-08T05:00:00+02:00" },
    { "district": 3, "district_name": "Gasabo", "forecast_day": 7, "temperature": 23.1, "rainfall": 3.5, "humidity": 74.0, "reading_time": "2026-05-09T05:00:00+02:00" }
  ]
}
```

---

## 🔔 Notifications — `/api/v1/notifications/`

---

### `GET /api/v1/notifications/`

List all notifications for the current user, newest first.

**Auth required:** ✅ Any role

**Query parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `is_read` | boolean | `false` = unread only |
| `page` | integer | Page number |

**Response `200`:**
```json
{
  "success": true,
  "data": [
    {
      "id": 55,
      "user": 1,
      "alert": 87,
      "title": "🔶 Urgent Alert: Cow RW-GAS-2026-001",
      "message": "Mortality risk score 0.72 — Urgent vet consultation required within 24 hours.",
      "is_read": false,
      "read_at": null,
      "created_at": "2026-05-02T06:30:00+02:00"
    }
  ],
  "meta": { "count": 8, "next": null, "previous": null }
}
```

---

### `GET /api/v1/notifications/{id}/`

Get a single notification detail.

**Auth required:** ✅ Any role

**Response `200`:** *(returns full notification object)*

---

### `PATCH /api/v1/notifications/{id}/read/`

Mark a single notification as read. Sets `read_at` timestamp.

**Auth required:** ✅ Any role

**Request body:** None

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "id": 55,
    "is_read": true,
    "read_at": "2026-05-02T09:00:00+02:00"
  }
}
```

---

### `POST /api/v1/notifications/mark_all_read/`

Mark all unread notifications for the current user as read at once.

**Auth required:** ✅ Any role

**Request body:** None

**Response `200`:**
```json
{
  "success": true,
  "data": { "marked_read": 8 }
}
```

---

### `GET /api/v1/notifications/settings/`

Get the current user's notification preferences.

**Auth required:** ✅ Any role

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "user": 1,
    "sms": true,
    "email": true,
    "in_app": true,
    "push": false,
    "min_severity": "INFO",
    "updated_at": "2026-05-01T10:00:00+02:00"
  }
}
```

---

### `PATCH /api/v1/notifications/settings/`

Update notification preferences.

**Auth required:** ✅ Any role

**Request body** *(all fields optional):*
```json
{
  "email": true,
  "in_app": true,
  "push": false,
  "min_severity": "WARNING"
}
```

**Min severity options:** `INFO` · `WARNING` · `URGENT` · `CRITICAL`

**Response `200`:** *(returns updated preferences object)*

---

## Quick Reference Table

| Method | Endpoint | Description | Min Role |
|--------|----------|-------------|----------|
| `POST` | `/auth/login/` | Login, get tokens | Public |
| `POST` | `/auth/logout/` | Blacklist refresh token | Any |
| `POST` | `/auth/token/refresh/` | Get new access token | Public |
| `POST` | `/auth/password/reset/` | Request OTP via email | Public |
| `POST` | `/auth/password/confirm/` | Reset password with OTP | Public |
| `POST` | `/auth/password/change/` | Change own password | Any |
| `GET` | `/auth/me/` | Get own profile | Any |
| `PATCH` | `/auth/me/` | Update own profile | Any |
| `GET` | `/users/` | List all users | Admin |
| `POST` | `/users/` | Create user | Admin |
| `GET` | `/users/{id}/` | Get user | Admin |
| `PATCH` | `/users/{id}/` | Update user | Admin |
| `DELETE` | `/users/{id}/` | Deactivate user | Admin |
| `GET` | `/users/{id}/activity/` | User audit log | Admin |
| `GET` | `/districts/` | List districts | Any |
| `POST` | `/districts/` | Create district | Admin |
| `GET` | `/districts/{id}/` | Get district | Any |
| `PATCH` | `/districts/{id}/` | Update district | Admin |
| `DELETE` | `/districts/{id}/` | Delete district | Admin |
| `GET` | `/districts/{id}/stats/` | District live stats | Cell Leader+ |
| `GET` | `/districts/{id}/weather/` | District latest weather | Any |
| `GET` | `/beneficiaries/` | List beneficiaries | Any |
| `POST` | `/beneficiaries/` | Register farmer | Cell Leader+ |
| `GET` | `/beneficiaries/{id}/` | Get beneficiary | Any |
| `PATCH` | `/beneficiaries/{id}/` | Update beneficiary | Cell Leader+ |
| `POST` | `/beneficiaries/{id}/deregister/` | Deregister farmer | Cell Leader+ |
| `POST` | `/beneficiaries/{id}/reregister/` | Reactivate farmer | Admin |
| `GET` | `/beneficiaries/{id}/cows/` | Farmer's cows | Any |
| `GET` | `/beneficiaries/{id}/alerts/` | Farmer's alerts | Any |
| `GET` | `/beneficiaries/{id}/history/` | Program history | Cell Leader+ |
| `POST` | `/beneficiaries/bulk-import/` | CSV bulk import | Admin |
| `GET` | `/cows/` | List cows | Any |
| `POST` | `/cows/` | Register cow | Cell Leader+ |
| `GET` | `/cows/{id}/` | Get cow profile | Any |
| `PATCH` | `/cows/{id}/` | Update cow | Cell Leader+ |
| `POST` | `/cows/{id}/death/` | Record death | Cell Leader+ |
| `POST` | `/cows/{id}/upload_photo/` | Upload cow photo | Cell Leader+ |
| `GET` | `/cows/{id}/health/` | Cow health records | Any |
| `GET` | `/cows/{id}/milk/` | Cow milk history | Any |
| `GET` | `/cows/{id}/alerts/` | Cow alerts | Any |
| `GET` | `/cows/{id}/lineage/` | Cow lineage tree | Any |
| `GET` | `/cows/{id}/predictions/` | Cow AI history | Cell Leader+ |
| `POST` | `/cows/{id}/predict_risk/` | Run mortality prediction | Cell Leader+ |
| `POST` | `/cows/{id}/predict_milk/` | Run milk forecast | Any |
| `GET` | `/cows/at_risk/` | All at-risk cows | Cell Leader+ |
| `GET` | `/health/` | List health records | Cell Leader+ |
| `POST` | `/health/` | Create health record | Vet+ |
| `GET` | `/health/{id}/` | Get health record | Any |
| `PATCH` | `/health/{id}/` | Update health record | Vet+ |
| `GET` | `/health/schedule/` | Upcoming vet visits | Vet+ |
| `POST` | `/health/schedule/` | Schedule vet visit | Vet+ |
| `GET` | `/milk/` | List milk records | Any |
| `POST` | `/milk/` | Log daily milk | Farmer+ |
| `GET` | `/milk/{id}/` | Get milk record | Any |
| `PATCH` | `/milk/{id}/` | Update milk record | Farmer+ |
| `DELETE` | `/milk/{id}/` | Delete milk record | Admin |
| `GET` | `/milk/forecast/` | Run LSTM forecast | Any |
| `GET` | `/milk/summary/` | Production summary | Any |
| `GET` | `/alerts/` | List alerts | Any |
| `POST` | `/alerts/` | Create manual alert | Vet+ |
| `GET` | `/alerts/{id}/` | Get alert | Any |
| `POST` | `/alerts/{id}/resolve/` | Resolve alert | Cell Leader+ |
| `POST` | `/alerts/{id}/escalate/` | Escalate severity | Cell Leader+ |
| `GET` | `/alerts/unread_count/` | Count unread alerts | Any |
| `POST` | `/alerts/bulk_resolve/` | Bulk resolve alerts | Cell Leader+ |
| `POST` | `/predictions/mortality/` | CatBoost mortality risk | Cell Leader+ |
| `POST` | `/predictions/milk/` | LSTM milk forecast | Any |
| `POST` | `/predictions/disease/` | Random Forest disease | Vet+ |
| `POST` | `/predictions/passon/` | Birth probability | Cell Leader+ |
| `GET` | `/predictions/history/` | Prediction logs | Cell Leader+ |
| `GET` | `/predictions/history/{id}/` | Prediction log detail | Cell Leader+ |
| `GET` | `/predictions/models/` | List AI models | Admin |
| `GET` | `/predictions/models/{id}/` | Get AI model | Admin |
| `POST` | `/predictions/models/{id}/deploy/` | Deploy model version | Admin |
| `GET` | `/predictions/models/performance/` | Deployed model metrics | Admin |
| `POST` | `/predictions/models/retrain/` | Trigger retrain | Admin |
| `GET` | `/predictions/models/health_check/` | ML service status | Admin |
| `GET` | `/passon/` | List transfers | Cell Leader+ |
| `POST` | `/passon/` | Initiate transfer | Cell Leader+ |
| `GET` | `/passon/{id}/` | Get transfer | Any |
| `PATCH` | `/passon/{id}/` | Update transfer | Cell Leader+ |
| `POST` | `/passon/{id}/approve/` | Approve transfer | Cell Leader+ |
| `POST` | `/passon/{id}/complete/` | Complete transfer | Cell Leader+ |
| `POST` | `/passon/{id}/reject/` | Reject transfer | Cell Leader+ |
| `GET` | `/passon/{id}/certificate/` | Get certificate URL | Any |
| `GET` | `/lineage/` | List lineage records | Any |
| `GET` | `/lineage/{id}/` | Get lineage record | Any |
| `GET` | `/reports/` | List reports | Cell Leader+ |
| `POST` | `/reports/generate/` | Generate report | Cell Leader+ |
| `GET` | `/reports/{id}/` | Get report status | Cell Leader+ |
| `GET` | `/reports/{id}/download/` | Download report | Cell Leader+ |
| `GET` | `/reports/national/` | National live stats | District Leader+ |
| `GET` | `/weather/` | List weather data | Any |
| `GET` | `/weather/{id}/` | Get weather reading | Any |
| `GET` | `/weather/forecast/` | 7-day forecast | Any |
| `GET` | `/notifications/` | List notifications | Any |
| `GET` | `/notifications/{id}/` | Get notification | Any |
| `PATCH` | `/notifications/{id}/read/` | Mark as read | Any |
| `POST` | `/notifications/mark_all_read/` | Mark all read | Any |
| `GET` | `/notifications/settings/` | Get preferences | Any |
| `PATCH` | `/notifications/settings/` | Update preferences | Any |

---

*Girinka Pulse API · University of Rwanda · 2026*
*UMUTESI Kelia · MUGISHA Joseph · MUGISHA Philippe*
