import aiosmtplib
from email.message import EmailMessage
from ..settings import settings
async def send_email_async(to:str, subject:str, html:str, attachments:list[tuple[str,bytes]]|None=None):
    msg=EmailMessage(); msg['From']=settings.SMTP_FROM; msg['To']=to; msg['Subject']=subject
    msg.set_content('Client HTML non supportato.'); msg.add_alternative(html, subtype='html')
    if attachments:
        for filename,data in attachments:
            msg.add_attachment(data, maintype='application', subtype='octet-stream', filename=filename)
    await aiosmtplib.send(msg, hostname=settings.SMTP_HOST, port=settings.SMTP_PORT, username=settings.SMTP_USERNAME or None, password=settings.SMTP_PASSWORD or None, start_tls=False)
