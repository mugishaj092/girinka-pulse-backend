# 🔔 Girinka Pulse Web Notification System

## Overview
The Girinka Pulse system sends **in-app web notifications** (notification bell icon) to users when important events occur. These notifications appear in the web interface and can be accessed via the `/api/v1/notifications/` endpoint.

---

## 📱 When Web Notifications Are Sent

### 1. **Mortality Risk Alerts** 🚨

**Trigger:** AI detects mortality risk for a cow

**When:**
- **Daily at 6:30 AM** - Automated daily risk assessment
- **On-demand** - Manual prediction via API

**Recipients:**
- 🔔 **Farmer** (cow owner) - Always notified
- 🔔 **Cell Leaders** (district) - Notified if risk score ≥ 60%

**Notification Content:**
```
Title: 🚨 Mortality Risk Alert
Message: Your cow RW-KGL-001 has a 72% mortality risk (HIGH). 
         🔶 Urgent vet consultation within 24 hours. Monitor closely.
```

**For Cell Leaders (high risk only):**
```
Title: 🚨 High Mortality Risk in Your District
Message: Cow RW-KGL-001 (Owner: Jean Baptiste) has 72% mortality risk. 
         Immediate action required.
```

---

### 2. **Low Milk Production Alerts** 🥛

**Trigger:** 7-day milk forecast shows average < 5 liters/day

**When:**
- **Daily at 6:00 AM** - Automated milk forecasts
- **On-demand** - Manual forecast via API

**Recipients:**
- 🔔 **Farmer** (cow owner) - Always notified
- 🔔 **Cell Leaders** (district) - Always notified

**Notification Content:**
```
Title: 🥛 Low Milk Production Alert
Message: Your cow RW-KGL-001 is predicted to produce only 4.2L/day 
         over the next 7 days. Review feed quantity and consult your vet.
```

**For Cell Leaders:**
```
Title: 📉 Low Milk Production in Your District
Message: Cow RW-KGL-001 (Owner: Jean Baptiste) showing low milk forecast: 4.2L/day.
```

---

### 3. **Disease Risk Alerts** 🦠

**Trigger:** AI detects disease probability

**When:**
- **On-demand only** - When vet/cell leader runs disease prediction

**Recipients:**
- 🔔 **Veterinarians** (district) - Always notified
- 🔔 **Cell Leaders** (district) - Always notified
- ✉️ **Farmer** - Email only if emergency (≥75% probability)

**Notification Content:**
```
Title: 🦠 Disease Alert: Mastitis
Message: Cow RW-KGL-001 shows 82% probability of Mastitis. 
         Immediate attention required.
```

**Diseases Detected:**
- Foot and Mouth Disease (FMD)
- East Coast Fever (ECF)
- Mastitis
- Lumpy Skin Disease
- Brucellosis
- Anthrax
- Trypanosomiasis

---

### 4. **High-Risk Birth Alerts** 🐄

**Trigger:** Birth success probability < 50%

**When:**
- **On-demand only** - When cell leader runs birth prediction

**Recipients:**
- 🔔 **Cell Leaders** (district) - Always notified
- ✉️ **Farmer** - Email only if probability < 40%

**Notification Content:**
```
Title: ⚠️ High-Risk Birth: Very High Risk
Message: Cow RW-KGL-001 has 35% birth success probability. 
         Pre-birth vet exam recommended.
```

---

### 5. **Pass-On Transfer Approved** ✅

**Trigger:** Cell leader approves calf transfer

**When:**
- **Immediately** - When cell leader clicks "Approve"

**Recipients:**
- 🔔 **Donor Farmer** - Original cow owner
- 🔔 **Recipient Farmer** - New calf owner

**Notification Content:**

**For Donor:**
```
Title: ✅ Pass-On Transfer Approved
Message: Your calf transfer (RW-KGL-CALF-001) to Marie Claire has been 
         approved by the cell leader.
```

**For Recipient:**
```
Title: ✅ Pass-On Transfer Approved
Message: You have been approved to receive calf RW-KGL-CALF-001 from 
         Jean Baptiste. Transfer date: 2026-05-15.
```

---

### 6. **Pass-On Transfer Completed** 🎉

**Trigger:** Cell leader marks transfer as complete

**When:**
- **Immediately** - When cell leader clicks "Complete"

**Recipients:**
- 🔔 **Donor Farmer** - Original cow owner
- 🔔 **Recipient Farmer** - New calf owner

**Notification Content:**

**For Donor:**
```
Title: 🎉 Pass-On Transfer Completed
Message: Your calf RW-KGL-CALF-001 has been successfully transferred to 
         Marie Claire. Certificate will be sent via email.
```

**For Recipient:**
```
Title: 🎉 Welcome Your New Calf!
Message: Congratulations! You are now the owner of calf RW-KGL-CALF-001. 
         Certificate will be sent via email.
```

---

### 7. **Pass-On Transfer Rejected** ❌

**Trigger:** Cell leader rejects calf transfer

