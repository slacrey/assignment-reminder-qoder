import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.config import settings


async def send_reminder_email(to_email: str, child_name: str, assignment_title: str, description: str) -> None:
    """Send a homework reminder email to a child."""
    msg = MIMEMultipart()
    msg["From"] = settings.SMTP_FROM_EMAIL or settings.SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = f"📝 作业提醒：{assignment_title}"

    body = f"""
    <html>
    <body>
    <h2>作业提醒</h2>
    <p><strong>{child_name}</strong>，你好！</p>
    <p>你有一项作业需要完成：</p>
    <ul>
        <li><strong>作业标题：</strong>{assignment_title}</li>
        <li><strong>作业描述：</strong>{description or '无'}</li>
    </ul>
    <p>请尽快完成作业！💪</p>
    </body>
    </html>
    """

    html_part = MIMEText(body, "html", "utf-8")
    msg.attach(html_part)

    await aiosmtplib.send(
        msg,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        use_tls=True,
    )
