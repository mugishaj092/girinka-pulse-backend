Read `progress-tracker.md`, `architecture-context.md`, `api-context.md`, and `code-standards.md` before starting.

# 05 — Beneficiaries

Verify and complete the Beneficiaries module. Beneficiaries are the farmers enrolled in the Girinka program. Every cow must belong to a beneficiary. This module has significant business logic — Ubudehe validation, deregistration blocking, and bulk import.

Requires: spec `03-user-management` complete (users with roles exist), spec `04-districts` complete (30 districts in DB).

---

## Endpoints

All under `/api/v1/beneficiaries/`.

---

### GET `/api/v1/beneficiaries/`

**Auth required:** Any authenticated user (data scoped by role)

**Data scoping by role:**
- `FARMER` → only their own beneficiary profile (the one linked to their User account)
- `CELL_LEADER` / `VETERINARIAN` → all beneficiaries in their assigned district
- `DISTRICT_LEADER` → all beneficiaries in their assigned district (read-only)
- `ADMIN` → all beneficiaries nationally

**Query parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `is_active` | boolean | Filter active/inactive |
| `district` | integer | District ID (Admin only — others scoped automatically) |
| `ubudehe_category` | integer | `1` or `2` |
| `ml_risk_profile` | string | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `search` | string | Match on `full_name` or `national_id` |
| `page` | integer | Page number |
| `page_size` | integer | Max 100 |

