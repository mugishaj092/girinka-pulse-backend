"""Auth endpoint tests."""
import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestLogin:
    URL = "/api/v1/auth/login/"

    def test_valid_login(self, api_client, farmer_user):
        r = api_client.post(self.URL, {"username": "farmer_test", "password": "testpass123"})
        assert r.status_code == 200
        assert "access" in r.data["data"]
        assert "refresh" in r.data["data"]

    def test_invalid_credentials(self, api_client):
        r = api_client.post(self.URL, {"username": "nobody", "password": "wrong"})
        assert r.status_code == 400

    def test_deactivated_user(self, api_client, farmer_user):
        farmer_user.is_active = False
        farmer_user.save()
        r = api_client.post(self.URL, {"username": "farmer_test", "password": "testpass123"})
        assert r.status_code == 400


@pytest.mark.django_db
class TestMe:
    URL = "/api/v1/auth/me/"

    def test_get_profile(self, auth_farmer):
        r = auth_farmer.get(self.URL)
        assert r.status_code == 200
        assert r.data["data"]["username"] == "farmer_test"

    def test_unauthenticated(self, api_client):
        r = api_client.get(self.URL)
        assert r.status_code == 401

    def test_patch_profile(self, auth_farmer):
        r = auth_farmer.patch(self.URL, {"full_name": "Updated Name"})
        assert r.status_code == 200
