#!/usr/bin/env python
"""
Seeds AI model versions into the database.
Run once after migrate: python scripts/seed_ai_models.py
"""
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "girinka.settings")
django.setup()

from features.predictions.models import AIModel
from datetime import datetime

MODELS = [
    {
        "name": "CatBoost Mortality Risk",
        "model_type": "MORTALITY",
        "version": "v1.0.0",
        "algorithm": "CatBoost Classifier",
        "accuracy": 0.89,
        "precision": 0.87,
        "recall": 0.91,
        "f1_score": 0.89,
        "is_deployed": True,
        "description": "Predicts 30-day mortality risk based on health metrics, milk production, and environmental factors.",
    },
    {
        "name": "LSTM Milk Forecast",
        "model_type": "MILK_FORECAST",
        "version": "v1.0.0",
        "algorithm": "Bidirectional LSTM",
        "mae": 0.82,
        "rmse": 1.15,
        "r2_score": 0.91,
        "is_deployed": True,
        "description": "7-day milk yield forecast using historical production patterns and seasonal trends.",
    },
    {
        "name": "Random Forest Disease Detection",
        "model_type": "DISEASE",
        "version": "v1.0.0",
        "algorithm": "Random Forest Classifier",
        "accuracy": 0.85,
        "precision": 0.83,
        "recall": 0.87,
        "f1_score": 0.85,
        "is_deployed": True,
        "description": "Multi-class disease detection for FMD, ECF, Mastitis, Brucellosis, Anthrax, Lumpy Skin, and Blackleg.",
    },
    {
        "name": "Logistic Regression Birth Success",
        "model_type": "PASS_ON",
        "version": "v1.0.0",
        "algorithm": "Logistic Regression",
        "accuracy": 0.81,
        "precision": 0.79,
        "recall": 0.84,
        "f1_score": 0.81,
        "is_deployed": True,
        "description": "Predicts probability of successful calving for pass-on eligibility assessment.",
    },
]

print("Seeding AI models...")
for data in MODELS:
    model, created = AIModel.objects.get_or_create(
        name=data["name"],
        version=data["version"],
        defaults={
            "model_type": data["model_type"],
            "algorithm": data["algorithm"],
            "accuracy": data.get("accuracy"),
            "precision": data.get("precision"),
            "recall": data.get("recall"),
            "f1_score": data.get("f1_score"),
            "mae": data.get("mae"),
            "rmse": data.get("rmse"),
            "r2_score": data.get("r2_score"),
            "is_deployed": data["is_deployed"],
            "description": data["description"],
            "deployed_at": datetime.now() if data["is_deployed"] else None,
        }
    )
    if created:
        print(f"  ✅ Created: {model.name} {model.version}")
    else:
        print(f"  ⏭️  Exists: {model.name} {model.version}")

print(f"\n✅ Seeded {len(MODELS)} AI models. Total in DB: {AIModel.objects.count()}")
