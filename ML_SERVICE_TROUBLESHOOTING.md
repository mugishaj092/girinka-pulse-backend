# 🔧 ML Service Configuration & Troubleshooting

## SSL Error Fix

If you encounter this error:
```
[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)
```

This means the ML service at `https://girinka-pulse-ml.onrender.com` is either:
1. Down or unreachable
2. Has SSL certificate issues
3. Requires specific SSL configuration

---

## ✅ Solution: Use Mock ML Client

The system now includes a **Mock ML Client** that generates fake predictions for testing without needing the real ML service.

### Enable Mock Client

Add this to your `.env` file:
```env
USE_MOCK_ML_CLIENT=True
```

Then restart Docker:
```bash
docker-compose restart django celery-worker
```

### What the Mock Client Does

The mock client generates realistic fake predictions:

1. **Mortality Risk** - Random risk scores (0.1-0.9) with appropriate severity levels
2. **Milk Forecast** - 7-day predictions based on recent averages with variation
3. **Disease Detection** - Random probabilities for 7 disease types
4. **Birth Prediction** - Random success probabilities (0.25-0.95)

All predictions are **deterministic** (same cow_id = same prediction) for consistent testing.

---

## 🔄 Switch Between Real and Mock

### Use Mock Client (Development/Testing)
```env
USE_MOCK_ML_CLIENT=True
```

### Use Real ML Service (Production)
```env
USE_MOCK_ML_CLIENT=False
ML_SERVICE_URL=https://girinka-pulse-ml.onrender.com
```

---

## 🧪 Test ML Predictions

### Test Mortality Prediction
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "cell_leader", "password": "cell123"}'

# Run prediction
curl -X POST http://localhost:8000/api/v1/predictions/mortality/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cow_id": 1}'
```

**Expected Response (Mock):**
```json
{
  "success": true,
  "data": {
    "cow_id": 1,
    "mortality_risk_score": 0.72,
    "risk_level": "VERY_HIGH",
    "alert_triggered": true,
    "alert_severity": "URGENT",
    "recommended_action": "🔴 CRITICAL: Urgent vet consultation within 12 hours...",
    "model_version": "mock-v1.0"
  }
}
```

### Test Milk Forecast
```bash
curl -X POST http://localhost:8000/api/v1/predictions/milk/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cow_id": 1}'
```

**Expected Response (Mock):**
```json
{
  "success": true,
  "data": {
    "cow_id": 1,
    "forecast_days": 7,
    "predictions": [
      {"day": 1, "predicted_yield_litres": 11.2},
      {"day": 2, "predicted_yield_litres": 10.8},
      ...
    ],
    "avg_predicted_yield_litres": 10.5,
    "model_version": "mock-lstm-v1.0"
  }
}
```

---

## 🔍 Check Which Client Is Active

Look at Django logs on startup:
```bash
docker logs girinka-api | grep "ML Client"
```

**Mock Client:**
```
🟡 Using MOCK ML Client - predictions are fake for testing!
```

**Real Client:**
```
✅ Using real ML Client at https://girinka-pulse-ml.onrender.com
```

---

## 🛠️ Fix Real ML Service SSL Issues

If you want to use the real ML service but have SSL issues:

### Option 1: Disable SSL Verification (Development Only)
The code already includes `verify=False` in httpx requests to bypass SSL verification.

### Option 2: Update ML Service URL
If the service moved to a different URL:
```env
ML_SERVICE_URL=https://new-ml-service-url.com
```

### Option 3: Add API Key (If Required)
```env
ML_SERVICE_API_KEY=your-api-key-here
```

### Option 4: Use Local ML Service
Run the ML service locally:
```env
ML_SERVICE_URL=http://localhost:8001
USE_MOCK_ML_CLIENT=False
```

---

## 📊 Mock vs Real Predictions

| Feature | Mock Client | Real ML Service |
|---------|------------|-----------------|
| **Speed** | Instant | 1-5 seconds |
| **Accuracy** | Random (fake) | Trained AI models |
| **Availability** | Always available | Depends on service uptime |
| **Cost** | Free | May have API costs |
| **Use Case** | Development/Testing | Production |
| **SSL Issues** | None | May occur |

---

## 🚀 Production Deployment

For production, you should:

1. **Use Real ML Service**
   ```env
   USE_MOCK_ML_CLIENT=False
   ```

2. **Fix SSL Certificates**
   - Ensure ML service has valid SSL certificate
   - Or use internal network without SSL

3. **Add API Authentication**
   ```env
   ML_SERVICE_API_KEY=production-api-key
   ```

4. **Monitor ML Service Health**
   ```bash
   curl http://localhost:8000/api/v1/predictions/models/health_check/
   ```

5. **Set Proper Timeout**
   ```python
   # In settings/production.py
   ML_SERVICE_TIMEOUT = 60  # Increase for production
   ```

---

## 🔔 Notifications Still Work

Even with the mock ML client:
- ✅ Alerts are created based on mock predictions
- ✅ Email notifications are sent via Resend
- ✅ In-app notifications appear in the web interface
- ✅ All workflows function normally

The only difference is the predictions are fake, not from trained AI models.

---

## 📝 Summary

**Problem:** SSL error when connecting to ML service

**Quick Fix:** Enable mock client
```env
USE_MOCK_ML_CLIENT=True
```

**Long-term Fix:** 
- Fix SSL certificates on ML service
- Or use internal network
- Or run ML service locally

**Testing:** Mock client is perfect for development and testing

**Production:** Use real ML service with proper SSL configuration

---

**Last Updated:** May 2026  
**System:** Girinka Pulse Backend API
