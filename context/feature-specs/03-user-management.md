Read `progress-tracker.md`, `architecture-context.md`, `api-context.md`, and `code-standards.md` before starting.

# 03 — User Management

Verify and complete the Users module. Admin can create, list, update, deactivate, and audit all user accounts. This module is the prerequisite for all role-based access — districts, beneficiaries, and cows all depend on users existing with correct roles.

---

## Endpoints

All under `/api/v1/users/`. All require `Admin` role.

---

### GET `/api/v1/users/`

**Auth required:** Admin only

**Query parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `role` | string | Filter by role: `FARMER`, `CELL_LEADER`, `VETERINARIAN`, `DISTRICT_LEADER`, `ADMIN` |
| `district` | integer | Filter by district ID |
| `is_active` | boolean | `true` or `false` |
| `search` | string | Match on `username` or `full_name` |
| `page` | integer | Page number |
| `page_size` | integer | Max 100 |

**Success `200`:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@girinka.rw",
      "full_name": "Admin User",
      "phone_number": null,
      "role": "ADMIN",
      "district": null,
      "is_active": true,
      "is_verified": false,
      "created_at": "2026-05-02T10:00:00+02:00"
    }
  ],
  "meta": { "count": 1, "next": null, "previous": null }
}
```

**403 for non-admin:** Any user with role other than `ADMIN` must get `403 Forbidden`.

---

### POST `/api/v1/users/`

**Auth required:** Admin only

**Request:**
```json
{
  "username": "mugisha_joseph",
  "password": "SecurePass@2026",
  "full_name": "MUGISHA Joseph",
  "email": "joseph@girinka.rw",
  "phone_number": "+250788123456",
  "role": "CELL_LEADER",
  "district": 3,
  "national_id": "1199070123456789"
}
```

**Required fields:** `username`, `password`, `full_name`, `role`

**Optional fields:** `email`, `phone_number`, `district`, `national_id`

**Success `201`:** Returns created user object (without `password`).

**Error `400`:** Username already taken.
```json
{
  "success": false,
  "message": "A user with that username already exists.",
  "errors": { "username": ["A user with that username already exists."] }
}
```

**Password hashing:** Password must be stored as bcrypt hash via Django's `set_password()`. Never store plain text.

**Verify:**
- After creation, the user can log in with `POST /auth/login/` using their credentials
- `password` field is never returned in any response

---

### GET `/api/v1/users/{id}/`

**Auth required:** Admin only

**Success `200`:** Returns full user object.

**Error `404`:** User ID does not exist.

---

### PATCH `/api/v1/users/{id}/`

**Auth required:** Admin only

**Request** (all fields optional):
```json
{
  "full_name": "MUGISHA Joseph Emmanuel",
  "email": "joseph.new@girinka.rw",
  "role": "DISTRICT_LEADER",
  "district": 3,
  "is_active": true,
  "phone_number": "+250722987654"
}
```

**Success `200`:** Returns updated user object.

**Cannot change via this endpoint:** `username`, `password` (use `/auth/password/change/` for password).

---

### DELETE `/api/v1/users/{id}/`

**Auth required:** Admin only

**Behavior:** Soft delete — sets `is_active = False`. Does **not** delete the record from the database. This preserves audit trail and foreign key integrity.

**Success `204`:** No content.

**Verify:**
- After DELETE, `GET /users/{id}/` still returns the user with `is_active: false`
- The deactivated user cannot log in (login returns `400 Account is deactivated`)

---

### GET `/api/v1/users/{id}/activity/`

**Auth required:** Admin only

Returns the last 50 audit log entries for this user — all their CREATE, UPDATE, DELETE, and LOGIN actions recorded in `audit_logs`.

**Success `200`:**
```json
{
  "success": true,
  "data": [
    {
      "id": 12,
      "action": "CREATE",
      "resource_type": "Cow",
      "resource_id": 42,
      "old_values": null,
      "new_values": { "tag_number": "RW-GAS-001", "breed": "FRIESIAN_CROSS" },
      "ip_address": "197.243.12.45",
      "user_agent": "Mozilla/5.0...",
      "created_at": "2026-05-02T09:15:00+02:00"
    }
  ],
  "meta": { "count": 12, "next": null, "previous": null }
}
```

If the user has no audit log entries yet, return an empty list — not a 404.

---

## Role Enforcement Verification

Test that every non-admin role is blocked from all user management endpoints.

Create test users with each role. Attempt `GET /api/v1/users/` with each. All must return `403`.

```bash
# FARMER token
curl -H "Authorization: Bearer $FARMER_TOKEN" http://localhost:8000/api/v1/users/
# Expected: 403

# CELL_LEADER token
curl -H "Authorization: Bearer $CL_TOKEN" http://localhost:8000/api/v1/users/
# Expected: 403
```

---

## Missing Pieces To Check For

### `UserCreateSerializer` in `features/users/serializers.py`

Must include `password` as a write-only field. Must call `user.set_password(password)` in `create()`.

### `UserUpdateSerializer` in `features/users/serializers.py`

Must **exclude** `username` and `password` from updatable fields.

### `UserViewSet.perform_destroy()` in `features/users/views.py`

Must soft-delete: `instance.is_active = False; instance.save(update_fields=["is_active"])`. Must not call `instance.delete()`.

### `UserViewSet` uses `IsAdmin` permission class

```python
permission_classes = [IsAdmin]
```

---

## Completion Criteria

- [ ] `GET /users/` returns paginated list with filters working
- [ ] `POST /users/` creates user, password is hashed, user can log in
- [ ] `POST /users/` returns `400` for duplicate username
- [ ] `GET /users/{id}/` returns full profile
- [ ] `PATCH /users/{id}/` updates allowed fields
- [ ] `DELETE /users/{id}/` soft-deletes — user still exists with `is_active: false`
- [ ] Deleted user cannot log in
- [ ] `GET /users/{id}/activity/` returns audit log entries
- [ ] All endpoints return `403` for non-admin users
- [ ] `progress-tracker.md` updated
