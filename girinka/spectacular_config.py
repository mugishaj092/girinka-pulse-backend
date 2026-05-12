"""
Girinka Pulse — drf-spectacular schema customisation.
Imported by settings/base.py via SPECTACULAR_SETTINGS.
"""

SPECTACULAR_SETTINGS = {
    "TITLE": "🐄 Girinka Pulse API",
    "DESCRIPTION": """
## Rwanda "One Cow Per Family" — National Program Backend

Girinka Pulse is the AI-powered backend for Rwanda's **Girinka** poverty reduction program,
managing **500,000+ farmers** and **400,000+ cows** across all 30 districts.

---

### 🔑 Authentication

All protected endpoints require a **Bearer JWT token** in the `Authorization` header:

```
Authorization: Bearer <your_access_token>
```

**Get a token:** `POST /api/v1/auth/login/`

---

### 👥 User Roles

| Role | Scope |
|------|-------|
| `FARMER` | Own cows and milk records only |
| `CELL_LEADER` | All cows and beneficiaries in their district |
| `VETERINARIAN` | Health records + disease predictions in their district |
| `DISTRICT_LEADER` | Read-only access to all district data |
| `ADMIN` | Full system access |

---

### 📦 Standard Response Format

Every response is wrapped in:

```json
{
  "success": true,
  "data": { },
  "message": "OK",
  "errors": null,
  "meta": { "count": 100, "next": "...", "previous": null }
}
```

---

### ❌ Error Codes

| Code | HTTP | Meaning |
|------|------|---------|
| `INSUFFICIENT_MILK_DATA` | 422 | Need ≥ 7 days of milk records for LSTM |
| `COW_ALREADY_DECEASED` | 422 | Cannot update a deceased cow |
| `PASSON_PENDING` | 422 | Cannot deregister while pass-on is pending |
| `DUPLICATE_TAG_NUMBER` | 409 | Cow tag already registered |
| `INVALID_UBUDEHE` | 400 | Only categories 1 & 2 qualify |
| `MODEL_NOT_DEPLOYED` | 503 | No active ML model for this type |
| `PREDICTION_FAILED` | 503 | ML service returned error |

---

### 🤖 ML Service

All AI predictions call the **Girinka ML FastAPI** service:
`https://girinka-pulse-ml.onrender.com`

- **M1 CatBoost** — Mortality risk (0–1 score)
- **M2 LSTM** — 7-day milk yield forecast
- **M3 Random Forest** — Disease risk detection
- **M4 Logistic Regression** — Birth success probability

---

**Team:** UMUTESI Kelia · MUGISHA Joseph · MUGISHA Philippe
**Institution:** University of Rwanda — CST, Year 3, 2026
    """,
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SORT_OPERATIONS": False,
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
        "displayOperationId": False,
        "defaultModelsExpandDepth": 2,
        "defaultModelExpandDepth": 2,
        "docExpansion": "none",        # all sections collapsed by default
        "filter": True,               # search box at top
        "showExtensions": False,
        "showCommonExtensions": True,
        "syntaxHighlight.theme": "monokai",
        "tryItOutEnabled": True,
    },
    "SWAGGER_UI_FAVICON_HREF": "https://cdn.jsdelivr.net/npm/twemoji@14/2/svg/1f404.svg",
    "TAGS": [
        {"name": "🔑 Auth",            "description": "Login, logout, token refresh, password reset via email OTP"},
        {"name": "👥 Users",           "description": "User account management — Admin only"},
        {"name": "🗺️ Districts",       "description": "Rwanda district registry with GPS and live statistics"},
        {"name": "🏠 Beneficiaries",   "description": "Farmer enrollment, deregistration, and profile management"},
        {"name": "🐮 Cows",            "description": "Cow lifecycle — registration, health status, death recording, photos"},
        {"name": "🩺 Health Records",  "description": "Veterinary visit logs, treatment records, visit scheduling"},
        {"name": "🥛 Milk Production", "description": "Daily milk entry, LSTM-powered 7-day forecasting"},
        {"name": "🚨 Alerts",          "description": "AI-generated alerts — mortality, disease, low milk, with escalation"},
        {"name": "🤖 Predictions",     "description": "AI model endpoints — CatBoost, LSTM, Random Forest, Logistic Regression"},
        {"name": "🔄 Pass-On",         "description": "Calf transfer workflow — approve, complete, certificate generation"},
        {"name": "🧬 Lineage",         "description": "Cow family tree and genetic profile records"},
        {"name": "📊 Reports",         "description": "Report generation uploaded to Cloudinary and emailed via Resend"},
        {"name": "🌤️ Weather",         "description": "Daily Open-Meteo weather data per district"},
        {"name": "🔔 Notifications",   "description": "In-app notification inbox and user preferences"},
    ],
    "SCHEMA_PATH_PREFIX": "/api/v1/",
    "SERVE_PERMISSIONS": [],          # schema endpoint is public
    "POSTPROCESSING_HOOKS": [
        "drf_spectacular.hooks.postprocess_schema_enums",
    ],
}
