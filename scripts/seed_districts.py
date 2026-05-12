#!/usr/bin/env python
"""
Seeds all 30 Rwanda districts with GPS coordinates.
Run once after migrate: python scripts/seed_districts.py
"""
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "girinka.settings")
django.setup()

from features.districts.models import District

DISTRICTS = [
    # Kigali City
    {"name": "Gasabo", "province": "Kigali City", "latitude": -1.9403, "longitude": 30.0619},
    {"name": "Kicukiro", "province": "Kigali City", "latitude": -1.9667, "longitude": 30.1000},
    {"name": "Nyarugenge", "province": "Kigali City", "latitude": -1.9536, "longitude": 30.0606},
    
    # Southern Province
    {"name": "Gisagara", "province": "Southern Province", "latitude": -2.5833, "longitude": 29.8333},
    {"name": "Huye", "province": "Southern Province", "latitude": -2.5950, "longitude": 29.7389},
    {"name": "Kamonyi", "province": "Southern Province", "latitude": -2.0333, "longitude": 29.9667},
    {"name": "Muhanga", "province": "Southern Province", "latitude": -2.0833, "longitude": 29.7500},
    {"name": "Nyamagabe", "province": "Southern Province", "latitude": -2.4500, "longitude": 29.4167},
    {"name": "Nyanza", "province": "Southern Province", "latitude": -2.3500, "longitude": 29.7500},
    {"name": "Nyaruguru", "province": "Southern Province", "latitude": -2.6167, "longitude": 29.4333},
    {"name": "Ruhango", "province": "Southern Province", "latitude": -2.2333, "longitude": 29.7833},
    
    # Western Province
    {"name": "Karongi", "province": "Western Province", "latitude": -2.0000, "longitude": 29.3833},
    {"name": "Ngororero", "province": "Western Province", "latitude": -1.8333, "longitude": 29.5333},
    {"name": "Nyabihu", "province": "Western Province", "latitude": -1.6500, "longitude": 29.5000},
    {"name": "Nyamasheke", "province": "Western Province", "latitude": -2.3333, "longitude": 29.1167},
    {"name": "Rubavu", "province": "Western Province", "latitude": -1.6833, "longitude": 29.2667},
    {"name": "Rusizi", "province": "Western Province", "latitude": -2.4833, "longitude": 28.9000},
    {"name": "Rutsiro", "province": "Western Province", "latitude": -1.9833, "longitude": 29.3333},
    
    # Northern Province
    {"name": "Burera", "province": "Northern Province", "latitude": -1.4833, "longitude": 29.8833},
    {"name": "Gakenke", "province": "Northern Province", "latitude": -1.6833, "longitude": 29.7833},
    {"name": "Gicumbi", "province": "Northern Province", "latitude": -1.5833, "longitude": 30.0667},
    {"name": "Musanze", "province": "Northern Province", "latitude": -1.4989, "longitude": 29.6350},
    {"name": "Rulindo", "province": "Northern Province", "latitude": -1.7667, "longitude": 30.0667},
    
    # Eastern Province
    {"name": "Bugesera", "province": "Eastern Province", "latitude": -2.2667, "longitude": 30.1333},
    {"name": "Gatsibo", "province": "Eastern Province", "latitude": -1.6167, "longitude": 30.4167},
    {"name": "Kayonza", "province": "Eastern Province", "latitude": -1.8833, "longitude": 30.4167},
    {"name": "Kirehe", "province": "Eastern Province", "latitude": -2.2167, "longitude": 30.7167},
    {"name": "Ngoma", "province": "Eastern Province", "latitude": -2.1667, "longitude": 30.5167},
    {"name": "Nyagatare", "province": "Eastern Province", "latitude": -1.3000, "longitude": 30.3333},
    {"name": "Rwamagana", "province": "Eastern Province", "latitude": -1.9500, "longitude": 30.4333},
]

print("Seeding Rwanda districts...")
for data in DISTRICTS:
    district, created = District.objects.get_or_create(
        name=data["name"],
        defaults={
            "province": data["province"],
            "latitude": data["latitude"],
            "longitude": data["longitude"],
        }
    )
    if created:
        print(f"  ✅ Created: {district.name}, {district.province}")
    else:
        print(f"  ⏭️  Exists: {district.name}")

print(f"\n✅ Seeded {len(DISTRICTS)} districts. Total in DB: {District.objects.count()}")