**Success `200`:**
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
      "deregistered_at": null,
      "deregister_reason": null,
      "created_at": "2026-01-20T09:00:00+02:00"
    }
  ],
  "meta": { "count": 980, "next": null, "previous": null }
}
```

`active_cows` is a computed field: count of `Cow` objects where `beneficiary=this`, `is_alive=True`.

---

### POST `/api/v1/beneficiaries/`

**Auth required:** Cell Leader, Admin

**Request:**
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

**Required fields:** `national_id`, `full_name`, `ubudehe_category`, `district`, `registration_date`

**Validation rules:**

1. `ubudehe_category` must be `1` or `2`. If `3` or `4`, raise `InvalidUbudehe`:
```json
{
  "success": false,
  "error_code": "INVALID_UBUDEHE",
  "message": "Only Ubudehe category 1 or 2 qualifies for Girinka."
}
```

2. `national_id` must be unique. If already registered, raise `DuplicateNationalIdError`:
```json
{
  "success": false,
  "error_code": "DUPLICATE_NATIONAL_ID",
  "message": "This national ID is already registered."
}
```

3. `national_id` must be exactly 16 digits:
```json
{
  "success": false,
  "errors": { "national_id": ["National ID must be exactly 16 digits."] }
}
```

**Success `201`:** Returns created beneficiary object.

---

### GET `/api/v1/beneficiaries/{id}/`

**Auth required:** Any authenticated user (subject to role-based data scoping)

**Success `200`:** Returns full beneficiary profile.

**Error `404`:** Beneficiary does not exist or is not in scope for this user's role.

---

### PATCH `/api/v1/beneficiaries/{id}/`

**Auth required:** Cell Leader, Admin

**Request** (all fields optional):
```json
{
  "phone_number": "+250722456789",
  "ubudehe_category": 2
}
```

**Immutable fields** (ignore if sent): `national_id`, `district`, `registration_date`

**Success `200`:** Returns updated beneficiary.

---

### POST `/api/v1/beneficiaries/{id}/deregister/`

**Auth required:** Cell Leader, Admin

**Request:**
```json
{
  "reason": "RELOCATED",
  "notes": "Farmer moved to Kigali city permanently."
}
```

**Required fields:** `reason`

**Valid reason values:** `NO_LONGER_ELIGIBLE`, `COW_DIED`, `RULE_VIOLATION`, `RELOCATED`, `VOLUNTARY`, `DECEASED`, `LAND_LOSS`

**Pre-condition check:** Before deregistering, check if any `PassOnRegistry` record exists where `donor_farmer=this` AND `status="PENDING"`. If yes, raise `PassonPendingError`:
```json
{
  "success": false,
  "error_code": "PASSON_PENDING",
  "message": "Cannot deregister while a pass-on transfer is pending."
}
```

**On success:**
- Set `is_active = False`
- Set `deregistered_at = now()`
- Set `deregister_reason = reason`
- Set `deregister_notes = notes`
- Set `deregistered_by = request.user`
- Save

**Success `200`:**
```json
{ "success": true, "data": { "detail": "Beneficiary deregistered." } }
```

**Error if already inactive:**
```json
{
  "success": false,
  "error_code": "BENEFICIARY_INACTIVE",
  "message": "This beneficiary is already deregistered."
}
```

---

### POST `/api/v1/beneficiaries/{id}/reregister/`

**Auth required:** Admin only

**Behavior:**
- Set `is_active = True`
- Clear `deregistered_at = None`
- Clear `deregister_reason = None`
- Clear `deregister_notes = None`
- Clear `deregistered_by = None`
- Save

**Success `200`:** Returns updated beneficiary with `is_active: true`.

---

### GET `/api/v1/beneficiaries/{id}/cows/`

**Auth required:** Any authenticated user

Returns all living cows for this beneficiary.

**Success `200`:**
```json
{
  "success": true,
  "data": [
    {
      "id": 42,
      "tag_number": "RW-GAS-2026-001",
      "breed": "FRIESIAN_CROSS",
      "health_status": "HEALTHY",
      "mortality_risk_score": 0.12,
      "is_alive": true
    }
  ]
}
```

---

### GET `/api/v1/beneficiaries/{id}/alerts/`

**Auth required:** Any authenticated user

Returns unresolved alerts linked to all cows owned by this beneficiary.

**Success `200`:** Returns list of alert objects, most recent first.

---

### GET `/api/v1/beneficiaries/{id}/history/`

**Auth required:** Cell Leader and above

Returns the full beneficiary record with extended history — all audit log entries, deregistration history if any, and program timeline.

**Success `200`:** Returns full beneficiary object plus `history` array of audit events.

---

### POST `/api/v1/beneficiaries/bulk-import/`

**Auth required:** Admin only

**Content-Type:** `multipart/form-data`

**Request:** Upload a CSV file with key `file`.

**Required CSV columns:**
- `national_id` — 16-digit national ID
- `full_name` — full name
- `ubudehe_category` — 1 or 2
- `district` — district name (matched case-insensitively to `District.district_name`)
- `phone_number` — optional, Rwanda format

**Processing:**
- Parse CSV in Celery task `process_bulk_import` — do not block the request
- Skip rows with duplicate `national_id` (log them)
- Skip rows with invalid `ubudehe_category` (log them)
- Skip rows where district name does not match (log them)
- Valid rows are created with `registration_date = today`

**Success `202`:**
```json
{
  "success": true,
  "data": { "detail": "Import queued. You will be notified by email when complete." }
}
```

**Implementation:** `features/beneficiaries/tasks.py` contains `process_bulk_import(csv_content: str)`.

---

## Completion Criteria

- [ ] `GET /beneficiaries/` returns data scoped correctly for each role
- [ ] `POST /beneficiaries/` creates beneficiary with valid data
- [ ] `POST /beneficiaries/` returns `INVALID_UBUDEHE` for category 3 or 4
- [ ] `POST /beneficiaries/` returns `DUPLICATE_NATIONAL_ID` for existing national ID
- [ ] `POST /beneficiaries/` validates 16-digit national ID format
- [ ] `PATCH /beneficiaries/{id}/` updates allowed fields only
- [ ] `POST /beneficiaries/{id}/deregister/` sets all deregistration fields
- [ ] `POST /beneficiaries/{id}/deregister/` returns `PASSON_PENDING` when blocked
- [ ] `POST /beneficiaries/{id}/reregister/` clears all deregistration fields
- [ ] `GET /beneficiaries/{id}/cows/` returns living cows only
- [ ] `GET /beneficiaries/{id}/alerts/` returns unresolved alerts
- [ ] `POST /beneficiaries/bulk-import/` queues Celery task and returns 202
- [ ] `progress-tracker.md` updated
