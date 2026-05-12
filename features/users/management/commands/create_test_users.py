from django.core.management.base import BaseCommand
from features.users.models import User
from features.districts.models import District


class Command(BaseCommand):
    help = "Create test accounts for all 5 roles"

    def handle(self, *args, **kwargs):
        # Get or create a test district
        district, _ = District.objects.get_or_create(
            district_name="Gasabo",
            defaults={"province": "Kigali", "latitude": -1.94, "longitude": 30.06},
        )

        users = [
            {"username": "admin_test",    "password": "Test@1234", "full_name": "Admin User",          "role": "ADMIN",           "email": "admin@girinka.test"},
            {"username": "farmer_test",   "password": "Test@1234", "full_name": "Jean Baptiste",       "role": "FARMER",          "email": "farmer@girinka.test"},
            {"username": "cl_test",       "password": "Test@1234", "full_name": "Cell Leader Uwase",   "role": "CELL_LEADER",     "email": "cl@girinka.test"},
            {"username": "vet_test",      "password": "Test@1234", "full_name": "Dr. Mugabo Eric",     "role": "VETERINARIAN",    "email": "vet@girinka.test"},
            {"username": "dl_test",       "password": "Test@1234", "full_name": "District Leader Neza","role": "DISTRICT_LEADER", "email": "dl@girinka.test"},
        ]

        self.stdout.write("\n🐄 Creating Girinka test accounts...\n")

        for u in users:
            if User.objects.filter(username=u["username"]).exists():
                self.stdout.write(f"  ⚠️  {u['username']} already exists — skipped")
                continue

            User.objects.create_user(
                username=u["username"],
                password=u["password"],
                full_name=u["full_name"],
                role=u["role"],
                email=u["email"],
                district=district,
                is_active=True,
                is_verified=True,
            )
            self.stdout.write(f"  ✅  {u['role']:<18} → {u['username']} / {u['password']}")

        self.stdout.write("\n✅ Done! Login at POST /api/v1/auth/login/\n")
