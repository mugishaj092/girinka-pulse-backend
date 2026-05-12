# Prompt for Frontend Developer

## Context
The Girinka Pulse backend has been updated to fix a bug where disease and birth predictions were not creating alerts. Now all 4 prediction endpoints (mortality, milk, disease, birth) consistently return alert metadata.

---

## What Changed

**Disease and birth prediction API responses now include two new fields:**

```typescript
{
  // ... existing fields ...
  "alert_triggered": boolean,      // NEW: true if an alert was created
  "alert_severity": "INFO" | "WARNING" | "URGENT" | "CRITICAL" | "NONE"  // NEW
}
```

---

## Your Task

Update the frontend to handle these new fields in the disease and birth prediction responses.

### Required Changes:

1. **Update TypeScript types** for `DiseasePredictionResponse` and `BirthPredictionResponse` to include:
   - `alert_triggered: boolean`
   - `alert_severity: "INFO" | "WARNING" | "URGENT" | "CRITICAL" | "NONE"`

2. **Add alert indicator UI** to disease prediction results:
   - Show a colored badge/banner when `alert_triggered === true`
   - Color based on severity: CRITICAL=red, URGENT=orange, WARNING=yellow, INFO=blue
   - Display message: "CRITICAL Alert Created - Emergency alert sent to district vet and cell leader via email"

3. **Add alert indicator UI** to birth prediction results:
   - Show a colored badge/banner when `alert_triggered === true`
   - Color based on severity (same as above)
   - Display message: "High-Risk Birth Alert Created - Alert sent to cell leader"

4. **Add toast notification** when predictions create alerts:
   - Show success/warning toast with severity icon
   - Example: "🚨 CRITICAL Alert Created - Emergency alert sent to district vet"

5. **Update alerts dashboard** to display new alert types:
   - `DISEASE_OUTBREAK` alerts (use 🦠 icon)
   - `PASS_ON_DUE` alerts for high-risk births (use 🐄 icon)

### Optional Enhancements:

- Add real-time alert count badge to navbar (poll `/api/v1/alerts/unread_count/` every 30 seconds)
- Add filter for alert types in alerts dashboard

---

## Example Response

**Disease prediction with alert:**
```json
{
  "cow_id": 12,
  "top_prediction": "FMD",
  "top_probability": 0.9708,
  "triggered_alerts": [{
    "disease": "FMD",
    "probability": 0.9708,
    "alert_triggered": true,
    "recommended_action": "Isolate cow immediately. Notify RAB and district vet."
  }],
  "emergency": true,
  "alert_triggered": true,
  "alert_severity": "CRITICAL",
  "model_version": "v1.0.0"
}
```

**Birth prediction with alert:**
```json
{
  "cow_id": 18,
  "birth_success_probability": 0.31,
  "prognosis_label": "High Risk",
  "pass_on_eligible": false,
  "recommended_action": "🔴 Urgent pre-birth vet exam required. Alert cell leader.",
  "alert_triggered": true,
  "alert_severity": "CRITICAL",
  "model_version": "v1.0.0"
}
```

---

## Alert Severity Rules

### Disease Predictions
- `emergency: true` (FMD or Brucellosis) → `CRITICAL`
- `probability >= 0.75` → `URGENT`
- `probability >= 0.50` → `WARNING`
- `probability < 0.50` → `INFO`

### Birth Predictions
- `probability < 0.30` → `CRITICAL`
- `probability 0.30-0.39` → `URGENT`
- `probability 0.40-0.49` → `WARNING`
- `probability >= 0.50` → No alert

---

## Testing

After implementing, test these scenarios:

1. **Disease prediction with FMD symptoms:**
   - POST to `/api/v1/predictions/disease/` with `fever: true, lameness: true, nasal_discharge: true`
   - Verify `alert_triggered: true` and `alert_severity: "CRITICAL"` in response
   - Verify red alert badge appears in UI
   - Verify toast notification shows
   - Check `/alerts` page for new DISEASE_OUTBREAK alert

2. **Birth prediction with low success:**
   - POST to `/api/v1/predictions/passon/` with `birth_success_probability: 0.25`
   - Verify `alert_triggered: true` and `alert_severity: "CRITICAL"` in response
   - Verify red alert badge appears in UI
   - Check `/alerts` page for new PASS_ON_DUE alert

3. **Birth prediction with high success:**
   - POST with `birth_success_probability: 0.92`
   - Verify `alert_triggered: false` and no alert badge appears

---

## Reference Documentation

Full implementation guide with code examples: `docs/FRONTEND_INTEGRATION_GUIDE.md`

API documentation: `http://localhost:8000/api/v1/docs/`

---

## Questions?

If anything is unclear, check:
1. `docs/FRONTEND_INTEGRATION_GUIDE.md` — detailed code examples
2. `docs/BUG_FIX_PREDICTION_ALERTS.md` — backend implementation details
3. Backend API docs at `/api/v1/docs/` — interactive examples
