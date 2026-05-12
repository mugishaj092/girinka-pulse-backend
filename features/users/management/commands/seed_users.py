"""
Seed initial users for testing and development.
Run: docker exec girinka-api python manage.py seed_users
"""
from django.core.management.base import BaseCommand
from features.users.models import User
from features.districts.models import District


class Command(BaseCommand):
    help = 'Seeds initial users with all 5 roles'

    def handle(self, *args, **options):
        # Get or create a district for testing
        district, _ = District.objects.get_or_create(
            district_name="Kigali",
            defaults={
                "province": "Kigali City",
                "latitude": -1.9441,
                "longitude": 30.0619,
            }
        )

        users_data = [
            {
                "username": "admin",
                "email": "admin@girinka.rw",
                "full_name": "System Administrator",
                "role": "ADMIN",
                "phone_number": "+250788000001",
                "password": "admin123",
            },
            {
                "username": "district_leader",
                "email": "district@girinka.rw",
                "full_name": "District Leader Kigali",
                "role": "DISTRICT_LEADER",
                "phone_number": "+250788000002",
                "district": district,
                "password": "district123",
            },
            {
                "username": "cell_leader",
                "email": "cell@girinka.rw",
                "full_name": "Cell Leader Kimironko",
                "role": "CELL_LEADER",
                "phone_number": "+250788000003",
                "district": district,
                "password": "cell123",
            },
            {
                "username": "vet",
                "email": "vet@girinka.rw",
                "full_name": "Dr. Veterinarian",
                "role": "VETERINARIAN",
                "phone_number": "+250788000004",
                "district": district,
                "password": "vet123",
            },
            {
                "username": "farmer",
                "email": "farmer@girinka.rw",
                "full_name": "Farmer John Doe",
                "role": "FARMER",
                "phone_number": "+250788000005",
                "district": district,
                "password": "farmer123",
            },
        ]

        created_count = 0
        credentials = []
        
        for user_data in users_data:
            username = user_data["username"]
            password = user_data["password"]
            role = user_data["role"]
            
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f"  ⚠️  User '{username}' already exists - skipped")
                )
                continue

            user_create_data = {
                "email": user_data["email"],
                "full_name": user_data["full_name"],
                "role": role,
                "phone_number": user_data["phone_number"],
            }
            
            if "district" in user_data:
                user_create_data["district"] = user_data["district"]
            
            user = User.objects.create_user(
                username=username,
                password=password,
                **user_create_data
            )
            created_count += 1
            credentials.append({"role": role, "username": username, "password": password})
            self.stdout.write(
                self.style.SUCCESS(f"  ✅ Created {role}: {username}")
            )

        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS(f"✅ Seeded {created_count} users"))
        self.stdout.write("="*60 + "\n")
        
        if credentials:
            self.stdout.write("\n📋 Login Credentials:\n")
            self.stdout.write("-" * 60)
            for cred in credentials:
                self.stdout.write(f"  Role: {cred['role']}")
                self.stdout.write(f"  Username: {cred['username']}")
                self.stdout.write(f"  Password: {cred['password']}")
                self.stdout.write("-" * 60)
