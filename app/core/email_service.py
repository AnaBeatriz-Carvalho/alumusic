# Caminho: app/core/email_service.py

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger(__name__)

def send_summary_email(summary_text, start_date, end_date, recipients):
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    sender_email = os.getenv('SENDER_EMAIL', 'noreply@alumusic.com')

    if not all([smtp_server, recipients]):
        logger.error("Servidor SMTP ou destinatários não configurados. E-mail não enviado.")
        return

    message = MIMEMultipart("alternative")
    subject = f"🎵 AluMusic Insights: Resumo Semanal ({start_date.strftime('%d/%m')} - {end_date.strftime('%d/%m')})"
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = ", ".join(recipients)

    html_body = f"""
    <html><body>
        <h2>Resumo de Tendências da Semana</h2>
        <p>Abaixo estão os principais insights gerados pela IA com base nos comentários da última semana:</p>
        <div style="background-color:#f5f5f5; border-left: 5px solid #00ff88; padding: 15px; margin: 10px 0; color: #000;">
          <pre style="white-space: pre-wrap; font-family: sans-serif; font-size: 14px;">{summary_text}</pre>
        </div>
    </body></html>
    """
    message.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            if smtp_user and smtp_password:
                server.starttls()
                server.login(smtp_user, smtp_password)
            server.sendmail(sender_email, recipients, message.as_string())
        logger.info(f"E-mail de resumo enviado com sucesso para: {recipients}")
    except Exception as e:
        logger.error(f"Falha ao enviar e-mail de resumo: {e}", exc_info=True)