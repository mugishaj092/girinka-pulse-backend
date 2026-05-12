# Frontend Integration Guide: Prediction Alerts Update

## Overview

The backend now returns **consistent alert metadata** for all 4 prediction endpoints. Previously, only mortality predictions included `alert_triggered` and `alert_severity` fields. Now **disease** and **birth** predictions also return these fields.

---

## API Response Changes

### Before (Disease & Birth)

**Disease prediction response:**
```json
{
  "cow_id": 12,
  "top_prediction": "FMD",
  "top_probability": 0.9708,
  "triggered_alerts": [...],
  "emergency": true,
  "model_version": "v1.0.0"
}
```

**Birth prediction response:**
```json
{
  "cow_id": 18,
  "birth_success_probability": 0.31,
  "prognosis_label": "High Risk",
  "pass_on_eligible": false,
  "model_version": "v1.0.0"
}
```

### After (Disease & Birth)

**Disease prediction response:**
```json
{
  "cow_id": 12,
  "top_prediction": "FMD",
  "top_probability": 0.9708,
  "triggered_alerts": [...],
  "emergency": true,
  "alert_triggered": true,        // ✅ NEW
  "alert_severity": "CRITICAL",   // ✅ NEW
  "model_version": "v1.0.0"
}
```

**Birth prediction response:**
```json
{
  "cow_id": 18,
  "birth_success_probability": 0.31,
  "prognosis_label": "High Risk",
  "pass_on_eligible": false,
  "alert_triggered": true,        // ✅ NEW
  "alert_severity": "CRITICAL",   // ✅ NEW
  "model_version": "v1.0.0"
}
```

---

## Frontend Changes Required

### 1. Update TypeScript Types

**File:** `types/predictions.ts` (or wherever you define prediction types)

```typescript
// Disease prediction response
export interface DiseasePredictionResponse {
  cow_id: number;
  top_prediction: string;
  top_probability: number;
  all_disease_probabilities: Record<string, number>;
  triggered_alerts: Array<{
    disease: string;
    probability: number;
    threshold_used: number;
    alert_triggered: boolean;
    recommended_action: string;
  }>;
  emergency: boolean;
  total_symptoms_observed: number;
  alert_triggered: boolean;      // ✅ ADD THIS
  alert_severity: AlertSeverity; // ✅ ADD THIS
  model_version: string;
}

// Birth prediction response
export interface BirthPredictionResponse {
  cow_id: number;
  birth_success_probability: number;
  prognosis_label: string;
  pass_on_eligible: boolean;
  recommended_action: string;
  alert_triggered: boolean;      // ✅ ADD THIS
  alert_severity: AlertSeverity; // ✅ ADD THIS
  model_version: string;
}

// Alert severity enum
export type AlertSeverity = "INFO" | "WARNING" | "URGENT" | "CRITICAL" | "NONE";
```

---

### 2. Update Disease Prediction UI Component

**File:** `components/predictions/DiseasePredictionResult.tsx` (or similar)

**Add alert badge/indicator after prediction result:**

```tsx
import { AlertTriangle, AlertCircle, Info } from "lucide-react";

export function DiseasePredictionResult({ result }: { result: DiseasePredictionResponse }) {
  return (
    <div className="space-y-4">
      {/* Existing disease prediction display */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">
          Top Prediction: {result.top_prediction}
        </h3>
        <span className="text-2xl font-bold">
          {(result.top_probability * 100).toFixed(1)}%
        </span>
      </div>

      {/* ✅ ADD THIS: Alert indicator */}
      {result.alert_triggered && (
        <div className={`
          flex items-center gap-2 p-3 rounded-lg border
          ${result.alert_severity === "CRITICAL" ? "bg-red-50 border-red-200 text-red-800" : ""}
          ${result.alert_severity === "URGENT" ? "bg-orange-50 border-orange-200 text-orange-800" : ""}
          ${result.alert_severity === "WARNING" ? "bg-yellow-50 border-yellow-200 text-yellow-800" : ""}
          ${result.alert_severity === "INFO" ? "bg-blue-50 border-blue-200 text-blue-800" : ""}
        `}>
          {result.alert_severity === "CRITICAL" && <AlertTriangle className="h-5 w-5" />}
          {result.alert_severity === "URGENT" && <AlertCircle className="h-5 w-5" />}
          {result.alert_severity === "WARNING" && <AlertCircle className="h-5 w-5" />}
          {result.alert_severity === "INFO" && <Info className="h-5 w-5" />}
          
          <div className="flex-1">
            <p className="font-semibold">
              {result.alert_severity} Alert Created
            </p>
            <p className="text-sm">
              {result.emergency 
                ? "Emergency alert sent to district vet and cell leader via email."
                : "Alert created and notifications sent to relevant staff."}
            </p>
          </div>
        </div>
      )}

      {/* Existing triggered alerts display */}
      {result.triggered_alerts.map((alert, idx) => (
        <div key={idx} className="border-l-4 border-red-500 pl-4">
          <p className="font-medium">{alert.disease}</p>
          <p className="text-sm text-gray-600">{alert.recommended_action}</p>
        </div>
      ))}
    </div>
  );
}
```

