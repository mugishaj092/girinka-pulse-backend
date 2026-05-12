Read `progress-tracker.md`, `architecture-context.md`, and `code-standards.md` before starting.

# 01 — Database Seed

Populate the database with real reference data that all other features depend on. Without this data, every endpoint that filters by district, role, or model version will return empty results.

Do not invent data. Use real Rwanda districts with verified GPS coordinates. Do not create fake beneficiaries or cows here — those belong to demo data scripts.

---

## What To Build

### 1. District seeder — `scripts/seed_districts.py`

Create a standalone Python script at `scripts/seed_districts.py`.

The script must be idempotent — running it twice must not create duplicate records.

Use `District.objects.update_or_create(district_name=..., defaults={...})`.

Seed all 30 Rwanda districts with the following exact data:

```python
DISTRICTS = [
    # Kigali City
    {"district_name": "Nyarugenge",  "province": "Kigali",    "latitude": -1.9500, "longitude": 30.0588, "is_remote": False},
    {"district_name": "Gasabo",      "province": "Kigali",    "latitude": -1.9441, "longitude": 30.1619, "is_remote": False},
    {"district_name": "Kicukiro",    "province": "Kigali",    "latitude": -2.0041, "longitude": 30.1036, "is_remote": False},
    # Northern Province
    {"district_name": "Burera",      "province": "Northern",  "latitude": -1.4667, "longitude": 29.8667, "is_remote": True},
    {"district_name": "Gakenke",     "province": "Northern",  "latitude": -1.6833, "longitude": 29.7833, "is_remote": True},
    {"district_name": "Gicumbi",     "province": "Northern",  "latitude": -1.5833, "longitude": 30.0667, "is_remote": False},
    {"district_name": "Musanze",     "province": "Northern",  "latitude": -1.4994, "longitude": 29.6343, "is_remote": False},
    {"district_name": "Rulindo",     "province": "Northern",  "latitude": -1.7167, "longitude": 30.0333, "is_remote": True},
    # Southern Province
    {"district_name": "Gisagara",    "province": "Southern",  "latitude": -2.6167, "longitude": 29.8500, "is_remote": True},
    {"district_name": "Huye",        "province": "Southern",  "latitude": -2.5963, "longitude": 29.7392, "is_remote": False},
    {"district_name": "Kamonyi",     "province": "Southern",  "latitude": -2.0000, "longitude": 29.8833, "is_remote": False},
    {"district_name": "Muhanga",     "province": "Southern",  "latitude": -2.0833, "longitude": 29.7500, "is_remote": False},
    {"district_name": "Nyamagabe",   "province": "Southern",  "latitude": -2.4333, "longitude": 29.4833, "is_remote": True},
    {"district_name": "Nyanza",      "province": "Southern",  "latitude": -2.3500, "longitude": 29.7500, "is_remote": False},
    {"district_name": "Nyaruguru",   "province": "Southern",  "latitude": -2.7000, "longitude": 29.5500, "is_remote": True},
    {"district_name": "Ruhango",     "province": "Southern",  "latitude": -2.2167, "longitude": 29.7833, "is_remote": False},
    # Eastern Province
    {"district_name": "Bugesera",    "province": "Eastern",   "latitude": -2.1500, "longitude": 30.1167, "is_remote": False},
    {"district_name": "Gatsibo",     "province": "Eastern",   "latitude": -1.5833, "longitude": 30.4667, "is_remote": False},
    {"district_name": "Kayonza",     "province": "Eastern",   "latitude": -1.8833, "longitude": 30.6500, "is_remote": False},
    {"district_name": "Kirehe",      "province": "Eastern",   "latitude": -2.1667, "longitude": 30.6833, "is_remote": False},
    {"district_name": "Ngoma",       "province": "Eastern",   "latitude": -2.1500, "longitude": 30.5000, "is_remote": False},
    {"district_name": "Nyagatare",   "province": "Eastern",   "latitude": -1.3000, "longitude": 30.3333, "is_remote": False},
    {"district_name": "Rwamagana",   "province": "Eastern",   "latitude": -1.9500, "longitude": 30.4333, "is_remote": False},
    # Western Province
    {"district_name": "Karongi",     "province": "Western",   "latitude": -2.0667, "longitude": 29.3667, "is_remote": True},
    {"district_name": "Ngororero",   "province": "Western",   "latitude": -1.8833, "longitude": 29.5333, "is_remote": True},
    {"district_name": "Nyabihu",     "province": "Western",   "latitude": -1.6333, "longitude": 29.5167, "is_remote": True},
    {"district_name": "Nyamasheke",  "province": "Western",   "latitude": -2.3333, "longitude": 29.2000, "is_remote": True},
    {"district_name": "Rubavu",      "province": "Western",   "latitude": -1.6833, "longitude": 29.2500, "is_remote": False},
    {"district_name": "Rusizi",      "province": "Western",   "latitude": -2.4833, "longitude": 28.9000, "is_remote": False},
    {"district_name": "Rutsiro",     "province": "Western",   "latitude": -1.9500, "longitude": 29.3833, "is_remote": True},
]
```

