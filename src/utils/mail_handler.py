import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class MailHandler:
    report = "report.html"

    @staticmethod
    def send_mail():
        print('Inside send mail')
        html = open(MailHandler.report, 'rb').read()
        from_email = os.getenv('FROM_ADDR')
        from_password = os.getenv('FROM_PASSWORD')
        to_email = os.getenv('TO_ADDR')
        msg = MIMEMultipart('alternative')
        msg['Subject'] = '[FAIL] Test Report'
        msg['From'] = from_email
        msg['To'] = to_email
        part1 = MIMEText(html, 'html', 'utf-8')
        msg.attach(part1)
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            try:
                server.login(from_email, from_password)
                server.sendmail(from_email, to_email.split(','), msg.as_string())
                server.quit()
            except smtplib.SMTPAuthenticationError as e:
                raise smtplib.SMTPAuthenticationError('Username and Password not accepted' + str(e))
            except Exception as e:
                raise ConnectionError('Failed to send email. Exception:' + str(e))


MailHandler.send_mail()
