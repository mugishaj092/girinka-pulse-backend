"""Notification tests — Resend email, no SMS."""
import pytest
from unittest.mock import patch, MagicMock


class TestResendEmail:
    """Test Resend email sending (mocked)."""

    @patch("resend.Emails.send")
    def test_send_email_success(self, mock_send):
        mock_send.return_value = {"id": "test-email-id-123"}
        from features.notifications.utils import send_email
        result = send_email(
            to="test@example.com",
            subject="Test",
            html="<p>Test</p>",
        )
        assert result is True
        mock_send.assert_called_once()

    @patch("resend.Emails.send")
    def test_send_alert_email(self, mock_send):
        mock_send.return_value = {"id": "alert-email-456"}
        from features.notifications.utils import send_alert_email
        result = send_alert_email(
            to="farmer@example.com",
            farmer_name="Jean Baptiste",
            cow_tag="RW-GAS-001",
            alert_type="MORTALITY_RISK",
            severity="URGENT",
            message="Risk score: 0.75",
            recommendation="Urgent vet visit within 24 hours.",
        )
        assert result is True

    @patch("resend.Emails.send")
    def test_send_password_reset_email(self, mock_send):
        mock_send.return_value = {"id": "otp-email-789"}
        from features.notifications.utils import send_password_reset_email
        result = send_password_reset_email(
            to="user@example.com",
            user_name="Joseph",
            otp_code="482951",
        )
        assert result is True

    @patch("resend.Emails.send", side_effect=Exception("Resend API error"))
    def test_send_email_handles_failure(self, mock_send):
        from features.notifications.utils import send_email
        result = send_email(to="bad@example.com", subject="Fail", html="<p>x</p>")
        assert result is False

    @patch("resend.Emails.send")
    def test_send_to_list(self, mock_send):
        mock_send.return_value = {"id": "bulk-email-001"}
        from features.notifications.utils import send_email
        result = send_email(
            to=["a@example.com", "b@example.com"],
            subject="Bulk",
            html="<p>bulk</p>",
        )
        assert result is True
        call_args = mock_send.call_args[0][0]
        assert len(call_args["to"]) == 2


class TestCloudinaryUpload:
    """Test Cloudinary upload helpers (mocked)."""

    @patch("cloudinary.uploader.upload")
    def test_upload_cow_photo(self, mock_upload):
        mock_upload.return_value = {"secure_url": "https://res.cloudinary.com/dhforyx1s/image/upload/cows/test.jpg"}
        from shared.cloudinary_utils import upload_cow_photo
        url = upload_cow_photo(b"fake-image-bytes", "RW-GAS-001")
        assert url is not None
        assert "cloudinary.com" in url

    @patch("cloudinary.uploader.upload")
    def test_upload_report_pdf(self, mock_upload):
        mock_upload.return_value = {"secure_url": "https://res.cloudinary.com/dhforyx1s/raw/upload/reports/test.html"}
        from shared.cloudinary_utils import upload_report_pdf
        url = upload_report_pdf(b"<html>report</html>", "report_1.html")
        assert url is not None

    @patch("cloudinary.uploader.upload", side_effect=Exception("Cloudinary error"))
    def test_upload_handles_failure(self, mock_upload):
        from shared.cloudinary_utils import upload_cow_photo
        url = upload_cow_photo(b"fake", "BAD-TAG")
        assert url is None
