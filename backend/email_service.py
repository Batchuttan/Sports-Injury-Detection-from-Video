import os
import smtplib
import logging
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load environment variables from .env in backend directory and root workspace
env_path = Path(__file__).resolve().parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
load_dotenv()

logger = logging.getLogger("email_service")
logging.basicConfig(level=logging.INFO)

def get_email_config():
    smtp_host = os.getenv("SMTP_HOST") or "smtp.gmail.com"
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER") or os.getenv("EMAIL_USER", "yourtubeentertainments@gmail.com")
    smtp_password = os.getenv("SMTP_PASSWORD") or os.getenv("EMAIL_PASS", "bspd hfbr wphq phzy")
    smtp_from_email = os.getenv("SMTP_FROM_EMAIL") or smtp_user
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000").rstrip("/")
    return {
        "host": smtp_host,
        "port": smtp_port,
        "user": smtp_user,
        "password": smtp_password.replace(" ", "").strip() if smtp_password else "",
        "from_email": smtp_from_email,
        "frontend_url": frontend_url
    }

# Local in-memory log of sent emails for audit and debugging
sent_emails_store = []

def send_password_reset_email(to_email: str, reset_token: str, mode: str = "reset") -> dict:
    """
    Sends an email with a secure link to reset or change password.
    mode: 'reset' (forgot password) or 'change' (settings change password)
    """
    config = get_email_config()
    reset_url = f"{config['frontend_url']}/reset-password?token={reset_token}&mode={mode}"
    
    action_title = "Password Reset Request" if mode == "reset" else "Confirm Password Change"
    action_description = (
        "We received a request to reset the password for your SportsAI Biomechanics account."
        if mode == "reset"
        else "You requested to update your SportsAI account password from account settings."
    )
    button_text = "Reset My Password Now" if mode == "reset" else "Confirm Password Change"

    subject = f"{action_title} | SportsAI Biomechanics"

    text_body = f"""Hello,

{action_description}

Please click the secure link below to proceed with setting a new password (valid for 30 minutes):
{reset_url}

If you did not request this, please disregard this email. Your password will remain unchanged.

Best regards,
SportsAI Biomechanics Security Team
{config['user']}
"""

    html_body = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{subject}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #0b0f19; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #f8fafc;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color: #0b0f19; padding: 40px 16px;">
    <tr>
      <td align="center">
        <!-- Main Card -->
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width: 580px; background-color: #111827; border: 1px solid #1e293b; border-radius: 16px; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.6);">
          
          <!-- Top Accent Bar -->
          <tr>
            <td style="height: 4px; background: linear-gradient(90deg, #4f46e5 0%, #ec4899 100%); font-size: 0; line-height: 0;">&nbsp;</td>
          </tr>

          <!-- Header -->
          <tr>
            <td style="padding: 36px 32px 24px 32px; text-align: center; background: radial-gradient(circle at top, rgba(99, 102, 241, 0.15) 0%, transparent 70%);">
              <div style="display: inline-block; padding: 10px 18px; border-radius: 9999px; background: rgba(79, 70, 229, 0.15); border: 1px solid rgba(99, 102, 241, 0.3); margin-bottom: 16px;">
                <span style="font-size: 13px; font-weight: 700; letter-spacing: 1px; color: #a5b4fc; text-transform: uppercase;">Sports Injury Detection AI</span>
              </div>
              <h1 style="margin: 0; font-size: 28px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px;">
                Sports<span style="color: #818cf8;">AI</span> Platform
              </h1>
              <p style="margin: 6px 0 0 0; font-size: 13px; color: #94a3b8; font-weight: 500;">
                Biomechanical Intelligence &amp; Injury Prevention
              </p>
            </td>
          </tr>

          <!-- Main Content -->
          <tr>
            <td style="padding: 12px 32px 36px 32px;">
              <div style="background-color: #172033; border: 1px solid #283548; border-radius: 12px; padding: 24px; margin-bottom: 24px;">
                <h2 style="margin: 0 0 10px 0; font-size: 19px; font-weight: 700; color: #f8fafc;">
                  {action_title}
                </h2>
                <p style="margin: 0 0 16px 0; font-size: 14px; line-height: 1.6; color: #cbd5e1;">
                  {action_description}
                </p>
                <p style="margin: 0; font-size: 13px; line-height: 1.6; color: #94a3b8;">
                  Target Account: <strong style="color: #a5b4fc;">{to_email}</strong>
                </p>
              </div>

              <p style="font-size: 14px; line-height: 1.6; color: #cbd5e1; margin: 0 0 28px 0; text-align: center;">
                Click the button below to authenticate and enter your new password. For security, this link expires in <strong style="color: #f43f5e;">30 minutes</strong>.
              </p>

              <!-- CTA Button -->
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="center">
                    <a href="{reset_url}" target="_blank" style="display: inline-block; background: linear-gradient(135deg, #4f46e5 0%, #6366f1 50%, #ec4899 100%); color: #ffffff; font-size: 15px; font-weight: 700; text-decoration: none; padding: 15px 36px; border-radius: 10px; box-shadow: 0 6px 20px rgba(79, 70, 229, 0.45); letter-spacing: 0.2px;">
                      {button_text} &rarr;
                    </a>
                  </td>
                </tr>
              </table>

              <!-- Direct Link Fallback -->
              <div style="margin-top: 36px; padding-top: 24px; border-top: 1px solid #1e293b;">
                <p style="margin: 0 0 10px 0; font-size: 12px; color: #64748b; line-height: 1.5;">
                  If the button does not work, copy and paste this direct URL into your browser:
                </p>
                <div style="word-break: break-all; background-color: #0b0f19; border: 1px solid #1e293b; border-radius: 8px; padding: 12px; font-size: 12px; color: #818cf8; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; line-height: 1.4;">
                  {reset_url}
                </div>
              </div>

              <!-- Security Notice -->
              <div style="margin-top: 24px; padding: 14px 16px; background-color: rgba(15, 23, 42, 0.8); border: 1px solid #1e293b; border-radius: 8px;">
                <p style="margin: 0; font-size: 12px; line-height: 1.5; color: #64748b;">
                  🔒 <strong>Security Warning:</strong> If you did not initiate this password reset, please ignore this email or reach out to support. Your SportsAI account remains protected.
                </p>
              </div>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding: 20px 32px; background-color: #090d16; border-top: 1px solid #1e293b; text-align: center;">
              <p style="margin: 0; font-size: 12px; color: #475569; line-height: 1.5;">
                Sent securely by SportsAI Security Gateway<br>
                From: {config['from_email']} &bull; &copy; 2026 SportsAI Biomechanics Intelligence.
              </p>
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
        "mode": mode
    }

    # Transmit via SMTP using the provided credentials
    if config["host"] and config["user"] and config["password"]:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"SportsAI Biomechanics <{config['from_email']}>"
            msg["To"] = to_email

            msg.attach(MIMEText(text_body, "plain"))
            msg.attach(MIMEText(html_body, "html"))

            logger.info(f"Connecting to SMTP server {config['host']}:{config['port']}...")
            with smtplib.SMTP(config["host"], config["port"], timeout=15) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(config["user"], config["password"])
                server.sendmail(config["from_email"], [to_email], msg.as_string())

            logger.info(f"Successfully dispatched {mode} email via Gmail SMTP to {to_email}")
            sent_emails_store.append(email_record)
            return {
                "success": True,
                "method": "smtp",
                "message": f"Verification email successfully sent to {to_email}",
                "reset_url": reset_url
            }
        except Exception as e:
            logger.error(f"Failed to send email via SMTP: {e}", exc_info=True)
            return {
                "success": False,
                "method": "smtp_error",
                "message": f"SMTP delivery failed: {str(e)}",
                "reset_url": None
            }

    logger.warning("SMTP credentials not fully configured.")
    return {
        "success": False,
        "method": "unconfigured",
        "message": "SMTP configuration missing.",
        "reset_url": None
    }
