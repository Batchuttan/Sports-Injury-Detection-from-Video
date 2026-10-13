import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger("email_service")
logging.basicConfig(level=logging.INFO)

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "no-reply@sportsai.com")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000").rstrip("/")

# Local in-memory log of sent emails for instant debugging and demo verification
sent_emails_store = []

def send_password_reset_email(to_email: str, reset_token: str, mode: str = "reset") -> dict:
    """
    Sends an email with a secure link to reset or change password.
    mode: 'reset' (forgot password) or 'change' (settings change password)
    """
    reset_url = f"{FRONTEND_URL}/reset-password?token={reset_token}&mode={mode}"
    
    action_title = "Password Reset Request" if mode == "reset" else "Confirm Password Change"
    action_description = (
        "We received a request to reset your SportsAI account password."
        if mode == "reset"
        else "You requested to update your SportsAI account password from account settings."
    )
    button_text = "Reset Password Now" if mode == "reset" else "Change Password Now"

    subject = f"{action_title} - SportsAI Biomechanics Platform"

    text_body = f"""Hello,

{action_description}

Click the secure link below to proceed (valid for 30 minutes):
{reset_url}

If you did not request this, you can safely ignore this email.

Best regards,
The SportsAI Security Team
"""

    html_body = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{subject}</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #0b0f19; color: #f1f5f9;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #0b0f19; padding: 40px 20px;">
    <tr>
      <td align="center">
        <table width="100%" max-width="600" cellpadding="0" cellspacing="0" style="max-width: 600px; background-color: #111827; border: 1px solid #1f2937; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
          <!-- Header -->
          <tr>
            <td style="padding: 32px; background: linear-gradient(135deg, rgba(79, 70, 229, 0.2), rgba(236, 72, 153, 0.2)); border-bottom: 1px solid #1f2937; text-align: center;">
              <span style="font-size: 24px; font-weight: 800; background: linear-gradient(to right, #818cf8, #f472b6); -webkit-background-clip: text; color: #818cf8; letter-spacing: -0.5px;">
                SportsAI
              </span>
              <div style="font-size: 13px; color: #94a3b8; margin-top: 4px; font-weight: 500;">
                AI-Powered Biomechanics & Injury Prevention
              </div>
            </td>
          </tr>

          <!-- Content -->
          <tr>
            <td style="padding: 36px 32px;">
              <h2 style="font-size: 20px; font-weight: 700; color: #ffffff; margin-top: 0; margin-bottom: 12px;">
                {action_title}
              </h2>
              <p style="font-size: 15px; line-height: 1.6; color: #cbd5e1; margin-bottom: 24px;">
                {action_description} Please click the button below to complete the process. This security link expires in <strong>30 minutes</strong>.
              </p>

              <!-- CTA Button -->
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="center" style="padding: 16px 0 28px 0;">
                    <a href="{reset_url}" target="_blank" style="display: inline-block; background: linear-gradient(135deg, #4f46e5, #6366f1); color: #ffffff; font-size: 15px; font-weight: 600; text-decoration: none; padding: 14px 32px; border-radius: 10px; box-shadow: 0 4px 14px rgba(79, 70, 229, 0.4);">
                      {button_text} &rarr;
                    </a>
                  </td>
                </tr>
              </table>

              <p style="font-size: 13px; color: #64748b; line-height: 1.5; margin-bottom: 8px;">
                If the button above does not work, copy and paste this link into your browser:
              </p>
              <div style="word-break: break-all; background-color: #0b0f19; border: 1px solid #1e293b; border-radius: 8px; padding: 12px; font-size: 12px; color: #818cf8; font-family: monospace;">
                {reset_url}
              </div>

              <div style="border-top: 1px solid #1f2937; margin-top: 28px; padding-top: 20px; font-size: 13px; color: #64748b; line-height: 1.5;">
                <strong>Security Reminder:</strong> If you did not make this request, someone else may have typed your email address by accident. Your password will remain unchanged until you access the link above.
              </div>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding: 20px 32px; background-color: #090d16; border-top: 1px solid #1f2937; text-align: center; font-size: 12px; color: #475569;">
              &copy; 2026 SportsAI Biomechanics Intelligence. All rights reserved.
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

    email_record = {
        "to_email": to_email,
        "subject": subject,
        "reset_url": reset_url,
        "mode": mode,
        "timestamp": None
    }

    # Attempt real SMTP transmission if configured
    if SMTP_HOST and SMTP_USER and SMTP_PASSWORD:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = SMTP_FROM_EMAIL
            msg["To"] = to_email

            msg.attach(MIMEText(text_body, "plain"))
            msg.attach(MIMEText(html_body, "html"))

            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(SMTP_FROM_EMAIL, [to_email], msg.as_string())

            logger.info(f"Successfully sent {mode} email via SMTP to {to_email}")
            sent_emails_store.append(email_record)
            return {
                "success": True,
                "method": "smtp",
                "message": f"Verification email sent to {to_email}",
                "reset_url": reset_url
            }
        except Exception as e:
            logger.warning(f"SMTP send failed: {e}. Falling back to secure link logging.")

    # Local development / fallback handling:
    logger.info("=" * 60)
    logger.info(f"[SportsAI Security Email Service] To: {to_email}")
    logger.info(f"Action: {action_title}")
    logger.info(f"Access Link: {reset_url}")
    logger.info("=" * 60)

    sent_emails_store.append(email_record)
    return {
        "success": True,
        "method": "mock_preview",
        "message": f"Verification email prepared for {to_email}",
        "reset_url": reset_url
    }
