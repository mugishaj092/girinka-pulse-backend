"""Beneficiary endpoint tests."""
import pytest
from datetime import date


@pytest.mark.django_db
class TestBeneficiaryRegistration:
    URL = "/api/v1/beneficiaries/"

    def test_cell_leader_can_register(self, auth_cl, district, cell_leader_user):
        cell_leader_user.district = district
        cell_leader_user.save()
        r = auth_cl.post(self.URL, {
            "national_id": "1199099999999901",
            "full_name": "New Farmer",
            "ubudehe_category": 1,
            "district": district.id,
            "registration_date": str(date.today()),
            "phone_number": "+250788111222",
        })
        assert r.status_code == 201

    def test_invalid_ubudehe_rejected(self, auth_cl, district, cell_leader_user):
        cell_leader_user.district = district
        cell_leader_user.save()
        r = auth_cl.post(self.URL, {
            "national_id": "1199099999999902",
            "full_name": "Rich Farmer",
            "ubudehe_category": 4,  # invalid for Girinka
            "district": district.id,
            "registration_date": str(date.today()),
        })
        assert r.status_code == 400

    def test_farmer_cannot_register(self, auth_farmer, district, beneficiary):
        r = auth_farmer.post(self.URL, {"national_id": "xxx", "full_name": "x", "ubudehe_category": 1})
        assert r.status_code == 403

    def test_deregister(self, auth_cl, beneficiary, cell_leader_user, district):
        cell_leader_user.district = district
        cell_leader_user.save()
        r = auth_cl.post(f"{self.URL}{beneficiary.id}/deregister/", {"reason": "VOLUNTARY"})
        assert r.status_code == 200
        beneficiary.refresh_from_db()
        assert not beneficiary.is_active

    def test_reregister_by_admin(self, auth_admin, beneficiary):
        beneficiary.is_active = False
        beneficiary.save()
        r = auth_admin.post(f"{self.URL}{beneficiary.id}/reregister/")
        assert r.status_code == 200
        beneficiary.refresh_from_db()
        assert beneficiary.is_active
