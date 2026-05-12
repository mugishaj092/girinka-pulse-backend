#!/usr/bin/env python
"""
Test script to verify ML service connectivity and all models.
Run: docker exec girinka-api python test_ml_service.py
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "girinka.settings.development")
django.setup()

from features.predictions.ml_client import ml_client
from features.cows.models import Cow
from features.predictions.services import PredictionService
import json

print("\n" + "="*70)
print("🤖 TESTING ML SERVICE CONNECTION")
print("="*70 + "\n")

# Test 1: Health Check
print("1️⃣ Testing ML Service Health Check...")
try:
    health = ml_client.health()
    print(f"   ✅ Health Check: {json.dumps(health, indent=2)}")
except Exception as e:
    print(f"   ❌ Health Check Failed: {e}")

print("\n" + "-"*70 + "\n")

# Test 2: Get a test cow
print("2️⃣ Getting test cow...")
try:
    cow = Cow.objects.filter(is_alive=True).first()
    if cow:
        print(f"   ✅ Found cow: {cow.tag_number} (ID: {cow.id})")
        print(f"      Owner: {cow.beneficiary.full_name}")
        print(f"      Breed: {cow.breed}")
        print(f"      Health Status: {cow.health_status}")
    else:
        print("   ⚠️  No living cows found in database")
        print("   Run: docker exec girinka-api python manage.py seed_all")
        exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

print("\n" + "-"*70 + "\n")

# Test 3: Mortality Risk Prediction
print("3️⃣ Testing Mortality Risk Prediction (CatBoost)...")
try:
    result = PredictionService.run_mortality_check(cow)
    print(f"   ✅ Mortality Prediction:")
    print(f"      Risk Score: {result.get('mortality_risk_score', 'N/A')}")
    print(f"      Risk Level: {result.get('risk_level', 'N/A')}")
    print(f"      Alert Triggered: {result.get('alert_triggered', False)}")
    if result.get('alert_triggered'):
        print(f"      Severity: {result.get('alert_severity', 'N/A')}")
except Exception as e:
    print(f"   ❌ Mortality Prediction Failed: {e}")

print("\n" + "-"*70 + "\n")

# Test 4: Milk Forecast
print("4️⃣ Testing Milk Forecast (LSTM)...")
try:
    # Check if cow has enough milk records
    milk_count = cow.milk_records.count()
    print(f"   Milk records available: {milk_count}")
    
    if milk_count >= 7:
        result = PredictionService.run_milk_forecast(cow)
        print(f"   ✅ Milk Forecast:")
        print(f"      Forecast Days: {result.get('forecast_days', 'N/A')}")
        print(f"      Avg Predicted Yield: {result.get('avg_predicted_yield_litres', 'N/A')} L/day")
        predictions = result.get('predictions', [])
        if predictions:
            print(f"      Day 1: {predictions[0].get('predicted_yield_litres', 'N/A')} L")
            print(f"      Day 7: {predictions[-1].get('predicted_yield_litres', 'N/A')} L")
    else:
        print(f"   ⚠️  Need at least 7 milk records (found {milk_count})")
        print("   Skipping milk forecast test")
except Exception as e:
    print(f"   ❌ Milk Forecast Failed: {e}")

print("\n" + "-"*70 + "\n")

# Test 5: Disease Detection
print("5️⃣ Testing Disease Detection (Random Forest)...")
try:
    payload = {
        "cow_id": cow.id,
        "breed": cow.breed,
        "age_months": 36,
        "body_temperature_c": 39.5,
        "weight_kg": 350,
        "fever": True,
        "lameness": False,
        "nasal_discharge": False,
        "coughing": False,
        "diarrhea": False,
        "loss_of_appetite": True,
        "swollen_lymph_nodes": False,
        "skin_lesions": False,
        "udder_swelling": False,
        "milk_changes": False,
        "respiratory_distress": False,
        "weakness": True,
        "recent_vaccination": False,
        "contact_with_sick_animals": False,
        "grazing_area_change": False
    }
    result = PredictionService.run_disease_check(cow, payload)
    print(f"   ✅ Disease Detection:")
    print(f"      Top Disease: {result.get('top_disease', 'N/A')}")
    print(f"      Probability: {result.get('top_probability', 'N/A')}")
    print(f"      Emergency: {result.get('emergency', False)}")
    triggered = result.get('triggered_alerts', [])
    if triggered:
        print(f"      Alerts Triggered: {len(triggered)}")
except Exception as e:
    print(f"   ❌ Disease Detection Failed: {e}")

print("\n" + "-"*70 + "\n")

# Test 6: Birth Prediction
print("6️⃣ Testing Birth Prediction (Logistic Regression)...")
try:
    payload = {
        "cow_id": cow.id,
        "breed": cow.breed,
        "age_months": 48,
        "parity": 2,
        "body_condition_score": 3.5,
        "gestation_days": 270,
        "previous_birth_complications": False,
        "nutrition_quality": "Good",
        "veterinary_care_access": True,
        "season": "Dry"
    }
    result = PredictionService.run_birth_check(cow, payload)
    print(f"   ✅ Birth Prediction:")
    print(f"      Success Probability: {result.get('birth_success_probability', 'N/A')}")
    print(f"      Prognosis: {result.get('prognosis_label', 'N/A')}")
    print(f"      Risk Level: {result.get('risk_level', 'N/A')}")
except Exception as e:
    print(f"   ❌ Birth Prediction Failed: {e}")

print("\n" + "="*70)
print("✅ ML SERVICE TEST COMPLETE")
print("="*70 + "\n")