---

### 3. Update Birth Prediction UI Component

**File:** `components/predictions/BirthPredictionResult.tsx` (or similar)

**Add alert badge/indicator for high-risk births:**

```tsx
export function BirthPredictionResult({ result }: { result: BirthPredictionResponse }) {
  return (
    <div className="space-y-4">
      {/* Existing birth prediction display */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">
          Prognosis: {result.prognosis_label}
        </h3>
        <span className="text-2xl font-bold">
          {(result.birth_success_probability * 100).toFixed(1)}%
        </span>
      </div>

      {/* ✅ ADD THIS: Alert indicator for high-risk births */}
      {result.alert_triggered && (
        <div className={`
          flex items-center gap-2 p-3 rounded-lg border
          ${result.alert_severity === "CRITICAL" ? "bg-red-50 border-red-200 text-red-800" : ""}
          ${result.alert_severity === "URGENT" ? "bg-orange-50 border-orange-200 text-orange-800" : ""}
          ${result.alert_severity === "WARNING" ? "bg-yellow-50 border-yellow-200 text-yellow-800" : ""}
        `}>
          <AlertTriangle className="h-5 w-5" />
          
          <div className="flex-1">
            <p className="font-semibold">
              High-Risk Birth Alert Created
            </p>
            <p className="text-sm">
              {result.birth_success_probability < 0.40
                ? "Critical alert sent to cell leader via email. Immediate vet intervention required."
                : "Alert created and cell leader notified. Pre-birth vet exam recommended."}
            </p>
          </div>
        </div>
      )}

      {/* Existing recommendation display */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <p className="text-sm font-medium text-gray-700">Recommended Action:</p>
        <p className="text-sm text-gray-600 mt-1">{result.recommended_action}</p>
      </div>

      {/* Pass-on eligibility badge */}
      {result.pass_on_eligible && (
        <div className="bg-green-50 border border-green-200 text-green-800 p-3 rounded-lg">
          <p className="font-semibold">✅ Pass-On Eligible</p>
          <p className="text-sm">Calf will be auto-flagged for Pass-On program after birth.</p>
        </div>
      )}
    </div>
  );
}
```

---

### 4. Add Toast Notification on Alert Creation

**File:** `hooks/usePredictions.ts` or your prediction API hook

```typescript
import { toast } from "sonner"; // or your toast library

export function useDiseasePrediction() {
  const mutation = useMutation({
    mutationFn: (payload: DiseasePredictionPayload) => 
      api.post("/predictions/disease/", payload),
    onSuccess: (data) => {
      // ✅ ADD THIS: Show toast when alert is created
      if (data.alert_triggered) {
        const severityConfig = {
          CRITICAL: { icon: "🚨", color: "destructive" },
          URGENT: { icon: "⚠️", color: "warning" },
          WARNING: { icon: "⚡", color: "default" },
          INFO: { icon: "ℹ️", color: "default" },
        };
        
        const config = severityConfig[data.alert_severity] || severityConfig.INFO;
        
        toast.success(`${config.icon} ${data.alert_severity} Alert Created`, {
          description: data.emergency 
            ? "Emergency alert sent to district vet and cell leader."
            : "Alert created and notifications sent to relevant staff.",
        });
      }
    },
  });
  
  return mutation;
}

export function useBirthPrediction() {
  const mutation = useMutation({
    mutationFn: (payload: BirthPredictionPayload) => 
      api.post("/predictions/passon/", payload),
    onSuccess: (data) => {
      // ✅ ADD THIS: Show toast when alert is created
      if (data.alert_triggered) {
        toast.warning(`⚠️ High-Risk Birth Alert Created`, {
          description: data.birth_success_probability < 0.40
            ? "Critical alert sent to cell leader via email."
            : "Alert created and cell leader notified.",
        });
      }
    },
  });
  
  return mutation;
}
```

---

### 5. Update Alert List to Show New Alert Types

**File:** `components/alerts/AlertList.tsx` or your alerts dashboard

**Ensure disease and birth alerts are displayed correctly:**