**When:**
- **Immediately** - When cell leader clicks "Reject"

**Recipients:**
- 🔔 **Donor Farmer** - Original cow owner
- 🔔 **Recipient Farmer** - New calf owner

**Notification Content:**

**For Both Parties:**
```
Title: ❌ Pass-On Transfer Rejected
Message: The calf transfer has been rejected. 
         Reason: Recipient household failed land verification check.
```

---

### 8. **Alert Resolved** ✅

**Trigger:** Cell leader/vet resolves an alert

**When:**
- **Immediately** - When alert is marked as resolved

**Recipients:**
- 🔔 **Farmer** (cow owner) - Always notified

**Notification Content:**
```
Title: ✅ Alert Resolved: Mortality Risk
Message: Your alert for cow RW-KGL-001 has been resolved by Dr. Veterinarian. 
         Notes: Vet visited. Cow given antibiotics. Risk reduced.
```

---

## 📊 Notification Summary Table

| Event | Farmer | Cell Leader | Vet | District Leader | Admin |
|-------|:------:|:-----------:|:---:|:---------------:|:-----:|
| Mortality Risk (any) | 🔔 | - | - | - | - |
| Mortality Risk (≥60%) | 🔔 | 🔔 | - | - | - |
| Low Milk Production | 🔔 | 🔔 | - | - | - |
| Disease Risk | - | 🔔 | 🔔 | - | - |
| High-Risk Birth | - | 🔔 | - | - | - |
| Pass-On Approved | 🔔 | - | - | - | - |
| Pass-On Completed | 🔔 | - | - | - | - |
| Pass-On Rejected | 🔔 | - | - | - | - |
| Alert Resolved | 🔔 | - | - | - | - |

---

## 🔔 Notification Features

### **Unread Badge Count**
```bash
GET /api/v1/notifications/?is_read=false
```
Returns count of unread notifications for the notification bell badge.

### **Mark as Read**
```bash
PATCH /api/v1/notifications/{id}/read/
```
Marks a single notification as read.

### **Mark All as Read**
```bash
POST /api/v1/notifications/mark_all_read/
```
Marks all unread notifications as read at once.

### **Notification Preferences**
```bash
GET/PATCH /api/v1/notifications/settings/
```
Users can configure:
- `in_app` - Enable/disable in-app notifications (default: true)
- `email` - Enable/disable email notifications (default: true)
- `min_severity` - Minimum severity to notify (INFO, WARNING, URGENT, CRITICAL)

---

## 📱 API Endpoints

### **List Notifications**
```bash
GET /api/v1/notifications/
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 42,
      "title": "🚨 Mortality Risk Alert",
      "message": "Your cow RW-KGL-001 has a 72% mortality risk (HIGH)...",
      "is_read": false,
      "created_at": "2026-05-06T06:30:00Z",
      "alert": {
        "id": 87,
        "alert_type": "MORTALITY_RISK",
        "severity": "URGENT"
      }
    }
  ]
}
```

### **Get Single Notification**
```bash
GET /api/v1/notifications/{id}/
Authorization: Bearer {token}
```

### **Mark as Read**
```bash
PATCH /api/v1/notifications/{id}/read/
Authorization: Bearer {token}
```

### **Mark All as Read**
```bash
POST /api/v1/notifications/mark_all_read/
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "marked_read": 8
  }
}
```

### **Get Notification Settings**
```bash
GET /api/v1/notifications/preferences/
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "email": true,
    "sms": false,
    "in_app": true,
    "push": false,
    "min_severity": "WARNING"
  }
}
```

### **Update Notification Settings**
```bash
PATCH /api/v1/notifications/preferences/
Authorization: Bearer {token}
Content-Type: application/json

{
  "in_app": true,
  "email": true,
  "min_severity": "URGENT"
}
```

---

## 🧪 Testing Web Notifications

### **1. Test Mortality Risk Notification**
```bash
# Login as farmer
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "farmer1", "password": "farmer123"}'

# Trigger mortality prediction (as cell leader)
curl -X POST http://localhost:8000/api/v1/predictions/mortality/ \
  -H "Authorization: Bearer $CELL_LEADER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cow_id": 1}'

# Check farmer's notifications
curl http://localhost:8000/api/v1/notifications/ \
  -H "Authorization: Bearer $FARMER_TOKEN"
```

### **2. Test Low Milk Notification**
```bash
# Trigger milk forecast
curl -X POST http://localhost:8000/api/v1/predictions/milk/ \
  -H "Authorization: Bearer $FARMER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cow_id": 1}'

# Check notifications
curl http://localhost:8000/api/v1/notifications/ \
  -H "Authorization: Bearer $FARMER_TOKEN"
```

