"""Cow endpoint tests."""
import pytest


@pytest.mark.django_db
class TestCowPermissions:
    URL = "/api/v1/cows/"

    def test_farmer_sees_only_own_cows(self, auth_farmer, cow):
        r = auth_farmer.get(self.URL)
        assert r.status_code == 200
        data = r.data["data"]
        assert all(c["beneficiary"] == cow.beneficiary_id for c in data)

    def test_cell_leader_sees_district_cows(self, auth_cl, cow, cell_leader_user, district):
        cell_leader_user.district = district
        cell_leader_user.save()
        r = auth_cl.get(self.URL)
        assert r.status_code == 200

    def test_unauthenticated_blocked(self, api_client):
        r = api_client.get(self.URL)
        assert r.status_code == 401

    def test_farmer_cannot_register_cow(self, auth_farmer, beneficiary, district):
        r = auth_farmer.post(self.URL, {
            "tag_number": "RW-TEST-999",
            "breed": "FRIESIAN",
            "beneficiary": beneficiary.id,
            "district": district.id,
        })
        assert r.status_code == 403

    def test_cow_death_recording(self, auth_cl, cow, cell_leader_user, district):
        cell_leader_user.district = district
        cell_leader_user.save()
        r = auth_cl.post(f"/api/v1/cows/{cow.id}/death/", {"cause": "Respiratory illness"})
        assert r.status_code == 200
        cow.refresh_from_db()
        assert not cow.is_alive

    def test_duplicate_tag_number(self, auth_cl, cow, beneficiary, district, cell_leader_user):
        cell_leader_user.district = district
        cell_leader_user.save()
        r = auth_cl.post("/api/v1/cows/", {
            "tag_number": cow.tag_number,  # duplicate
            "breed": "JERSEY",
            "beneficiary": beneficiary.id,
            "district": district.id,
        })
        assert r.status_code in (400, 409)


@pytest.mark.django_db
class TestCowAtRisk:
    def test_at_risk_endpoint(self, auth_cl, cow, cell_leader_user, district):
        from features.cows.models import HealthStatus
        cell_leader_user.district = district
        cell_leader_user.save()
        cow.health_status = HealthStatus.HIGH_RISK
        cow.save()
        r = auth_cl.get("/api/v1/cows/at_risk/")
        assert r.status_code == 200
        assert len(r.data["data"]) >= 1
