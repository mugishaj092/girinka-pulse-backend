"""Alert endpoint tests."""
import pytest
from features.alerts.models import Alert, AlertType, AlertSeverity


@pytest.mark.django_db
class TestAlerts:
    def test_farmer_sees_own_alerts(self, auth_farmer, cow, beneficiary):
        Alert.objects.create(
            cow=cow, beneficiary=beneficiary,
            alert_type=AlertType.MORTALITY_RISK,
            severity=AlertSeverity.URGENT,
            message="Test alert"
        )
        r = auth_farmer.get("/api/v1/alerts/")
        assert r.status_code == 200

    def test_unread_count(self, auth_farmer, cow, beneficiary):
        Alert.objects.create(cow=cow, beneficiary=beneficiary, alert_type=AlertType.LOW_MILK, severity=AlertSeverity.INFO)
        r = auth_farmer.get("/api/v1/alerts/unread_count/")
        assert r.status_code == 200
        assert r.data["data"]["unread_count"] >= 1

    def test_resolve_alert(self, auth_cl, cow, beneficiary, cell_leader_user, district):
        cell_leader_user.district = district
        cell_leader_user.save()
        alert = Alert.objects.create(cow=cow, beneficiary=beneficiary, alert_type=AlertType.MORTALITY_RISK, severity=AlertSeverity.URGENT)
        r = auth_cl.post(f"/api/v1/alerts/{alert.id}/resolve/", {"notes": "Vet visited"})
        assert r.status_code == 200
        alert.refresh_from_db()
        assert alert.is_resolved
