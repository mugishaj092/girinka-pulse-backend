# 🤖 Girinka Pulse — Predictions API Reference

> All prediction endpoints call the **Girinka ML FastAPI service** at `https://girinka-pulse-ml.onrender.com`
>
> **Base URL:** `http://localhost:8000/api/v1/predictions/`
> **Auth required:** All endpoints need `Authorization: Bearer <access_token>`

---

## Table of Contents

- [POST /predictions/mortality/](#post-apiv1predictionsmortality)
- [POST /predictions/milk/](#post-apiv1predictionsmilk)
- [POST /predictions/disease/](#post-apiv1predictionsdisease)
- [POST /predictions/passon/](#post-apiv1predictionspasson)
- [GET /predictions/history/](#get-apiv1predictionshistory)
- [GET /predictions/history/{id}/](#get-apiv1predictionshistoryid)
- [GET /predictions/models/](#get-apiv1predictionsmodels)
- [GET /predictions/models/{id}/](#get-apiv1predictionsmodelsid)
- [POST /predictions/models/{id}/deploy/](#post-apiv1predictionsmodelsiddeploy)
- [GET /predictions/models/performance/](#get-apiv1predictionsmodelsperformance)
- [POST /predictions/models/retrain/](#post-apiv1predictionsmodelsretrain)
- [GET /predictions/models/health_check/](#get-apiv1predictionsmodelshealthcheck)

---

## How It Works

```
Your Frontend
     │
     ▼
POST /api/v1/predictions/mortality/    ← Django backend
     │
     ▼  (internal HTTP call via httpx)
POST /predict/mortality                ← ML FastAPI service
     │
     ▼  (CatBoost model runs)
← risk score, alert level, recommendation
     │
     ▼  (Django saves result, creates alert, sends email)
← response back to frontend
```

Every prediction is:
1. **Sent** to the ML service
2. **Logged** in `PredictionLog` table with full input + output
3. **Saved** back to the cow record
4. **Alerts** created automatically if thresholds exceeded
5. **Emails** sent via Resend if severity is high enough

---

## POST /api/v1/predictions/mortality/

**Model:** M1 — CatBoost Regressor
**ML endpoint called:** `POST /predict/mortality`
**Auth required:** ✅ Cell Leader and above

Runs the CatBoost mortality risk prediction for a specific cow. Pulls all required features from the database automatically — you only need to send `cow_id`.

**Side effects:**
- Updates `cow.mortality_risk_score`
- Updates `cow.health_status` based on risk level
- Creates an `Alert` if risk ≥ 0.50
- Sends alert email via Resend if risk ≥ 0.60
- Logs result in `PredictionLog`

### Request Body

```json
{
  "cow_id": 42
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `cow_id` | integer | ✅ | ID of the cow to run prediction for |

### Response `200`

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

| Field | Type | Description |
|-------|------|-------------|
| `cow_id` | integer | Echoed back |
| `mortality_risk_score` | float | Risk score from 0.0 (safe) to 1.0 (critical) |
| `risk_level` | string | One of: `LOW`, `MEDIUM_LOW`, `MEDIUM`, `HIGH`, `VERY_HIGH`, `EMERGENCY` |
| `alert_triggered` | boolean | `true` if score ≥ 0.50 |
| `alert_severity` | string | `NONE`, `INFO`, `WARNING`, `URGENT`, `CRITICAL` |
| `sms_required` | boolean | `true` if score ≥ 0.80 |
| `sms_recipients` | array | Who gets SMS: `farmer`, `cell_leader`, `district_vet` |
| `recommended_action` | string | Plain-language action for the vet or cell leader |
| `model_version` | string | Deployed model version |

### Risk Level Reference

| Score Range | Risk Level | Alert Severity | Email Sent |
|-------------|------------|----------------|------------|
| 0.90 – 1.00 | `EMERGENCY` | `CRITICAL` | ✅ farmer + cell leader + vet |
| 0.80 – 0.89 | `VERY_HIGH` | `CRITICAL` | ✅ farmer + cell leader |
| 0.60 – 0.79 | `HIGH` | `URGENT` | ✅ farmer |
| 0.50 – 0.59 | `MEDIUM` | `WARNING` | ❌ |
| 0.30 – 0.49 | `MEDIUM_LOW` | `INFO` | ❌ |
| 0.00 – 0.29 | `LOW` | `NONE` | ❌ |

### Response `404` — Cow not found

```json
{
  "success": false,
  "message": "Cow not found.",
  "errors": { "detail": "Cow not found." }
}
```

### Response `503` — ML service down

```json
{
  "success": false,
  "error_code": "PREDICTION_FAILED",
  "message": "ML service returned an error."
}
```

### Example — Healthy cow (LOW risk)

```json
{
  "success": true,
  "data": {
    "cow_id": 7,
    "mortality_risk_score": 0.09,
    "risk_level": "LOW",
    "alert_triggered": false,
    "alert_severity": "NONE",
    "sms_required": false,
    "sms_recipients": [],
    "recommended_action": "✅ Cow appears healthy. Continue routine monthly monitoring.",
    "model_version": "v1.0.0"
  }
}
```

### Example — Emergency cow

```json
{
  "success": true,
  "data": {
    "cow_id": 18,
    "mortality_risk_score": 0.9320,
    "risk_level": "EMERGENCY",
    "alert_triggered": true,
    "alert_severity": "CRITICAL",
    "sms_required": true,
    "sms_recipients": ["farmer", "cell_leader", "district_vet"],
    "recommended_action": "🚨 Emergency vet immediately. Notify farmer, cell leader and district vet.",
    "model_version": "v1.0.0"
  }
}
```

---

## POST /api/v1/predictions/milk/

**Model:** M2 — Bidirectional LSTM
**ML endpoint called:** `POST /predict/milk`
**Auth required:** ✅ Any role

Runs the LSTM 7-day milk yield forecast for a specific cow. The Django backend automatically fetches the last 15 milk records from the database and builds the sequence payload for the ML service.

**Requires:** At least **7 days** of milk records in `MilkProduction` table for this cow.

**Side effects:**
- Creates a `LOW_MILK` alert if the average forecast < 5 L/day
- Logs result in `PredictionLog`

### Request Body

```json
{
  "cow_id": 7
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `cow_id` | integer | ✅ | ID of the cow to forecast |

### Response `200`

```json
{
  "success": true,
  "data": {
    "cow_id": 7,
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

| Field | Type | Description |
|-------|------|-------------|
| `forecast_days` | integer | Always 7 |
| `forecasts` | array | One object per day |
| `forecasts[].day` | integer | Day from today (1 = tomorrow) |
| `forecasts[].predicted_yield_litres` | float | Predicted litres for that day |
| `forecasts[].confidence` | string | `high` (≥15 records), `medium` (7–14 records) |
| `avg_predicted_yield_litres` | float | Average across 7 days |
| `total_predicted_litres` | float | Total litres for the week |
| `data_quality` | string | `sufficient` (≥15 records) or `low_confidence` (7–14) |
| `note` | string | Human-readable data quality message |
| `model_version` | string | Deployed LSTM version |

### Confidence Reference

| Records Available | Confidence | Data Quality |
|-------------------|------------|--------------|
| 15 – 30 days | `high` | `sufficient` |
| 7 – 14 days | `medium` | `low_confidence` |
| < 7 days | — | Returns `422` error |

### Response `422` — Not enough records

```json
{
  "success": false,
  "error_code": "INSUFFICIENT_MILK_DATA",
  "message": "LSTM requires at least 7 days of milk records."
}
```

### Response `404` — Cow not found

```json
{
  "success": false,
  "message": "Cow not found.",
  "errors": { "detail": "Cow not found." }
}
```

### Example — Low-producing cow (alert triggered)

```json
{
  "success": true,
  "data": {
    "cow_id": 31,
    "forecast_days": 7,
    "forecasts": [
      { "day": 1, "predicted_yield_litres": 4.2, "confidence": "medium" },
      { "day": 2, "predicted_yield_litres": 4.0, "confidence": "medium" },
      { "day": 3, "predicted_yield_litres": 3.8, "confidence": "medium" },
      { "day": 4, "predicted_yield_litres": 3.7, "confidence": "medium" },
      { "day": 5, "predicted_yield_litres": 3.6, "confidence": "medium" },
      { "day": 6, "predicted_yield_litres": 3.5, "confidence": "medium" },
      { "day": 7, "predicted_yield_litres": 3.4, "confidence": "medium" }
    ],
    "avg_predicted_yield_litres": 3.74,
    "total_predicted_litres": 26.2,
    "data_quality": "low_confidence",
    "note": "Only 10 days provided. Provide 15+ for best accuracy.",
    "model_version": "v1.0.0"
  }
}
```

> ⚠️ Because avg < 5 L/day, a `LOW_MILK` alert with severity `WARNING` was automatically created.

---

## POST /api/v1/predictions/disease/

**Model:** M3 — Random Forest (500 trees)
**ML endpoint called:** `POST /predict/disease`
**Auth required:** ✅ Veterinarian and above

Detects disease risk across 7 disease classes based on observed symptoms and environmental factors. This is the only prediction endpoint where you send symptom data directly — it is not pulled from the database automatically.

**Side effects:**
- Logs result in `PredictionLog`
- Does **not** auto-create alerts (vet must review and act)

### Request Body

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

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `cow_id` | integer | ✅ | Cow identifier |
| `breed` | string | ✅ | Cow breed |
| `age_months` | integer | ✅ | Age in months (min: 12) |
| `body_temperature_c` | float | ✅ | Body temperature in °C (normal: 38.0–39.5) |
| `weight_kg` | float | ✅ | Body weight in kg (min: 50) |
| `feeding_type` | string | ✅ | `Poor`, `Adequate`, or `Good` |
| `water_access` | boolean | ❌ | Defaults to `true` |
| `disease_cases_last_90d` | integer | ❌ | Number of disease incidents in last 90 days |
| `outbreak_flag_last_30d` | boolean | ❌ | Known outbreak in district? |
| `nearest_outbreak_km` | float | ❌ | Distance to nearest known outbreak |
| `avg_temperature_c` | float | ❌ | District average temperature |
| `avg_rainfall_mm` | float | ❌ | District average annual rainfall |
| `humidity_pct` | float | ❌ | Humidity percentage (0–100) |
| `fever` | boolean | ❌ | Observed fever |
| `lameness` | boolean | ❌ | Observed lameness |
| `nasal_discharge` | boolean | ❌ | Observed nasal discharge |
| `skin_lesions` | boolean | ❌ | Observed skin lesions |
| `reduced_appetite` | boolean | ❌ | Observed reduced appetite |
| `weight_loss` | boolean | ❌ | Observed weight loss |
| `swollen_lymph_nodes` | boolean | ❌ | Observed swollen lymph nodes |
| `diarrhea` | boolean | ❌ | Observed diarrhea |
| `labored_breathing` | boolean | ❌ | Observed labored breathing |
| `mastitis_signs` | boolean | ❌ | Observed mastitis signs |

### Response `200`

```json
{
  "success": true,
  "data": {
    "cow_id": 12,
    "top_prediction": "FMD",
    "top_probability": 0.9708,
    "all_disease_probabilities": {
      "FMD": 0.9708,
      "ECF": 0.0120,
      "Mastitis": 0.0080,
      "Respiratory": 0.0050,
      "Nutritional_Deficiency": 0.0030,
      "Brucellosis": 0.0010,
      "LSD": 0.0001
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

| Field | Type | Description |
|-------|------|-------------|
| `top_prediction` | string | Disease class with highest probability |
| `top_probability` | float | Probability of top prediction (0.0–1.0) |
| `all_disease_probabilities` | object | Probability for each of the 7 disease classes |
| `triggered_alerts` | array | Diseases that exceeded their alert threshold |
| `triggered_alerts[].disease` | string | Disease name |
| `triggered_alerts[].probability` | float | Predicted probability |
| `triggered_alerts[].threshold_used` | float | Threshold that triggered the alert |
| `triggered_alerts[].recommended_action` | string | Vet action to take immediately |
| `emergency` | boolean | `true` if FMD or Brucellosis threshold exceeded |
| `total_symptoms_observed` | integer | Count of `true` symptom flags sent |
| `model_version` | string | Deployed Random Forest version |

### Disease Alert Thresholds

| Disease | Threshold | Emergency | Recommended Action |
|---------|-----------|-----------|-------------------|
| `FMD` | 0.60 | ✅ Yes | Isolate cow. Notify RAB and district vet. No contact with other animals |
| `ECF` | 0.55 | ❌ | Urgent vet visit within 24 hours. Begin tick treatment protocol |
| `Mastitis` | 0.50 | ❌ | Reduce milking pressure. Vet visit within 48 hours |
| `Respiratory` | 0.55 | ❌ | Vet visit within 24 hours. Improve shelter ventilation |
| `Nutritional_Deficiency` | 0.65 | ❌ | Adjust feed immediately. Contact Ehinga platform |
| `Brucellosis` | 0.70 | ✅ Yes | Quarantine immediately. Notify district leader. Zoonotic risk to humans |
| `LSD` | 0.60 | ❌ | Vaccinate herd contacts. Notify district vet office |

### Example — Mastitis detected

```json
{
  "success": true,
  "data": {
    "cow_id": 9,
    "top_prediction": "Mastitis",
    "top_probability": 0.8240,
    "all_disease_probabilities": {
      "FMD": 0.0210,
      "ECF": 0.0180,
      "Mastitis": 0.8240,
      "Respiratory": 0.0910,
      "Nutritional_Deficiency": 0.0310,
      "Brucellosis": 0.0080,
      "LSD": 0.0070
    },
    "triggered_alerts": [
      {
        "disease": "Mastitis",
        "probability": 0.8240,
        "threshold_used": 0.50,
        "alert_triggered": true,
        "recommended_action": "Reduce milking pressure. Vet visit within 48 hours. Record reduced yield."
      }
    ],
    "emergency": false,
    "total_symptoms_observed": 2,
    "model_version": "v1.0.0"
  }
}
```

### Example — Healthy cow, no alerts

```json
{
  "success": true,
  "data": {
    "cow_id": 5,
    "top_prediction": "Nutritional_Deficiency",
    "top_probability": 0.4120,
    "all_disease_probabilities": {
      "FMD": 0.0450,
      "ECF": 0.0380,
      "Mastitis": 0.0920,
      "Respiratory": 0.1240,
      "Nutritional_Deficiency": 0.4120,
      "Brucellosis": 0.0210,
      "LSD": 0.2680
    },
    "triggered_alerts": [],
    "emergency": false,
    "total_symptoms_observed": 0,
    "model_version": "v1.0.0"
  }
}
```

---

## POST /api/v1/predictions/passon/

**Model:** M4 — Logistic Regression
**ML endpoint called:** `POST /predict/birth`
**Auth required:** ✅ Cell Leader and above

Predicts the probability of a successful calving outcome for a pregnant cow. Score ≥ 0.86 auto-flags the calf as eligible for the Pass-On program.

**Side effects:**
- Logs result in `PredictionLog`
- Does **not** auto-create a Pass-On record — it just returns the eligibility flag

### Request Body

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

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `cow_id` | integer | ✅ | Cow identifier |
| `breed` | string | ✅ | Cow breed |
| `cow_age_months` | integer | ✅ | Cow age in months (min: 24) |
| `lactation_number` | integer | ✅ | How many times she has calved (min: 1) |
| `initial_health_status` | string | ✅ | `Poor`, `Fair`, `Good`, or `Excellent` |
| `feeding_type` | string | ✅ | `Poor`, `Adequate`, or `Good` |
| `water_access` | boolean | ❌ | Defaults to `true` |
| `disease_cases_last_180d` | integer | ❌ | Illness incidents during gestation |
| `vet_access` | boolean | ❌ | Access to assisted delivery |
| `avg_temperature_last_trim` | float | ❌ | Average °C during last trimester |
| `days_until_expected_birth` | integer | ❌ | Predicted days to calving |

### Response `200`

```json
{
  "success": true,
  "data": {
    "cow_id": 5,
    "birth_success_probability": 0.9230,
    "prognosis_label": "Excellent",
    "pass_on_eligible": true,
    "recommended_action": "✅ Auto-flag calf for Pass-On program after birth.",
    "model_version": "v1.0.0"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `birth_success_probability` | float | Probability of successful birth (0.0–1.0) |
| `prognosis_label` | string | `Excellent`, `Good`, `Moderate`, or `High Risk` |
| `pass_on_eligible` | boolean | `true` only when prognosis is `Excellent` (score ≥ 0.86) |
| `recommended_action` | string | Plain-language action |
| `model_version` | string | Deployed Logistic Regression version |

### Prognosis Reference

| Score Range | Label | Pass-On Eligible | Action |
|-------------|-------|-----------------|--------|
| 0.86 – 1.00 | `Excellent` | ✅ Yes | Auto-flag calf for Pass-On after birth |
| 0.66 – 0.85 | `Good` | ❌ | Schedule routine vet check 1 week before birth |
| 0.41 – 0.65 | `Moderate` | ❌ | Schedule vet visit within 2 weeks |
| 0.00 – 0.40 | `High Risk` | ❌ | Urgent pre-birth vet exam. Alert cell leader |

### Example — First-time calver, moderate risk

```json
{
  "success": true,
  "data": {
    "cow_id": 22,
    "birth_success_probability": 0.5410,
    "prognosis_label": "Moderate",
    "pass_on_eligible": false,
    "recommended_action": "🟡 Schedule vet visit within 2 weeks. Monitor closely.",
    "model_version": "v1.0.0"
  }
}
```

### Example — Old cow, poor conditions, high risk

```json
{
  "success": true,
  "data": {
    "cow_id": 18,
    "birth_success_probability": 0.2840,
    "prognosis_label": "High Risk",
    "pass_on_eligible": false,
    "recommended_action": "🔴 Urgent pre-birth vet exam required. Alert cell leader.",
    "model_version": "v1.0.0"
  }
}
```

---

## GET /api/v1/predictions/history/

**Auth required:** ✅ Cell Leader and above

Returns the prediction audit log — every AI prediction ever run, with full input features and output values stored. Filter by cow to see a specific cow's AI history.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `cow_id` | integer | ❌ | Filter predictions for a specific cow |
| `prediction_type` | string | ❌ | `MORTALITY_RISK`, `MILK_FORECAST`, `DISEASE_RISK`, `BIRTH_PROBABILITY` |
| `page` | integer | ❌ | Page number (default: 1) |
| `page_size` | integer | ❌ | Results per page (max: 100) |

### Response `200`

```json
{
  "success": true,
  "data": [
    {
      "id": 301,
      "cow": 42,
      "model": 1,
      "prediction_type": "MORTALITY_RISK",
      "input_features": {
        "disease_cases": 3,
        "vet_coverage_rate": 0.45,
        "poverty_rate": 0.50,
        "years_in_program": 2.5
      },
      "output_values": {
        "mortality_risk_score": 0.7155,
        "risk_level": "HIGH",
        "alert_triggered": true
      },
      "confidence_score": 0.7155,
      "predicted_at": "2026-05-02T06:30:00+02:00"
    },
    {
      "id": 298,
      "cow": 42,
      "model": 2,
      "prediction_type": "MILK_FORECAST",
      "input_features": {
        "records_used": 15,
        "avg_daily_yield": 12.5
      },
      "output_values": {
        "avg_predicted_yield_litres": 11.97,
        "total_predicted_litres": 83.8
      },
      "confidence_score": null,
      "predicted_at": "2026-05-02T06:05:00+02:00"
    }
  ],
  "meta": {
    "count": 148,
    "next": "http://localhost:8000/api/v1/predictions/history/?page=2",
    "previous": null
  }
}
```

---

## GET /api/v1/predictions/history/{id}/

**Auth required:** ✅ Cell Leader and above

Get full detail of a single prediction log entry including complete input features and output values.

### Response `200`

```json
{
  "success": true,
  "data": {
    "id": 301,
    "cow": 42,
    "model": 1,
    "prediction_type": "MORTALITY_RISK",
    "input_features": {
      "cow_id": 42,
      "breed": "FRIESIAN_CROSS",
      "district": "Bugesera",
      "ubudehe_category": 1,
      "initial_health_status": "Fair",
      "feeding_type": "Adequate",
      "water_source": "River",
      "disease_cases": 3,
      "vet_coverage_rate": 0.45,
      "poverty_rate": 0.50,
      "years_in_program": 2.5,
      "reproduction_count": 1,
      "lactation_number": 2,
      "days_since_last_vet_visit": 90,
      "avg_temperature_c": 22.5,
      "avg_rainfall_mm": 850.0
    },
    "output_values": {
      "mortality_risk_score": 0.7155,
      "risk_level": "HIGH",
      "alert_triggered": true,
      "alert_severity": "URGENT",
      "recommended_action": "🔶 Urgent vet consultation within 24 hours.",
      "model_version": "v1.0.0"
    },
    "confidence_score": 0.7155,
    "predicted_at": "2026-05-02T06:30:00+02:00"
  }
}
```

---

## GET /api/v1/predictions/models/

**Auth required:** ✅ Admin only

List all AI model versions registered in the system — both deployed and historical versions.

### Response `200`

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
      "last_training_date": "2026-04-30T02:00:00+02:00",
      "feature_columns": [
        "disease_cases", "vet_coverage_rate", "health_encoded",
        "health_feeding_interaction", "poverty_rate"
      ],
      "model_file_path": "ml_models/catboost/v1.0.0.cbm",
      "created_at": "2026-04-30T04:00:00+02:00"
    },
    {
      "id": 2,
      "model_type": "LSTM",
      "version": "v1.0.0",
      "accuracy_metric": null,
      "r2_score": null,
      "mae": 0.0776,
      "rmse": 0.0940,
      "is_deployed": true,
      "training_samples": 13440,
      "last_training_date": "2026-04-30T02:00:00+02:00",
      "model_file_path": "ml_models/lstm/v1.0.0.keras",
      "created_at": "2026-04-30T04:30:00+02:00"
    },
    {
      "id": 3,
      "model_type": "RANDOM_FOREST",
      "version": "v1.0.0",
      "accuracy_metric": 0.9639,
      "r2_score": null,
      "mae": null,
      "rmse": null,
      "is_deployed": true,
      "training_samples": 2418,
      "last_training_date": "2026-04-30T02:00:00+02:00",
      "model_file_path": "ml_models/random_forest/v1.0.0.pkl",
      "created_at": "2026-04-30T05:00:00+02:00"
    },
    {
      "id": 4,
      "model_type": "LOGISTIC_REGRESSION",
      "version": "v1.0.0",
      "accuracy_metric": 0.8767,
      "r2_score": null,
      "mae": null,
      "rmse": null,
      "is_deployed": true,
      "training_samples": 2400,
      "last_training_date": "2026-04-30T02:00:00+02:00",
      "model_file_path": "ml_models/logistic/v1.0.0.pkl",
      "created_at": "2026-04-30T05:30:00+02:00"
    }
  ],
  "meta": { "count": 4, "next": null, "previous": null }
}
```

---

## GET /api/v1/predictions/models/{id}/

**Auth required:** ✅ Admin only

Get full details of a specific AI model version including all metrics and file paths.

### Response `200`

```json
{
  "success": true,
  "data": {
    "id": 1,
    "model_type": "CATBOOST",
    "version": "v1.0.0",
    "accuracy_metric": 0.9812,
    "r2_score": 0.9282,
    "mae": 0.0372,
    "rmse": 0.0479,
    "is_deployed": true,
    "training_data_source": "girinka_db — mortality_train.csv",
    "training_samples": 4000,
    "feature_columns": [
      "disease_cases", "vet_coverage_rate", "health_encoded",
      "health_feeding_interaction", "poverty_rate", "years_in_program",
      "feed_encoded", "reproduction_count", "water_access",
      "avg_temperature_c", "avg_rainfall_mm", "breed",
      "ubudehe_category", "days_since_last_vet_visit",
      "lactation_number", "climate_poverty_risk", "days_since_vet_normalized"
    ],
    "model_file_path": "ml_models/catboost/v1.0.0.cbm",
    "scaler_file_path": null,
    "last_training_date": "2026-04-30T02:00:00+02:00",
    "created_at": "2026-04-30T04:00:00+02:00"
  }
}
```

---

## POST /api/v1/predictions/models/{id}/deploy/

**Auth required:** ✅ Admin only

Deploy a specific model version as the active model. Automatically deactivates the currently deployed model of the same type. Only one model per type can be deployed at a time.

### Request Body

None — just `POST` to the URL.

### Response `200`

```json
{
  "success": true,
  "data": {
    "detail": "CATBOOST v1.1.0 deployed."
  }
}
```

### Response `404` — Model not found

```json
{
  "success": false,
  "message": "Not found."
}
```

---

## GET /api/v1/predictions/models/performance/

**Auth required:** ✅ Admin only

Returns accuracy metrics for all currently deployed models — useful for monitoring model quality over time.

### Response `200`

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "model_type": "CATBOOST",
      "version": "v1.0.0",
      "is_deployed": true,
      "r2_score": 0.9282,
      "mae": 0.0372,
      "rmse": 0.0479,
      "accuracy_metric": 0.9812,
      "training_samples": 4000,
      "last_training_date": "2026-04-30T02:00:00+02:00"
    },
    {
      "id": 2,
      "model_type": "LSTM",
      "version": "v1.0.0",
      "is_deployed": true,
      "mae": 0.0776,
      "rmse": 0.0940,
      "training_samples": 13440,
      "last_training_date": "2026-04-30T02:00:00+02:00"
    },
    {
      "id": 3,
      "model_type": "RANDOM_FOREST",
      "version": "v1.0.0",
      "is_deployed": true,
      "accuracy_metric": 0.9639,
      "training_samples": 2418,
      "last_training_date": "2026-04-30T02:00:00+02:00"
    },
    {
      "id": 4,
      "model_type": "LOGISTIC_REGRESSION",
      "version": "v1.0.0",
      "is_deployed": true,
      "accuracy_metric": 0.8767,
      "training_samples": 2400,
      "last_training_date": "2026-04-30T02:00:00+02:00"
    }
  ]
}
```

---

## POST /api/v1/predictions/models/retrain/

**Auth required:** ✅ Admin only

Queues a full ML model retrain pipeline on the ML service. The job runs asynchronously via Celery and calls `POST /retrain` on the FastAPI service which:

1. Regenerates training datasets
2. Retrains all 4 models
3. Evaluates new models against current ones
4. Deploys new versions if accuracy improves
5. Sends admin email notification when complete

### Request Body

None

### Response `202` — Queued

```json
{
  "success": true,
  "data": {
    "detail": "Retrain pipeline queued."
  }
}
```

> ℹ️ This also runs automatically on the **1st of every month at 02:00 AM** via Celery Beat.

---

## GET /api/v1/predictions/models/health_check/

**Auth required:** ✅ Admin only

Checks if the Girinka ML FastAPI service is reachable and all 4 models are loaded and ready to serve predictions.

### Response `200` — All healthy

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

### Response `503` — ML service down or degraded

```json
{
  "success": false,
  "data": {
    "status": "down",
    "error": "Connection refused — ML service at https://girinka-pulse-ml.onrender.com is not responding"
  }
}
```

### Response `200` — Degraded (some models failed to load)

```json
{
  "success": true,
  "data": {
    "status": "degraded",
    "models": {
      "catboost": true,
      "lstm": false,
      "random_forest": true,
      "logistic": true
    }
  }
}
```

---

## Also Triggered Automatically — Celery Background Tasks

These three Celery scheduled tasks run predictions **without a user hitting an endpoint:**

### `run_daily_risk_assessment`
**Schedule:** Every day at **06:30 AM**
**ML call:** `POST /predict/mortality` — for every living cow in the system

Runs the CatBoost mortality check on all active cows. Creates alerts and sends emails automatically.

### `run_daily_milk_forecasts`
**Schedule:** Every day at **06:00 AM**
**ML call:** `POST /predict/milk` — for every cow with ≥7 days of milk records

Forecasts milk yield for the week ahead. Creates LOW_MILK alerts if avg < 5 L/day.

### `monthly_model_retrain`
**Schedule:** 1st of every month at **02:00 AM**
**ML call:** `POST /retrain` — triggers full retraining pipeline

---

## Quick Reference

| Endpoint | Method | ML Model | Min Role |
|----------|--------|----------|----------|
| `/predictions/mortality/` | `POST` | CatBoost M1 | Cell Leader |
| `/predictions/milk/` | `POST` | LSTM M2 | Any |
| `/predictions/disease/` | `POST` | Random Forest M3 | Veterinarian |
| `/predictions/passon/` | `POST` | Logistic Regression M4 | Cell Leader |
| `/predictions/history/` | `GET` | — | Cell Leader |
| `/predictions/history/{id}/` | `GET` | — | Cell Leader |
| `/predictions/models/` | `GET` | — | Admin |
| `/predictions/models/{id}/` | `GET` | — | Admin |
| `/predictions/models/{id}/deploy/` | `POST` | — | Admin |
| `/predictions/models/performance/` | `GET` | — | Admin |
| `/predictions/models/retrain/` | `POST` | All 4 | Admin |
| `/predictions/models/health_check/` | `GET` | — | Admin |

---

*Girinka Pulse API · University of Rwanda · 2026*
*UMUTESI Kelia · MUGISHA Joseph · MUGISHA Philippe*
