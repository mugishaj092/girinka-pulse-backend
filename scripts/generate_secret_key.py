#!/usr/bin/env python
"""
Generate a secure Django SECRET_KEY for production use.
Run: python scripts/generate_secret_key.py
"""
from django.core.management.utils import get_random_secret_key

print("\n" + "="*70)
print("🔐 Django SECRET_KEY Generator")
print("="*70)
print("\nGenerated SECRET_KEY (copy this to Render environment variables):\n")
print(get_random_secret_key())
print("\n" + "="*70)
print("⚠️  Keep this secret! Never commit it to Git.")
print("="*70 + "\n")
