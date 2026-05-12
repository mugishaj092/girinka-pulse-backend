"""
Comprehensive seed command for testing - creates all related data.
Run: docker exec girinka-api python manage.py seed_all
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from features.users.models import User
from features.districts.models import District
from features.beneficiaries.models import Beneficiary
from features.cows.models import Cow
from features.health.models import Veterinarian, HealthRecord
from features.milk.models import MilkProduction
from features.alerts.models import Alert
from features.predictions.models import AIModel, PredictionLog
from features.weather.models import WeatherData
from features.notifications.models import NotificationPreference
import random


class Command(BaseCommand):
    help = 'Seeds comprehensive test data with all relationships'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("\n" + "="*70))
        self.stdout.write(self.style.SUCCESS("🌱 SEEDING GIRINKA PULSE TEST DATA"))
        self.stdout.write(self.style.SUCCESS("="*70 + "\n"))

        # 1. Seed Districts (Rwanda's 30 districts)
        self.stdout.write("📍 Seeding Districts...")
        districts_data = [
            {"district_name": "Kigali", "province": "Kigali City", "latitude": -1.9441, "longitude": 30.0619},
            {"district_name": "Gasabo", "province": "Kigali City", "latitude": -1.9536, "longitude": 30.0605},
            {"district_name": "Kicukiro", "province": "Kigali City", "latitude": -1.9667, "longitude": 30.1000},
            {"district_name": "Nyarugenge", "province": "Kigali City", "latitude": -1.9500, "longitude": 30.0588},
            {"district_name": "Bugesera", "province": "Eastern", "latitude": -2.2167, "longitude": 30.1333},
            {"district_name": "Gatsibo", "province": "Eastern", "latitude": -1.6167, "longitude": 30.4167},
            {"district_name": "Kayonza", "province": "Eastern", "latitude": -1.8833, "longitude": 30.6167},
            {"district_name": "Kirehe", "province": "Eastern", "latitude": -2.2167, "longitude": 30.7167},
            {"district_name": "Ngoma", "province": "Eastern", "latitude": -2.1833, "longitude": 30.5333},
            {"district_name": "Nyagatare", "province": "Eastern", "latitude": -1.3000, "longitude": 30.3333},
            {"district_name": "Rwamagana", "province": "Eastern", "latitude": -1.9500, "longitude": 30.4333},
            {"district_name": "Gicumbi", "province": "Northern", "latitude": -1.5833, "longitude": 30.0667},
            {"district_name": "Musanze", "province": "Northern", "latitude": -1.5000, "longitude": 29.6333},
            {"district_name": "Burera", "province": "Northern", "latitude": -1.4833, "longitude": 29.8667},
            {"district_name": "Gakenke", "province": "Northern", "latitude": -1.6833, "longitude": 29.7833},
            {"district_name": "Rulindo", "province": "Northern", "latitude": -1.7667, "longitude": 30.0667},
            {"district_name": "Kamonyi", "province": "Southern", "latitude": -2.0333, "longitude": 29.9833},
            {"district_name": "Muhanga", "province": "Southern", "latitude": -2.0833, "longitude": 29.7500},
            {"district_name": "Nyanza", "province": "Southern", "latitude": -2.3500, "longitude": 29.7500},
            {"district_name": "Ruhango", "province": "Southern", "latitude": -2.2333, "longitude": 29.7833},
            {"district_name": "Gisagara", "province": "Southern", "latitude": -2.5833, "longitude": 29.8333},
            {"district_name": "Huye", "province": "Southern", "latitude": -2.5833, "longitude": 29.7333},
            {"district_name": "Nyamagabe", "province": "Southern", "latitude": -2.5000, "longitude": 29.4167},
            {"district_name": "Nyaruguru", "province": "Southern", "latitude": -2.7333, "longitude": 29.4333},
            {"district_name": "Karongi", "province": "Western", "latitude": -2.0000, "longitude": 29.3833},
            {"district_name": "Ngororero", "province": "Western", "latitude": -1.8167, "longitude": 29.5333},
            {"district_name": "Nyabihu", "province": "Western", "latitude": -1.6500, "longitude": 29.5167},
            {"district_name": "Nyamasheke", "province": "Western", "latitude": -2.3333, "longitude": 29.1167},
            {"district_name": "Rubavu", "province": "Western", "latitude": -1.6833, "longitude": 29.2667},
            {"district_name": "Rusizi", "province": "Western", "latitude": -2.4833, "longitude": 28.9000},
        ]
        
        districts = {}
        for data in districts_data:
            district, created = District.objects.get_or_create(
                district_name=data["district_name"],
                defaults=data
            )
            districts[data["district_name"]] = district
            if created:
                self.stdout.write(f"  ✅ {data['district_name']}")
        
        self.stdout.write(self.style.SUCCESS(f"✅ {len(districts)} districts ready\n"))

        # 2. Seed Users (all 5 roles)
        self.stdout.write("👥 Seeding Users...")
        users_data = [
            {"username": "admin", "password": "admin123", "email": "admin@girinka.rw", 
             "full_name": "System Administrator", "role": "ADMIN", "phone_number": "+250788000001"},
            {"username": "district_leader", "password": "district123", "email": "district@girinka.rw",
             "full_name": "District Leader Kigali", "role": "DISTRICT_LEADER", "phone_number": "+250788000002",
             "district": districts["Kigali"]},
            {"username": "cell_leader", "password": "cell123", "email": "cell@girinka.rw",
             "full_name": "Cell Leader Kimironko", "role": "CELL_LEADER", "phone_number": "+250788000003",
             "district": districts["Kigali"]},
            {"username": "vet", "password": "vet123", "email": "vet@girinka.rw",
             "full_name": "Dr. Veterinarian", "role": "VETERINARIAN", "phone_number": "+250788000004",
             "district": districts["Kigali"]},
            {"username": "farmer1", "password": "farmer123", "email": "farmer1@girinka.rw",
             "full_name": "Jean Baptiste Farmer", "role": "FARMER", "phone_number": "+250788000005",
             "district": districts["Kigali"]},
            {"username": "farmer2", "password": "farmer123", "email": "farmer2@girinka.rw",
             "full_name": "Marie Claire Farmer", "role": "FARMER", "phone_number": "+250788000006",
             "district": districts["Gasabo"]},
        ]
        
        users = {}
        for data in users_data:
            username = data.pop("username")
            password = data.pop("password")
            
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, password=password, **data)
                users[username] = user
                self.stdout.write(f"  ✅ {username} ({data['role']})")
            else:
                users[username] = User.objects.get(username=username)
        
        self.stdout.write(self.style.SUCCESS(f"✅ {len(users)} users ready\n"))

        # 3. Create Veterinarian profile
        self.stdout.write("🩺 Creating Veterinarian profile...")
        vet_user = users.get("vet")
        if vet_user and not Veterinarian.objects.filter(user=vet_user).exists():
            vet = Veterinarian.objects.create(
                user=vet_user,
                district=districts["Kigali"],
                license_number="VET-RW-2024-001",
                specialization="Cattle Health"
            )
            self.stdout.write(f"  ✅ Veterinarian profile created\n")

        # 4. Seed Beneficiaries
        self.stdout.write("🏠 Seeding Beneficiaries...")
        beneficiaries_data = [
            {"national_id": "1198780012345678", "full_name": "Jean Baptiste Farmer", 
             "ubudehe_category": 1, "phone_number": "+250788000005", "gender": "M",
             "registration_date": date.today() - timedelta(days=365),
             "district": districts["Kigali"], "user": users.get("farmer1")},
            {"national_id": "1199080023456789", "full_name": "Marie Claire Farmer",
             "ubudehe_category": 2, "phone_number": "+250788000006", "gender": "F",
             "registration_date": date.today() - timedelta(days=300),
             "district": districts["Gasabo"], "user": users.get("farmer2")},
            {"national_id": "1198580034567890", "full_name": "Pierre Uwimana",
             "ubudehe_category": 1, "phone_number": "+250788000007", "gender": "M",
             "registration_date": date.today() - timedelta(days=200),
             "district": districts["Kicukiro"]},
            {"national_id": "1199280045678901", "full_name": "Grace Mukamana",
             "ubudehe_category": 2, "phone_number": "+250788000008", "gender": "F",
             "registration_date": date.today() - timedelta(days=150),
             "district": districts["Nyarugenge"]},
        ]
        
        beneficiaries = []
        for data in beneficiaries_data:
            user = data.pop("user", None)
            beneficiary, created = Beneficiary.objects.get_or_create(
                national_id=data["national_id"],
                defaults=data
            )
            if user and not beneficiary.user:
                beneficiary.user = user
                beneficiary.save()
            beneficiaries.append(beneficiary)
            if created:
                self.stdout.write(f"  ✅ {data['full_name']}")
        
        self.stdout.write(self.style.SUCCESS(f"✅ {len(beneficiaries)} beneficiaries ready\n"))

        # 5. Seed Cows
        self.stdout.write("🐮 Seeding Cows...")
        cows_data = [
            {"tag_number": "RW-KGL-001", "breed": "FRIESIAN", "dob": date(2021, 3, 15),
             "health_status": "HEALTHY", "beneficiary": beneficiaries[0], "district": districts["Kigali"],
             "lactation_number": 2, "days_in_milk": 120},
            {"tag_number": "RW-KGL-002", "breed": "JERSEY", "dob": date(2020, 8, 22),
             "health_status": "HEALTHY", "beneficiary": beneficiaries[0], "district": districts["Kigali"],
             "lactation_number": 3, "days_in_milk": 200},
            {"tag_number": "RW-GAS-001", "breed": "ANKOLE_CROSS", "dob": date(2022, 1, 10),
             "health_status": "AT_RISK", "beneficiary": beneficiaries[1], "district": districts["Gasabo"],
             "lactation_number": 1, "days_in_milk": 80, "mortality_risk_score": 0.45},
            {"tag_number": "RW-KIC-001", "breed": "FRIESIAN_CROSS", "dob": date(2021, 6, 5),
             "health_status": "HEALTHY", "beneficiary": beneficiaries[2], "district": districts["Kicukiro"],
             "lactation_number": 2, "days_in_milk": 150},
            {"tag_number": "RW-NYA-001", "breed": "JERSEY_CROSS", "dob": date(2020, 11, 18),
             "health_status": "HIGH_RISK", "beneficiary": beneficiaries[3], "district": districts["Nyarugenge"],
             "lactation_number": 3, "days_in_milk": 250, "mortality_risk_score": 0.72},
        ]
        
        cows = []
        for data in cows_data:
            cow, created = Cow.objects.get_or_create(
                tag_number=data["tag_number"],
                defaults=data
            )
            cows.append(cow)
            if created:
                self.stdout.write(f"  ✅ {data['tag_number']} - {data['breed']}")
        
        self.stdout.write(self.style.SUCCESS(f"✅ {len(cows)} cows ready\n"))

        # 6. Seed Health Records
        self.stdout.write("🩺 Seeding Health Records...")
        vet = Veterinarian.objects.first()
        for i, cow in enumerate(cows[:3]):
            record, created = HealthRecord.objects.get_or_create(
                cow=cow,
                date_recorded=timezone.now() - timedelta(days=random.randint(1, 30)),
                defaults={
                    "vet": vet,
                    "diagnosis": random.choice(["Routine checkup", "Mild fever", "Digestive issue"]),
                    "treatment_given": random.choice(["Vitamins", "Antibiotics", "Deworming"]),
                    "temperature": round(random.uniform(38.0, 39.5), 1),
                    "weight": round(random.uniform(350, 500), 1),
                    "next_visit_date": date.today() + timedelta(days=30),
                }
            )
            if created:
                self.stdout.write(f"  ✅ Health record for {cow.tag_number}")
        
        self.stdout.write(self.style.SUCCESS(f"✅ Health records created\n"))

        # 7. Seed Milk Production (last 14 days for each cow)
        self.stdout.write("🥛 Seeding Milk Production...")
        milk_count = 0
        for cow in cows:
            for days_ago in range(14, 0, -1):
                collection_date = date.today() - timedelta(days=days_ago)
                morning = round(random.uniform(4.0, 8.0), 1)
                evening = round(random.uniform(3.5, 7.5), 1)
                
                _, created = MilkProduction.objects.get_or_create(
                    cow=cow,
                    collection_date=collection_date,
                    defaults={
                        "morning_yield": morning,
                        "evening_yield": evening,
                        "daily_yield": morning + evening,
                        "feed_amount": round(random.uniform(5.0, 8.0), 1),
                        "water_intake": round(random.uniform(30.0, 50.0), 1),
                    }
                )
                if created:
                    milk_count += 1
        
        self.stdout.write(self.style.SUCCESS(f"✅ {milk_count} milk records created\n"))

        # 8. Seed AI Models
        self.stdout.write("🤖 Seeding AI Models...")
        models_data = [
            {"model_type": "MORTALITY_RISK", "version": "v1.0", "accuracy_metric": 0.89,
             "is_deployed": True, "training_samples": 50000},
            {"model_type": "MILK_FORECAST", "version": "v1.0", "r2_score": 0.85,
             "is_deployed": True, "training_samples": 75000},
            {"model_type": "DISEASE_RISK", "version": "v1.0", "accuracy_metric": 0.82,
             "is_deployed": True, "training_samples": 30000},
            {"model_type": "BIRTH_PROBABILITY", "version": "v1.0", "accuracy_metric": 0.78,
             "is_deployed": True, "training_samples": 20000},
        ]
        
        ai_models = []
        for data in models_data:
            model, created = AIModel.objects.get_or_create(
                model_type=data["model_type"],
                version=data["version"],
                defaults=data
            )
            ai_models.append(model)
            if created:
                self.stdout.write(f"  ✅ {data['model_type']} {data['version']}")
        
        self.stdout.write(self.style.SUCCESS(f"✅ {len(ai_models)} AI models ready\n"))

        # 9. Seed Alerts
        self.stdout.write("🚨 Seeding Alerts...")
        alerts_data = [
            {"cow": cows[2], "beneficiary": beneficiaries[1], "alert_type": "MORTALITY_RISK",
             "severity": "WARNING", "risk_score": 0.45, 
             "message": "Cow RW-GAS-001 showing moderate mortality risk",
             "recommendation": "Schedule veterinary checkup within 48 hours"},
            {"cow": cows[4], "beneficiary": beneficiaries[3], "alert_type": "MORTALITY_RISK",
             "severity": "CRITICAL", "risk_score": 0.72,
             "message": "Cow RW-NYA-001 at high mortality risk",
             "recommendation": "Immediate veterinary attention required"},
            {"cow": cows[1], "beneficiary": beneficiaries[0], "alert_type": "LOW_MILK",
             "severity": "INFO", "message": "Milk production below average for RW-KGL-002",
             "recommendation": "Review feeding schedule and nutrition"},
        ]
        
        for data in alerts_data:
            alert, created = Alert.objects.get_or_create(
                cow=data["cow"],
                alert_type=data["alert_type"],
                is_resolved=False,
                defaults=data
            )
            if created:
                self.stdout.write(f"  ✅ {data['alert_type']} for {data['cow'].tag_number}")
        
        self.stdout.write(self.style.SUCCESS(f"✅ Alerts created\n"))

        # 10. Seed Weather Data
        self.stdout.write("🌤️ Seeding Weather Data...")
        weather_count = 0
        for district in list(districts.values())[:5]:  # First 5 districts
            weather, created = WeatherData.objects.get_or_create(
                district=district,
                reading_time=timezone.now(),
                forecast_day=0,
                defaults={
                    "temperature": round(random.uniform(18.0, 28.0), 1),
                    "humidity": round(random.uniform(60.0, 85.0), 1),
                    "rainfall": round(random.uniform(0.0, 15.0), 1),
                    "wind_speed": round(random.uniform(5.0, 20.0), 1),
                    "data_source": "Open-Meteo",
                }
            )
            if created:
                weather_count += 1
        
        self.stdout.write(self.style.SUCCESS(f"✅ {weather_count} weather records created\n"))

        # 11. Create Notification Preferences for all users
        self.stdout.write("🔔 Setting up Notification Preferences...")
        for user in User.objects.all():
            NotificationPreference.objects.get_or_create(
                user=user,
                defaults={
                    "email": True,
                    "sms": False,
                    "in_app": True,
                    "push": False,
                    "min_severity": "WARNING",
                }
            )
        self.stdout.write(self.style.SUCCESS(f"✅ Notification preferences set\n"))

        # Summary
        self.stdout.write("\n" + "="*70)
        self.stdout.write(self.style.SUCCESS("✅ SEEDING COMPLETE - DATABASE SUMMARY"))
        self.stdout.write("="*70)
        self.stdout.write(f"  📍 Districts: {District.objects.count()}")
        self.stdout.write(f"  👥 Users: {User.objects.count()}")
        self.stdout.write(f"  🏠 Beneficiaries: {Beneficiary.objects.count()}")
        self.stdout.write(f"  🐮 Cows: {Cow.objects.count()}")
        self.stdout.write(f"  🩺 Health Records: {HealthRecord.objects.count()}")
        self.stdout.write(f"  🥛 Milk Records: {MilkProduction.objects.count()}")
        self.stdout.write(f"  🚨 Alerts: {Alert.objects.count()}")
        self.stdout.write(f"  🤖 AI Models: {AIModel.objects.count()}")
        self.stdout.write(f"  🌤️ Weather Records: {WeatherData.objects.count()}")
        self.stdout.write("="*70 + "\n")
        
        self.stdout.write(self.style.SUCCESS("🎉 Ready to test! Login credentials in TEST_CREDENTIALS.md\n"))
