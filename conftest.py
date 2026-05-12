"""Shared pytest fixtures for Girinka backend tests."""
import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from features.users.models import User, UserRole
from features.districts.models import District
from features.beneficiaries.models import Beneficiary
from features.cows.models import Cow
from datetime import date


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def district(db):
    return District.objects.create(
        district_name="Gasabo", province="Kigali", latitude=-1.9, longitude=30.1
    )


@pytest.fixture
def admin_user(db, district):
    return User.objects.create_user(
        username="admin_test", password="testpass123",
        full_name="Admin User", role=UserRole.ADMIN, district=district
    )


@pytest.fixture
def farmer_user(db, district):
    return User.objects.create_user(
        username="farmer_test", password="testpass123",
        full_name="Farmer User", role=UserRole.FARMER, district=district
    )


@pytest.fixture
def cell_leader_user(db, district):
    return User.objects.create_user(
        username="cl_test", password="testpass123",
        full_name="Cell Leader", role=UserRole.CELL_LEADER, district=district
    )


@pytest.fixture
def beneficiary(db, farmer_user, district):
    return Beneficiary.objects.create(
        user=farmer_user, district=district,
        national_id="1199012345678901", full_name="Jean Baptiste",
        ubudehe_category=1, registration_date=date.today(), phone_number="+250788000001"
    )


@pytest.fixture
def cow(db, beneficiary, district):
    return Cow.objects.create(
        beneficiary=beneficiary, district=district,
        tag_number="RW-GAS-001", breed="FRIESIAN_CROSS",
        dob=date(2020, 1, 15), lactation_number=2, days_in_milk=90
    )


@pytest.fixture
def auth_admin(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def auth_farmer(api_client, farmer_user):
    api_client.force_authenticate(user=farmer_user)
    return api_client


@pytest.fixture
def auth_cl(api_client, cell_leader_user):
    api_client.force_authenticate(user=cell_leader_user)
    return api_client
