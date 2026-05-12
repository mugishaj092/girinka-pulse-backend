"""
Notification utilities.
- Email: Resend SDK (no SMTP, no Africa's Talking)
- Files: Cloudinary
- No SMS
"""
import logging
import resend
from django.conf import settings

logger = logging.getLogger(__name__)


def _resend_client():
    resend.api_key = settings.RESEND_API_KEY
    return resend.Emails


def send_email(to: str | list, subject: str, html: str, text: str = "") -> bool:
    """
    Send email via Resend.
    `to` can be a single address or list of addresses.
    """
    if not settings.RESEND_API_KEY:
        logger.warning("RESEND_API_KEY not set — email skipped.")
        return False

    if isinstance(to, str):
        to = [to]

    try:
        resend.api_key = settings.RESEND_API_KEY
        params = {
            "from":    settings.FROM_EMAIL,
            "to":      to,
            "subject": subject,
            "html":    html,
        }
        if text:
            params["text"] = text

        result = resend.Emails.send(params)
        logger.info(f"Email sent to {to}: id={result.get('id')}")
        return True
    except Exception as e:
        logger.error(f"Resend email failed to {to}: {e}")
        return False


def send_alert_email(
    to: str,
    farmer_name: str,
    cow_tag: str,
    alert_type: str,
    severity: str,
    message: str,
    recommendation: str,
) -> bool:
    """Send a formatted alert email to a farmer or cell leader."""
    severity_colors = {
        "INFO":     "#3B82F6",
        "WARNING":  "#F59E0B",
        "URGENT":   "#EF4444",
        "CRITICAL": "#7F1D1D",
    }
    color = severity_colors.get(severity, "#6B7280")

    html = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; background: #f3f4f6; padding: 20px;">
      <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <div style="background: {color}; padding: 20px; text-align: center;">
          <h1 style="color: white; margin: 0; font-size: 22px;">🐄 Girinka Pulse Alert</h1>
          <p style="color: white; margin: 8px 0 0; font-size: 14px; opacity: 0.9;">{severity} — {alert_type.replace('_', ' ').title()}</p>
        </div>
        <div style="padding: 30px;">
          <p style="font-size: 16px; color: #374151;">Dear <strong>{farmer_name}</strong>,</p>
          <p style="color: #6B7280;">An AI alert has been generated for your cow:</p>
          <div style="background: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 6px; padding: 16px; margin: 20px 0;">
            <p style="margin: 0 0 8px;"><strong>Cow Tag:</strong> {cow_tag}</p>
            <p style="margin: 0 0 8px;"><strong>Alert:</strong> {message}</p>
            <p style="margin: 0; color: {color};"><strong>Recommended Action:</strong> {recommendation}</p>
          </div>
          <p style="font-size: 12px; color: #9CA3AF;">This alert was generated automatically by the Girinka Pulse AI system. Please contact your local cell leader or veterinarian if you need assistance.</p>
        </div>
        <div style="background: #F3F4F6; padding: 16px; text-align: center; font-size: 12px; color: #9CA3AF;">
          Girinka Pulse — Rwanda "One Cow Per Family" Program<br>
          Powered by AI for Rwanda Agriculture Board (RAB)
        </div>
      </div>
    </body>
    </html>
    """

    subject_map = {
        "INFO": "ℹ️ Girinka Info",
        "WARNING": "⚠️ Girinka Warning",
        "URGENT": "🔶 Girinka Urgent Alert",
        "CRITICAL": "🚨 Girinka Critical Alert",
    }

    return send_email(
        to=to,
        subject=f"{subject_map.get(severity, 'Girinka Alert')}: Cow {cow_tag}",
        html=html,
    )


def send_weekly_report_email(
    to: str | list,
    report_type: str,
    period: str,
    stats: dict,
    download_url: str = "",
) -> bool:
    """Send weekly/monthly report email to district or national leaders."""
    rows = "".join(
        f"<tr><td style='padding:8px;border-bottom:1px solid #e5e7eb;'>{k.replace('_',' ').title()}</td>"
        f"<td style='padding:8px;border-bottom:1px solid #e5e7eb;text-align:right;'><strong>{v}</strong></td></tr>"
        for k, v in stats.items()
    )

    download_btn = (
        f'<a href="{download_url}" style="display:inline-block;background:#16A34A;color:white;'
        f'padding:10px 24px;border-radius:6px;text-decoration:none;margin-top:16px;">📥 Download Report</a>'
        if download_url else ""
    )

    html = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family:Arial,sans-serif;background:#f3f4f6;padding:20px;">
      <div style="max-width:600px;margin:0 auto;background:white;border-radius:8px;overflow:hidden;">
        <div style="background:#166534;padding:20px;text-align:center;">
          <h1 style="color:white;margin:0;">🐄 Girinka Pulse</h1>
          <p style="color:#BBF7D0;margin:6px 0 0;">{report_type.replace('_',' ').title()} — {period}</p>
        </div>
        <div style="padding:30px;">
          <h2 style="color:#374151;">Program Summary</h2>
          <table style="width:100%;border-collapse:collapse;">
            <tbody>{rows}</tbody>
          </table>
          {download_btn}
        </div>
        <div style="background:#F3F4F6;padding:16px;text-align:center;font-size:12px;color:#9CA3AF;">
          Auto-generated by Girinka Pulse AI System
        </div>
      </div>
    </body>
    </html>
    """

    return send_email(
        to=to,
        subject=f"Girinka Report: {report_type.replace('_', ' ').title()} — {period}",
        html=html,
    )


def send_password_reset_email(to: str, user_name: str, otp_code: str) -> bool:
    """Send OTP password reset email via Resend."""
    html = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family:Arial,sans-serif;background:#f3f4f6;padding:20px;">
      <div style="max-width:480px;margin:0 auto;background:white;border-radius:8px;overflow:hidden;">
        <div style="background:#166534;padding:20px;text-align:center;">
          <h1 style="color:white;margin:0;font-size:20px;">🐄 Girinka Pulse</h1>
          <p style="color:#BBF7D0;margin:6px 0 0;">Password Reset</p>
        </div>
        <div style="padding:30px;text-align:center;">
          <p style="color:#374151;">Hello <strong>{user_name}</strong>,</p>
          <p style="color:#6B7280;">Your password reset code is:</p>
          <div style="background:#F0FDF4;border:2px solid #16A34A;border-radius:8px;padding:20px;margin:20px 0;">
            <span style="font-size:36px;font-weight:bold;letter-spacing:8px;color:#166534;">{otp_code}</span>
          </div>
          <p style="color:#9CA3AF;font-size:13px;">This code expires in <strong>10 minutes</strong>.</p>
          <p style="color:#9CA3AF;font-size:12px;">If you did not request this, ignore this email.</p>
        </div>
      </div>
    </body>
    </html>
    """

    return send_email(
        to=to,
        subject="Girinka Pulse — Password Reset Code",
        html=html,
    )
