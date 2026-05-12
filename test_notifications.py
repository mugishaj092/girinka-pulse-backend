#!/usr/bin/env python
"""
Test notification system - create test notifications and check they appear.
Run: docker exec girinka-api python test_notifications.py
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "girinka.settings.development")
django.setup()

from features.notifications.models import Notification
from features.users.models import User
from features.cows.models import Cow
from features.predictions.services import PredictionService

print("\n" + "="*70)
print("🔔 TESTING NOTIFICATION SYSTEM")
print("="*70 + "\n")

# Get users
print("1️⃣ Getting users...")
farmer = User.objects.filter(role="FARMER").first()
cell_leader = User.objects.filter(role="CELL_LEADER").first()

if not farmer:
    print("   ❌ No farmer found. Run: docker exec girinka-api python manage.py seed_all")
    exit(1)

print(f"   ✅ Farmer: {farmer.full_name} (ID: {farmer.id})")
if cell_leader:
    print(f"   ✅ Cell Leader: {cell_leader.full_name} (ID: {cell_leader.id})")

print("\n" + "-"*70 + "\n")

# Check existing notifications
print("2️⃣ Checking existing notifications...")
farmer_notifs = Notification.objects.filter(user=farmer).order_by('-created_at')
print(f"   Total notifications for {farmer.full_name}: {farmer_notifs.count()}")

if farmer_notifs.exists():
    print(f"\n   Recent notifications:")
    for notif in farmer_notifs[:5]:
        status = "📖 READ" if notif.is_read else "🔔 UNREAD"
        print(f"   {status} - {notif.title}")
        print(f"           {notif.message[:80]}...")
        print(f"           Created: {notif.created_at}")
        print()

print("\n" + "-"*70 + "\n")

# Trigger a prediction to create new notification
print("3️⃣ Triggering mortality prediction to create notification...")
cow = Cow.objects.filter(is_alive=True, beneficiary__user=farmer).first()

if cow:
    print(f"   Using cow: {cow.tag_number}")
    try:
        result = PredictionService.run_mortality_check(cow)
        print(f"   ✅ Prediction complete:")
        print(f"      Risk Score: {result.get('mortality_risk_score', 'N/A')}")
        print(f"      Alert Triggered: {result.get('alert_triggered', False)}")
        
        # Check if notification was created
        new_notifs = Notification.objects.filter(
            user=farmer,
            title__icontains="Mortality"
        ).order_by('-created_at')
        
        if new_notifs.exists():
            latest = new_notifs.first()
            print(f"\n   ✅ NEW NOTIFICATION CREATED:")
            print(f"      Title: {latest.title}")
            print(f"      Message: {latest.message[:100]}...")
            print(f"      Read: {latest.is_read}")
        else:
            print(f"\n   ℹ️  No notification created (risk may be too low)")
            
    except Exception as e:
        print(f"   ❌ Prediction failed: {e}")
else:
    print("   ⚠️  No cow found for this farmer")

print("\n" + "-"*70 + "\n")

# Show notification preferences
print("4️⃣ Checking notification preferences...")
from features.notifications.models import NotificationPreference

prefs, created = NotificationPreference.objects.get_or_create(user=farmer)
print(f"   User: {farmer.full_name}")
print(f"   Email: {prefs.email}")
print(f"   In-App: {prefs.in_app}")
print(f"   Min Severity: {prefs.min_severity}")

print("\n" + "="*70)
print("✅ NOTIFICATION TEST COMPLETE")
print("="*70 + "\n")

print("📱 To view notifications via API:")
print(f"   GET /api/v1/notifications/")
print(f"   Authorization: Bearer <token>")
print()
