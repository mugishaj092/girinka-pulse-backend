# Test User Credentials

These users have been seeded into the database for testing and development.

## 🔑 Login Credentials

### 1. Admin (Full System Access)
- **Username:** `admin`
- **Password:** `admin123`
- **Email:** admin@girinka.rw
- **Role:** ADMIN
- **Permissions:** Full access to all endpoints, user management, system configuration

---

### 2. District Leader (District-wide Read Access)
- **Username:** `district_leader`
- **Password:** `district123`
- **Email:** district@girinka.rw
- **Role:** DISTRICT_LEADER
- **District:** Kigali
- **Permissions:** Read-only access to all district data, view national reports

---

### 3. Cell Leader (District Management)
- **Username:** `cell_leader`
- **Password:** `cell123`
- **Email:** cell@girinka.rw
- **Role:** CELL_LEADER
- **District:** Kigali
- **Permissions:** 
  - Register/deregister beneficiaries
  - Register cows, record deaths
  - Approve pass-on transfers
  - Run AI predictions
  - Resolve alerts
  - Generate district reports

---

### 4. Veterinarian (Health Management)
- **Username:** `vet`
- **Password:** `vet123`
- **Email:** vet@girinka.rw
- **Role:** VETERINARIAN
- **District:** Kigali
- **Permissions:**
  - Add health records
  - Schedule vet visits
  - Record cow deaths
  - Run disease predictions
  - Resolve health alerts

---

### 5. Farmer (Own Data Only)
- **Username:** `farmer`
- **Password:** `farmer123`
- **Email:** farmer@girinka.rw
- **Role:** FARMER
- **District:** Kigali
- **Permissions:**
  - View own cows
  - Log daily milk production
  - View own alerts
  - View own notifications

---

## 🧪 Testing the API

### 1. Login to get JWT token

```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "id": 1,
      "username": "admin",
      "email": "admin@girinka.rw",
      "full_name": "System Administrator",
      "role": "ADMIN"
    }
  }
}
```

---

### 2. Use the access token

```bash
curl http://localhost:8000/api/v1/users/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

---

### 3. Test in Swagger UI

1. Open http://localhost:8000/api/v1/docs/
2. Click **"Authorize"** button (top right)
3. Enter: `Bearer <your_access_token>`
4. Click **"Authorize"**
5. Now you can test all endpoints interactively

---

## 🔄 Re-seeding Users

If you need to seed users again:

```bash
docker exec girinka-api python manage.py seed_users
```

**Note:** The command will skip users that already exist.

---

## 🗑️ Deleting All Users (Fresh Start)

```bash
docker exec girinka-api python manage.py shell -c "
from features.users.models import User
User.objects.all().delete()
print('All users deleted')
"
```

Then re-run the seed command.

---

## 📊 Verify Users Were Created

```bash
docker exec girinka-api python manage.py shell -c "
from features.users.models import User
for user in User.objects.all():
    print(f'{user.username} - {user.role} - {user.email}')
"
```

---

## 🎯 Next Steps

1. **Login with admin** to access Django admin panel:
   - URL: http://localhost:8000/admin/
   - Username: `admin`
   - Password: `admin123`

2. **Test API endpoints** in Swagger UI:
   - URL: http://localhost:8000/api/v1/docs/

3. **Create test data:**
   - Add districts (30 Rwanda districts)
   - Register beneficiaries
   - Register cows
   - Log milk production
   - Create alerts

4. **Test role-based permissions:**
   - Login as different users
   - Verify each role can only access their permitted endpoints
