import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os


def sendMail(toEmailAddress, subject, content):
    fromEmail = os.getenv("GMAIL_APP_EMAIL")
    fromPassword = os.getenv("GMAIL_APP_SECRET_PASSWORD")
    # print(fromEmail)
    msg = MIMEMultipart("alternative")

    msg["Subject"] = subject
    msg["From"] = fromEmail
    msg["To"] = toEmailAddress
    # print("message settt")

    text = "Your email client doesnt support html messages"
    html = content

    # Record the MIME types of both parts - text/plain and text/html.

    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(fromEmail, fromPassword)
            print("Sending mail to: ", toEmailAddress)
            print("Subject:", subject)
            print("Content:", content)
            smtp.sendmail(fromEmail, toEmailAddress, msg.as_string())
            print("Mail sent")
    except Exception as e:
        print("Email not sent; Error : ", e)
