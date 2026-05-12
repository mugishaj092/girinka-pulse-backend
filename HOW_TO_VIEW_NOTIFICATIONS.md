# 🔔 How to View Notifications

## The notifications ARE working! ✅

There are **13 notifications** in the database for different users:
- Jean Baptiste Farmer: 6 notifications
- Cell Leader Kimironko: 5 notifications
- Marie Claire Farmer: 1 notification
- Dr. Veterinarian: 1 notification

---

## 📱 View Notifications via API

### Step 1: Login as a user who has notifications

**Login as Jean Baptiste (has 6 notifications):**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "farmer1", "password": "farmer123"}'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "id": 5,
      "username": "farmer1",
      "full_name": "Jean Baptiste Farmer",
      "role": "FARMER"
    }
  }
}
```

Copy the `access` token.

---

### Step 2: Get notifications

```bash
curl http://localhost:8000/api/v1/notifications/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

**Expected Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "title": "🚨 Mortality Risk Alert",
      "message": "Your cow RW-KGL-001 has a 72% mortality risk (VERY_HIGH). 🔴 CRITICAL: Urgent vet consultation within 12 hours...",
      "is_read": false,
      "read_at": null,
      "created_at": "2026-05-10T06:30:00Z",
      "alert": {
        "id": 1,
        "alert_type": "MORTALITY_RISK",
        "severity": "URGENT"
      }
    },
    {
      "id": 2,
      "title": "🥛 Low Milk Production Alert",
      "message": "Your cow RW-KGL-002 is predicted to produce only 4.2L/day over the next 7 days...",
      "is_read": false,
      "read_at": null,
      "created_at": "2026-05-10T06:00:00Z",
      "alert": {
        "id": 2,
        "alert_type": "LOW_MILK",
        "severity": "WARNING"
      }
    }
  ],
  "meta": {
    "count": 6,
    "next": null,
    "previous": null
  }
}
```

---

### Step 3: Get only unread notifications

```bash
curl "http://localhost:8000/api/v1/notifications/?is_read=false" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

---

### Step 4: Mark a notification as read

```bash
curl -X PATCH http://localhost:8000/api/v1/notifications/1/read/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

---

### Step 5: Mark all as read

```bash
curl -X POST http://localhost:8000/api/v1/notifications/mark_all_read/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

---

### Step 6: Get notification preferences

```bash
curl http://localhost:8000/api/v1/notifications/preferences/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
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
    "min_severity": "INFO"
  }
}
```

---

### Step 7: Update notification preferences

```bash
curl -X PATCH http://localhost:8000/api/v1/notifications/preferences/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "in_app": true,
    "email": true,
    "min_severity": "WARNING"
  }'
```

---

## 🧪 Test with Other Users

### Cell Leader (5 notifications)
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "cell_leader", "password": "cell123"}'
```

### Marie Claire Farmer (1 notification)
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "farmer2", "password": "farmer123"}'
```

### Veterinarian (1 notification)
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "vet", "password": "vet123"}'
```

---

## 🎯 Create New Notifications

To create new notifications, trigger predictions:

### Trigger Mortality Risk Prediction
```bash
# Login as cell leader first
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "cell_leader", "password": "cell123"}'

# Run prediction (creates notification if risk >= 40%)
curl -X POST http://localhost:8000/api/v1/predictions/mortality/ \
  -H "Authorization: Bearer CELL_LEADER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cow_id": 1}'
```

### Trigger Milk Forecast
```bash
curl -X POST http://localhost:8000/api/v1/predictions/milk/ \
  -H "Authorization: Bearer FARMER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cow_id": 1}'
```

---

## 🌐 View in Swagger UI

1. Open: http://localhost:8000/api/v1/docs/
2. Click "Authorize" button (top right)
3. Login to get token
4. Paste token in authorization dialog
5. Navigate to "🔔 Notifications" section
6. Try the endpoints interactively

---

## ✅ Summary

**Notifications ARE working!** ✅

The issue is:
- You need to login as a user who has notifications
- Each user only sees their own notifications
- Farmers see notifications about their cows
- Cell leaders see notifications about cows in their district

**Users with notifications:**
- `farmer1` / `farmer123` - 6 notifications
- `cell_leader` / `cell123` - 5 notifications
- `farmer2` / `farmer123` - 1 notification
- `vet` / `vet123` - 1 notification

**Endpoints:**
- `GET /api/v1/notifications/` - List all
- `GET /api/v1/notifications/?is_read=false` - Unread only
- `PATCH /api/v1/notifications/{id}/read/` - Mark as read
- `POST /api/v1/notifications/mark_all_read/` - Mark all as read
- `GET /api/v1/notifications/preferences/` - Get preferences
- `PATCH /api/v1/notifications/preferences/` - Update preferences