### **3. Test Pass-On Notifications**
```bash
# Approve a pass-on transfer (as cell leader)
curl -X POST http://localhost:8000/api/v1/passon/1/approve/ \
  -H "Authorization: Bearer $CELL_LEADER_TOKEN"

# Check donor's notifications
curl http://localhost:8000/api/v1/notifications/ \
  -H "Authorization: Bearer $DONOR_TOKEN"

# Check recipient's notifications
curl http://localhost:8000/api/v1/notifications/ \
  -H "Authorization: Bearer $RECIPIENT_TOKEN"
```

### **4. Test Alert Resolution Notification**
```bash
# Resolve an alert (as cell leader)
curl -X POST http://localhost:8000/api/v1/alerts/1/resolve/ \
  -H "Authorization: Bearer $CELL_LEADER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"notes": "Vet visited. Cow given treatment. Risk reduced."}'

# Check farmer's notifications
curl http://localhost:8000/api/v1/notifications/ \
  -H "Authorization: Bearer $FARMER_TOKEN"
```

---

## 🎨 Frontend Integration Example

### **React/Vue Notification Bell**
```javascript
// Fetch unread count for badge
const fetchUnreadCount = async () => {
  const response = await fetch('/api/v1/notifications/?is_read=false', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const data = await response.json();
  return data.data.length; // Number of unread notifications
};

// Fetch all notifications
const fetchNotifications = async () => {
  const response = await fetch('/api/v1/notifications/', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const data = await response.json();
  return data.data;
};

// Mark notification as read
const markAsRead = async (notificationId) => {
  await fetch(`/api/v1/notifications/${notificationId}/read/`, {
    method: 'PATCH',
    headers: { 'Authorization': `Bearer ${token}` }
  });
};

// Mark all as read
const markAllAsRead = async () => {
  await fetch('/api/v1/notifications/mark_all_read/', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  });
};
```

### **Notification Bell Component**
```jsx
<NotificationBell>
  <Badge count={unreadCount} />
  <Dropdown>
    {notifications.map(notif => (
      <NotificationItem 
        key={notif.id}
        title={notif.title}
        message={notif.message}
        isRead={notif.is_read}
        onClick={() => markAsRead(notif.id)}
      />
    ))}
  </Dropdown>
</NotificationBell>
```

---

## 🔍 Database Schema

### **Notification Model**
```python
class Notification(models.Model):
    user       = ForeignKey(User)           # Who receives this
    alert      = ForeignKey(Alert)          # Related alert (optional)
    title      = CharField(max_length=200)  # Notification title
    message    = TextField()                # Notification body
    is_read    = BooleanField(default=False)
    read_at    = DateTimeField(null=True)
    created_at = DateTimeField(auto_now_add=True)
```

### **Query Examples**
```sql
-- Get unread notifications for user
SELECT * FROM notifications 
WHERE user_id = 5 AND is_read = false 
ORDER BY created_at DESC;

-- Mark notification as read
UPDATE notifications 
SET is_read = true, read_at = NOW() 
WHERE id = 42;

-- Count unread by user
SELECT user_id, COUNT(*) as unread_count 
FROM notifications 
WHERE is_read = false 
GROUP BY user_id;
```

---

## 📈 Notification Statistics

### **Check Notification Delivery**
```bash
# View recent notifications in Docker
docker exec girinka-api python manage.py shell -c "
from features.notifications.models import Notification
from django.utils import timezone
from datetime import timedelta

recent = Notification.objects.filter(
    created_at__gte=timezone.now() - timedelta(hours=24)
)
print(f'Last 24h: {recent.count()} notifications')
print(f'Unread: {recent.filter(is_read=False).count()}')
"
```

### **Monitor Notification Logs**
```bash
# Check Django logs for notification creation
docker logs -f girinka-api | grep "Notification"
```

---

## 🎯 Summary

**Total Notification Types:** 8
1. Mortality Risk Alert (farmer + cell leader if high)
2. Low Milk Production Alert (farmer + cell leader)
3. Disease Risk Alert (vet + cell leader)
4. High-Risk Birth Alert (cell leader)
5. Pass-On Transfer Approved (donor + recipient)
6. Pass-On Transfer Completed (donor + recipient)
7. Pass-On Transfer Rejected (donor + recipient)
8. Alert Resolved (farmer)

**Delivery Channels:**
- 🔔 In-app web notifications (notification bell)
- ✉️ Email notifications (via Resend)
- ❌ SMS (not implemented)

**Key Features:**
- ✅ Real-time notifications
- ✅ Unread badge count
- ✅ Mark as read (single or bulk)
- ✅ User preferences (min severity)
- ✅ Linked to alerts for context
- ✅ Role-based filtering

**API Endpoints:**
- `GET /api/v1/notifications/` - List all
- `GET /api/v1/notifications/{id}/` - Get one
- `PATCH /api/v1/notifications/{id}/read/` - Mark as read
- `POST /api/v1/notifications/mark_all_read/` - Mark all as read
- `GET/PATCH /api/v1/notifications/preferences/` - Preferences

---

**Last Updated:** May 2026  
**System:** Girinka Pulse Backend API  
**Notification System:** In-App Web Notifications