```tsx
export function AlertList() {
  const { data: alerts } = useQuery({
    queryKey: ["alerts"],
    queryFn: () => api.get("/alerts/"),
  });

  return (
    <div className="space-y-2">
      {alerts?.map((alert) => (
        <AlertCard key={alert.id} alert={alert} />
      ))}
    </div>
  );
}

function AlertCard({ alert }: { alert: Alert }) {
  // ✅ ADD ICONS FOR NEW ALERT TYPES
  const alertIcons = {
    MORTALITY_RISK: "💀",
    LOW_MILK: "🥛",
    DISEASE_OUTBREAK: "🦠",  // ✅ NEW
    WEATHER_RISK: "🌧️",
    VET_VISIT_DUE: "🩺",
    PASS_ON_DUE: "🐄",       // ✅ USED FOR BIRTH ALERTS
  };

  return (
    <div className={`border-l-4 p-4 ${getSeverityColor(alert.severity)}`}>
      <div className="flex items-start gap-3">
        <span className="text-2xl">{alertIcons[alert.alert_type]}</span>
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <h4 className="font-semibold">{alert.alert_type.replace(/_/g, " ")}</h4>
            <span className="text-xs font-medium">{alert.severity}</span>
          </div>
          <p className="text-sm text-gray-600 mt-1">{alert.message}</p>
          {alert.recommendation && (
            <p className="text-sm text-gray-500 mt-2 italic">{alert.recommendation}</p>
          )}
        </div>
      </div>
    </div>
  );
}
```

---

### 6. Optional: Add Alert Count Badge to Navbar

**File:** `components/layout/Navbar.tsx`

```tsx
export function Navbar() {
  const { data: alertCount } = useQuery({
    queryKey: ["alerts", "unread-count"],
    queryFn: () => api.get("/alerts/unread_count/"),
    refetchInterval: 30000, // Poll every 30 seconds
  });

  return (
    <nav>
      {/* ... other nav items ... */}
      
      <Link href="/alerts" className="relative">
        <Bell className="h-5 w-5" />
        {alertCount?.count > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
            {alertCount.count}
          </span>
        )}
      </Link>
    </nav>
  );
}
```

---

## Testing Checklist

After making these changes, test the following scenarios:

### Disease Predictions
- [ ] Run disease prediction with FMD symptoms (emergency case)
- [ ] Verify `alert_triggered: true` and `alert_severity: "CRITICAL"` in response
- [ ] Verify alert badge appears in UI with red styling
- [ ] Verify toast notification appears
- [ ] Check `/alerts` page shows new DISEASE_OUTBREAK alert
- [ ] Verify email was sent (check backend logs or Resend dashboard)

### Birth Predictions
- [ ] Run birth prediction with low success probability (< 0.30)
- [ ] Verify `alert_triggered: true` and `alert_severity: "CRITICAL"` in response
- [ ] Verify alert badge appears in UI with red styling
- [ ] Verify toast notification appears
- [ ] Check `/alerts` page shows new PASS_ON_DUE alert
- [ ] Run birth prediction with high success probability (> 0.50)
- [ ] Verify `alert_triggered: false` and no alert badge appears

### Alerts Dashboard
- [ ] Verify disease alerts show 🦠 icon
- [ ] Verify birth alerts show 🐄 icon
- [ ] Verify severity colors match (CRITICAL=red, URGENT=orange, WARNING=yellow)
- [ ] Verify alert count badge in navbar updates in real-time

---

## Summary of Changes

| Component | Change Required | Priority |
|-----------|----------------|----------|
| TypeScript types | Add `alert_triggered` and `alert_severity` fields | **Required** |
| Disease prediction UI | Add alert badge/indicator | **Required** |
| Birth prediction UI | Add alert badge/indicator | **Required** |
| Toast notifications | Show toast on alert creation | Recommended |
| Alert list | Add icons for DISEASE_OUTBREAK and PASS_ON_DUE | Recommended |
| Navbar | Add real-time alert count badge | Optional |

---

## API Endpoints Reference

All prediction endpoints now return consistent alert metadata:

```bash
# Disease prediction
POST /api/v1/predictions/disease/
Response: { ..., "alert_triggered": true, "alert_severity": "CRITICAL" }

# Birth prediction
POST /api/v1/predictions/passon/
Response: { ..., "alert_triggered": true, "alert_severity": "URGENT" }

# Mortality prediction (unchanged)
POST /api/v1/predictions/mortality/
Response: { ..., "alert_triggered": true, "alert_severity": "URGENT" }

# Milk forecast (unchanged)
POST /api/v1/predictions/milk/
Response: { ..., "forecasts": [...] }
```

---

## Questions?

If you encounter any issues or need clarification:
1. Check the backend API docs at `http://localhost:8000/api/v1/docs/`
2. Review the bug fix documentation at `docs/BUG_FIX_PREDICTION_ALERTS.md`
3. Run backend tests: `pytest tests/test_prediction_alerts.py -v`
