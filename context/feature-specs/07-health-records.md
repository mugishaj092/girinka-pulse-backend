Read `progress-tracker.md`, `architecture-context.md`, `api-context.md`, and `code-standards.md` before starting.

# 07 — Health Records

Verify and complete the Health Records module. Health records are veterinary visit logs — diagnosis, treatment, temperature, weight, and next visit scheduling. They are the primary source of vet coverage data used by the mortality prediction model.

Requires: spec `06-cows` complete (cows exist to attach health records to).

---

## Endpoints

All under `/api/v1/health/`.

---

### GET `/api/v1/health/`

**Auth required:** Cell Leader and above

**Data scoping:**
- `CELL_LEADER` / `VETERINARIAN` / `DISTRICT_LEADER` → records for cows in their district
- `ADMIN` → all records nationally

**Query parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `cow` | integer | Filter by cow ID |
| `vet` | integer | Filter by veterinarian ID |
| `date_after` | date | Records from this date (format: `YYYY-MM-DD`) |
| `date_before` | date | Records up to this date |
| `page` | integer | Page number |

**Success `200`:**
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

### POST `/api/v1/health/`

**Auth required:** Veterinarian, Admin

**Request:**
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

**Required fields:** `cow`, `date_recorded`

**Optional fields:** `vet`, `diagnosis`, `treatment_given`, `symptoms`, `temperature`, `weight`, `next_visit_date`

**Validation:**
- `cow` must exist and `is_alive=True`. If deceased:
```json
{
  "success": false,
  "error_code": "COW_ALREADY_DECEASED",
  "message": "Cannot add a health record for a deceased cow."
}
```
- `temperature` must be between `35.0` and `45.0` °C if provided
- `weight` must be between `50.0` and `1000.0` kg if provided

**Success `201`:** Returns created health record.

**Side effect:** If `mortality_risk_score` is set on the record, update the linked cow's `mortality_risk_score` field automatically.

---

### GET `/api/v1/health/{id}/`

**Auth required:** Any authenticated user

**Success `200`:** Returns full health record.

---

### PATCH `/api/v1/health/{id}/`

**Auth required:** Veterinarian, Admin

**Request** (all optional):
```json
{
  "treatment_given": "Oxytetracycline 20mg/kg IM + vitamin B12.",
  "next_visit_date": "2026-05-20",
  "diagnosis": "Respiratory infection — improved"
}
```

**Success `200`:** Returns updated health record.

---

### GET `/api/v1/health/schedule/`

**Auth required:** Veterinarian, Cell Leader and above

Returns all upcoming vet visits where `next_visit_date >= today`, ordered by `next_visit_date` ascending. Limit to 50 records.

**Success `200`:**
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
      "diagnosis": "Respiratory infection follow-up"
    }
  ]
}
```

---

### POST `/api/v1/health/schedule/`

**Auth required:** Veterinarian, Admin

Creates a new health record specifically for scheduling a future visit.

**Request:**
```json
{
  "cow": 42,
  "vet": 5,
  "next_visit_date": "2026-05-16",
  "diagnosis": "Routine follow-up after respiratory treatment",
  "date_recorded": "2026-05-02T10:30:00+02:00"
}
```

Internally calls the same `HealthRecord` creation logic — there is no separate schedule model.

---

## Veterinarian Profile Endpoint

The `Veterinarian` model stores the professional profile linked to a `User` with `role=VETERINARIAN`. Expose it under health for now.

### GET `/api/v1/health/vets/`

**Auth required:** Cell Leader and above

Returns active veterinarians in the district (scoped).

**Success `200`:**
```json
{
  "success": true,
  "data": [
    {
      "id": 5,
      "user": 12,
      "full_name": "Dr. HABIMANA Eric",
      "district": 3,
      "district_name": "Gasabo",
      "license_number": "RW-VET-2020-001",
      "specialization": "Large animal medicine",
      "is_active": true
    }
  ]
}
```

---

## Completion Criteria

- [ ] `GET /health/` returns records scoped to user's district
- [ ] `GET /health/` filters by `cow`, `vet`, `date_after`, `date_before`
- [ ] `POST /health/` creates record with all required validations
- [ ] `POST /health/` returns `COW_ALREADY_DECEASED` for dead cows
- [ ] `POST /health/` validates temperature and weight ranges
- [ ] `GET /health/{id}/` returns correct record
- [ ] `PATCH /health/{id}/` updates allowed fields
- [ ] `GET /health/schedule/` returns upcoming visits sorted by date
- [ ] `GET /health/vets/` returns district-scoped vet profiles
- [ ] `progress-tracker.md` updated
