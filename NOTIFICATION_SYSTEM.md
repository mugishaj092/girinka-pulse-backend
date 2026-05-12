# 📧 Girinka Pulse Notification System

## Overview
The Girinka Pulse system sends **email notifications** via **Resend** (no SMS) to farmers, cell leaders, veterinarians, and administrators when specific events occur.

---

## 🎯 When Notifications Are Sent

### 1. **Mortality Risk Alerts** 🚨

**Trigger:** AI detects high mortality risk (score ≥ 0.60)

**When:**
- **Daily at 6:30 AM** - Automated daily risk assessment runs for all living cows
- **On-demand** - When cell leader/vet manually triggers prediction via API

**Recipients:**
- ✉️ **Farmer** (cow owner) - Gets email alert

**Email Content:**
- Cow tag number
- Risk score and level (HIGH, VERY_HIGH, EMERGENCY)
- Alert message
- Recommended action (e.g., "Schedule veterinary checkup within 48 hours")

**Severity Levels:**
- `EMERGENCY` (score ≥ 0.85) → Red alert
- `VERY_HIGH` (score ≥ 0.70) → Critical alert
- `HIGH` (score ≥ 0.60) → Urgent alert
- `MEDIUM` (score 0.40-0.59) → Warning (no email)
- `LOW` (score < 0.40) → Info (no email)

---

### 2. **Low Milk Production Alerts** 🥛

**Trigger:** 7-day milk forecast shows average < 5 liters/day

**When:**
- **Daily at 6:00 AM** - Automated milk forecasts run for all cows with 7+ days of records
- **On-demand** - When user requests milk forecast via API

**Recipients:**
- ✉️ **Farmer** (cow owner) - Gets email alert

**Email Content:**
- Cow tag number
- Predicted average daily yield
- Alert message: "7-day avg milk forecast: X.XX L/day — below 5L threshold"
- Recommendation: "Review feed quantity and consult your vet"

---

### 3. **Disease Risk Alerts** 🦠

**Trigger:** AI detects high disease probability

**When:**
- **On-demand only** - When vet/cell leader runs disease prediction via API

**Recipients:**
- ✉️ **Farmer** - Gets email if emergency (probability ≥ 75% or emergency flag)
- 🔔 **Veterinarian** - Gets in-app notification
- 🔔 **Cell Leader** - Gets in-app notification

**Email Content:**
- Cow tag number
- Disease name (FMD, ECF, Mastitis, Lumpy Skin, Brucellosis, Anthrax, Trypanosomiasis)
- Probability percentage
- Recommended action

**Severity Levels:**
- `CRITICAL` - Emergency cases (email sent)
- `URGENT` - Probability ≥ 75% (email sent)
- `WARNING` - Probability 50-74% (in-app only)
- `INFO` - Probability < 50% (in-app only)

---

### 4. **High-Risk Birth Alerts** 🐄

**Trigger:** Birth success probability < 50%

**When:**
- **On-demand only** - When cell leader runs birth prediction for pregnant cow

**Recipients:**
- ✉️ **Farmer** - Gets email if probability < 40%
- 🔔 **Cell Leader** - Gets in-app notification

**Email Content:**
- Cow tag number
- Birth success probability
- Prognosis (e.g., "High Risk", "Very High Risk")
- Recommendation: "Pre-birth vet exam recommended"

**Severity Levels:**
- `CRITICAL` - Probability < 30% (email sent)
- `URGENT` - Probability 30-39% (email sent)
- `WARNING` - Probability 40-49% (in-app only)

---

### 5. **Password Reset OTP** 🔐

**Trigger:** User requests password reset

**When:**
- **Immediately** - When user submits password reset request via API

**Recipients:**
- ✉️ **Requesting User** - Gets 6-digit OTP code

**Email Content:**
- User's full name
- 6-digit OTP code (large, bold)
- Expiry notice: "This code expires in 10 minutes"

---

### 6. **Weekly District Reports** 📊

**Trigger:** Scheduled report generation

**When:**
- **Every Monday at 8:00 AM** - Automated weekly reports

**Recipients:**
- ✉️ **District Leaders** - One report per district
- ✉️ **Cell Leaders** - For their district

**Email Content:**
- Report type and period
- Summary statistics table:
  - Total cows
  - At-risk cows
  - Unresolved alerts
  - Average milk yield
  - Total beneficiaries
- Download link (Cloudinary signed URL)

---

### 7. **National Monthly Reports** 📈

**Trigger:** Scheduled national report generation

**When:**
- **Every Monday at 9:00 AM** - Automated national summary

**Recipients:**
- ✉️ **Admins** - System administrators
- ✉️ **MINAGRI/RAB Officials** - National program managers

**Email Content:**
- National statistics across all 30 districts
- Total program metrics
- Download link for full report

---

### 8. **Pass-On Transfer Certificates** 🔄

**Trigger:** Calf transfer completed

**When:**
- **Immediately** - When cell leader marks pass-on transfer as "COMPLETED"

**Recipients:**
- ✉️ **Donor Farmer** - Original cow owner
- ✉️ **Recipient Farmer** - New calf owner

**Email Content:**
- Transfer details (donor, recipient, calf)
- Transfer date
- Certificate download link (Cloudinary PDF)
- Official program seal

---

## 📅 Automated Schedule Summary

