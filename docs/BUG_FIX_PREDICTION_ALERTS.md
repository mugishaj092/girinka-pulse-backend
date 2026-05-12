# Bug Fix: Disease and Birth Predictions Now Create Alerts

## Issue
Disease and birth prediction endpoints were not creating `Alert` records or sending notifications, unlike the mortality prediction endpoint which correctly created alerts and sent emails.

## Root Cause
The `DiseasePredictionView` and `BirthPredictionView` were calling `ml_client` directly instead of going through `PredictionService`, which handles alert creation and email dispatch.

## Solution

### 1. Added `run_disease_check()` to PredictionService

**File:** `features/predictions/services.py`

This method:
- Calls the ML service via `ml_client.predict_disease()`
- Logs the prediction to `PredictionLog`
- Loops through `triggered_alerts` in the ML response
- Creates an `Alert` record for each triggered disease with:
  - `alert_type` = `DISEASE_OUTBREAK`
  - `severity` mapped from probability and emergency flag:
    - `emergency: true` → `CRITICAL`
    - `probability >= 0.75` → `URGENT`
    - `probability >= 0.50` → `WARNING`
    - otherwise → `INFO`
  - `message` = `"Disease prediction: {disease} ({probability}% probability)"`
  - `recommendation` = from ML service response
  - `risk_score` = disease probability
- Creates in-app `Notification` records for district vets and cell leaders
- Sends email via Resend if `emergency: true` (FMD or Brucellosis)
- Adds `alert_triggered` and `alert_severity` fields to the response

### 2. Added `run_birth_check()` to PredictionService

**File:** `features/predictions/services.py`

This method:
- Calls the ML service via `ml_client.predict_birth()`
- Logs the prediction to `PredictionLog`
- Creates an `Alert` record if birth success probability < 0.50 with:
  - `alert_type` = `PASS_ON_DUE` (birth-related)
  - `severity` mapped from probability:
    - `probability < 0.30` → `CRITICAL`
    - `probability < 0.40` → `URGENT`
    - `probability < 0.50` → `WARNING`
  - `message` = `"High-risk birth detected: {prognosis} ({probability}% success probability)"`
  - `recommendation` = from ML service response
  - `risk_score` = `1.0 - probability` (inverted to show risk, not success)
- Creates in-app `Notification` for cell leader
- Sends email via Resend if probability < 0.40 (critical cases)
- Adds `alert_triggered` and `alert_severity` fields to the response

### 3. Updated Views to Use PredictionService

**File:** `features/predictions/views.py`

- `DiseasePredictionView.post()` now calls `PredictionService.run_disease_check(cow, request.data)`
- `BirthPredictionView.post()` now calls `PredictionService.run_birth_check(cow, request.data)`
- Both views now extract `cow_id` from request and fetch the `Cow` object before calling the service

### 4. Updated OpenAPI Schema

**File:** `features/predictions/views.py`

Added `alert_triggered` and `alert_severity` fields to response examples:

**Disease prediction response:**
```json
{
  "cow_id": 12,
  "top_prediction": "FMD",
  "top_probability": 0.9708,
  "triggered_alerts": [...],
  "emergency": true,
  "alert_triggered": true,
  "alert_severity": "CRITICAL",
  "model_version": "v1.0.0"
}
```

**Birth prediction response:**
```json
{
  "cow_id": 18,
  "birth_success_probability": 0.31,
  "prognosis_label": "High Risk",
  "alert_triggered": true,
  "alert_severity": "CRITICAL",
  "model_version": "v1.0.0"
}
```

### 5. Added Comprehensive Tests

**File:** `tests/test_prediction_alerts.py`

Created 7 test cases:
- `test_disease_prediction_creates_alert_on_emergency` — FMD creates CRITICAL alert
- `test_disease_prediction_creates_urgent_alert_high_probability` — High probability creates URGENT alert
- `test_disease_prediction_no_alert_below_threshold` — No alert when no diseases triggered
- `test_birth_prediction_creates_critical_alert_very_low_probability` — <0.30 creates CRITICAL alert
- `test_birth_prediction_creates_urgent_alert_low_probability` — 0.30-0.40 creates URGENT alert
- `test_birth_prediction_creates_warning_alert_moderate_risk` — 0.40-0.50 creates WARNING alert
- `test_birth_prediction_no_alert_high_success_probability` — ≥0.50 creates no alert

## Alert Severity Mapping

### Disease Predictions
| Condition | Severity |
|-----------|----------|
| `emergency: true` (FMD, Brucellosis) | `CRITICAL` |
| `probability >= 0.75` | `URGENT` |
| `probability >= 0.50` | `WARNING` |
| `probability < 0.50` | `INFO` |

### Birth Predictions
| Birth Success Probability | Severity |
|---------------------------|----------|
| `< 0.30` | `CRITICAL` |
| `0.30 - 0.39` | `URGENT` |
| `0.40 - 0.49` | `WARNING` |
| `>= 0.50` | No alert |

## Email Notifications

- **Disease:** Email sent if `emergency: true` (FMD or Brucellosis detected)
- **Birth:** Email sent if probability < 0.40 (critical risk)
- All emails sent via Resend to the beneficiary's email address

## In-App Notifications

- **Disease:** Notifications created for district vets and cell leaders
- **Birth:** Notifications created for cell leaders

## Files Changed

1. `features/predictions/services.py` — Added `run_disease_check()` and `run_birth_check()` methods
2. `features/predictions/views.py` — Updated `DiseasePredictionView` and `BirthPredictionView` to use service methods
3. `tests/test_prediction_alerts.py` — New test file with 7 test cases
4. `context/tasks.md` — Updated Task 11 to reflect the fix

## Verification

Run the new tests:
```bash
pytest tests/test_prediction_alerts.py -v
```

Expected output: 7 tests pass, zero failures.

## Consistency Achieved

All 4 prediction endpoints now follow the same pattern:
1. Call ML service via `PredictionService`
2. Log prediction to `PredictionLog`
3. Create `Alert` records when thresholds are exceeded
4. Create in-app `Notification` records
5. Send email alerts for critical cases
6. Return response with `alert_triggered` and `alert_severity` fields