The script must print a summary when done:

```
Seeding 30 Rwanda districts...
  ✅ Nyarugenge (Kigali)
  ✅ Gasabo (Kigali)
  ... (one line per district)
Done. 30 districts seeded.
```

---

### 2. AI model version seeder — `scripts/seed_ai_models.py`

Create a standalone Python script at `scripts/seed_ai_models.py`.

This script registers the 4 trained ML model versions in the `ai_models` table so the predictions module can reference them. Only one model of each type can have `is_deployed=True`.

The script must be idempotent — running it twice must not create duplicate records or flip deployment status.

Use `AIModel.objects.update_or_create(model_type=..., version=..., defaults={...})`.

Seed these 4 records:

```python
AI_MODELS = [
    {
        "model_type": "CATBOOST",
        "version": "v1.0.0",
        "accuracy_metric": 0.9812,
        "r2_score": 0.9282,
        "mae": 0.0372,
        "rmse": 0.0479,
        "training_samples": 4000,
        "training_data_source": "synthetic — mortality_train.csv",
        "model_file_path": "ml_models/catboost/v1.0.0.cbm",
        "scaler_file_path": None,
        "is_deployed": True,
    },
    {
        "model_type": "LSTM",
        "version": "v1.0.0",
        "accuracy_metric": None,
        "r2_score": None,
        "mae": 0.0776,
        "rmse": 0.0940,
        "training_samples": 13440,
        "training_data_source": "synthetic — milk_train.csv",
        "model_file_path": "ml_models/lstm/v1.0.0.keras",
        "scaler_file_path": "ml_models/lstm/scaler_v1.0.0.pkl",
        "is_deployed": True,
    },
    {
        "model_type": "RANDOM_FOREST",
        "version": "v1.0.0",
        "accuracy_metric": 0.9639,
        "r2_score": None,
        "mae": None,
        "rmse": None,
        "training_samples": 2418,
        "training_data_source": "synthetic — disease_train.csv",
        "model_file_path": "ml_models/random_forest/v1.0.0.pkl",
        "scaler_file_path": "ml_models/random_forest/scaler_v1.0.0.pkl",
        "is_deployed": True,
    },
    {
        "model_type": "LOGISTIC_REGRESSION",
        "version": "v1.0.0",
        "accuracy_metric": 0.8767,
        "r2_score": None,
        "mae": None,
        "rmse": None,
        "training_samples": 2400,
        "training_data_source": "synthetic — birth_train.csv",
        "model_file_path": "ml_models/logistic/v1.0.0.pkl",
        "scaler_file_path": "ml_models/logistic/scaler_v1.0.0.pkl",
        "is_deployed": True,
    },
]
```

Print summary when done:

```
Seeding 4 AI model versions...
  ✅ CATBOOST v1.0.0 (deployed)
  ✅ LSTM v1.0.0 (deployed)
  ✅ RANDOM_FOREST v1.0.0 (deployed)
  ✅ LOGISTIC_REGRESSION v1.0.0 (deployed)
Done. 4 AI models seeded.
```

---

### 3. Admin user creation command — `scripts/create_admin.py`

Create a script that creates the first admin user if none exists.

```python
# Usage: python scripts/create_admin.py
# Reads from environment or prompts interactively
```

The script must:
- Check if any `ADMIN` role user already exists — if so, print a message and exit
- If not, create one using `User.objects.create_user()`
- Set `role = "ADMIN"`, `is_staff = True`, `is_superuser = True`
- Print credentials when done

---

### 4. Update `scripts/setup.sh`

Add the new seed scripts to the setup sequence:

```bash
# After migrate
echo "🌍 Seeding districts..."
python scripts/seed_districts.py

echo "🤖 Seeding AI model records..."
python scripts/seed_ai_models.py

echo "⏰ Seeding Celery schedules..."
python scripts/seed_celery_schedules.py

echo "👤 Creating admin user..."
python scripts/create_admin.py
```

---

## Completion Criteria

- [ ] `python scripts/seed_districts.py` runs without error and creates exactly 30 districts
- [ ] Running it a second time creates zero duplicates
- [ ] `python scripts/seed_ai_models.py` creates 4 records, all with `is_deployed=True`
- [ ] `GET /api/v1/districts/` returns 30 district objects
- [ ] `GET /api/v1/predictions/models/` returns 4 model objects (requires admin token)
- [ ] `setup.sh` runs all seed steps in order without error
- [ ] `progress-tracker.md` updated