| Task | Schedule | What Happens | Notifications Sent |
|------|----------|--------------|-------------------|
| **Daily Weather Fetch** | 5:00 AM daily | Fetches weather data for all 30 districts | None |
| **Daily Milk Forecasts** | 6:00 AM daily | Runs LSTM forecast for all cows | ✉️ Farmers (if avg < 5L) |
| **Daily Risk Assessment** | 6:30 AM daily | Runs CatBoost mortality check on all cows | ✉️ Farmers (if score ≥ 0.60) |
| **Weekly District Reports** | Monday 8:00 AM | Generates district reports | ✉️ District/Cell Leaders |
| **Weekly National Report** | Monday 9:00 AM | Generates national summary | ✉️ Admins/MINAGRI |
| **Monthly Model Retrain** | 1st of month 2:00 AM | Triggers ML model retraining | None |
| **Cleanup Expired Tokens** | Midnight daily | Removes expired JWT tokens | None |
| **Archive Old Predictions** | Sunday 3:00 AM | Deletes prediction logs > 90 days | None |
| **Escalate Unresolved Alerts** | Every 6 hours | Escalates URGENT → CRITICAL if > 24h old | None |

---

## 👥 Notification Recipients by Role

### **Farmers** 🌾
- ✉️ Mortality risk alerts (score ≥ 0.60)
- ✉️ Low milk production alerts (< 5L/day)
- ✉️ Disease emergency alerts (probability ≥ 75%)
- ✉️ High-risk birth alerts (probability < 40%)
- ✉️ Pass-on transfer certificates

### **Cell Leaders** 👨‍💼
- ✉️ Weekly district reports
- 🔔 Disease risk notifications (in-app)
- 🔔 High-risk birth notifications (in-app)

### **Veterinarians** 🩺
- 🔔 Disease risk notifications (in-app)

### **District Leaders** 📊
- ✉️ Weekly district reports

### **Admins** 🔧
- ✉️ Weekly national reports
- ✉️ Monthly national reports

---

## 🔔 In-App Notifications vs Email

### **Email Notifications** (via Resend)
- High-priority alerts requiring immediate action
- Reports and certificates
- Password reset OTPs
- Sent to user's registered email address

### **In-App Notifications** (stored in database)
- Lower-priority alerts for awareness
- Disease risk notifications for vets/cell leaders
- Birth risk notifications for cell leaders
- Viewable in `/api/v1/notifications/` endpoint
- Can be marked as read

---

## 📧 Email Service Details

**Provider:** Resend (https://resend.com)

**From Address:** `Girinka Pulse <no-reply@mugishajoseph.me>`

**API Key:** Configured in `.env` as `RESEND_API_KEY`

**Email Templates:**
- Mortality risk alert (color-coded by severity)
- Low milk production alert
- Disease risk alert
- High-risk birth alert
- Password reset OTP
- Weekly/monthly reports
- Pass-on certificates

**No SMS:** The system does NOT send SMS notifications. All alerts are email + in-app only.

---

## 🛠️ How to Test Notifications

### 1. **Test Mortality Risk Alert**
```bash
# Trigger prediction for a cow
curl -X POST http://localhost:8000/api/v1/predictions/mortality/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cow_id": 1}'

# If risk score ≥ 0.60, farmer gets email
```

### 2. **Test Low Milk Alert**
```bash
# Trigger milk forecast
curl -X POST http://localhost:8000/api/v1/predictions/milk/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cow_id": 1}'

# If avg < 5L, farmer gets email
```

### 3. **Test Password Reset**
```bash
# Request password reset
curl -X POST http://localhost:8000/api/v1/auth/password/reset/ \
  -H "Content-Type: application/json" \
  -d '{"email": "farmer1@girinka.rw"}'

# User gets OTP email immediately
```

### 4. **Test Weekly Reports (Manual)**
```bash
# Trigger report generation
docker exec girinka-api python manage.py shell -c "
from features.reports.tasks import send_weekly_district_reports
send_weekly_district_reports()
"
```

### 5. **View In-App Notifications**
```bash
# Get all notifications for current user
curl http://localhost:8000/api/v1/notifications/ \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🔍 Monitoring Notifications

### **Check Email Logs**
```bash
# View Django logs
docker logs -f girinka-api | grep "Email sent"

# Check Resend dashboard
# https://resend.com/emails
```

### **Check Alert Creation**
```bash
# List all unresolved alerts
curl http://localhost:8000/api/v1/alerts/?is_resolved=false \
  -H "Authorization: Bearer $TOKEN"
```

### **Check Notification Logs**
```sql
-- In PostgreSQL
SELECT * FROM notification_logs 
WHERE sent_at > NOW() - INTERVAL '24 hours'
ORDER BY sent_at DESC;
```

---

## 📝 Notification Preferences

Users can configure their notification preferences via:

**Endpoint:** `GET/PATCH /api/v1/notifications/settings/`

**Configurable Options:**
- `email` - Enable/disable email notifications (default: true)
- `sms` - Enable/disable SMS (not implemented, always false)
- `in_app` - Enable/disable in-app notifications (default: true)
- `push` - Enable/disable push notifications (not implemented)
- `min_severity` - Minimum severity to receive (INFO, WARNING, URGENT, CRITICAL)

**Example:**
```json
{
  "email": true,
  "in_app": true,
  "min_severity": "WARNING"
}
```

This means user will only receive email/in-app notifications for WARNING, URGENT, and CRITICAL alerts.

---

## 🎯 Summary

**Total Notification Types:** 8
- 4 AI-triggered alerts (mortality, milk, disease, birth)
- 1 authentication (password reset)
- 2 reports (district, national)
- 1 certificate (pass-on transfer)

**Delivery Channels:**
- ✉️ Email (via Resend)
- 🔔 In-app (database notifications)
- ❌ SMS (not implemented)

**Automated Schedules:** 9 Celery Beat tasks

**Primary Recipients:**
- Farmers (cow owners)
- Cell Leaders
- Veterinarians
- District Leaders
- System Admins

---

**Last Updated:** May 2026
**System:** Girinka Pulse Backend API
**Email Provider:** Resend
