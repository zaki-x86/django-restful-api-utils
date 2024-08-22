import threading
import queue
import smtplib
from os import path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.core.mail import send_mail

# Set those up in .env
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'   # Here I am using gmail smtp server 
# EMAIL_PORT = 587       # gmail smtp server port
# EMAIL_HOST_USER = 'username@mail.com'  # Use your email account
# EMAIL_HOST_PASSWORD = 'xxxxxxxxxxxxxxxx' # For gmail use app password
# EMAIL_USE_TLS = True     # for SSL communication use EMAIL_USE_SSL

class EmailService(threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.email_queue = queue.Queue()
        self.daemon = True
        
        self.host = settings.EMAIL_HOST
        self.port = settings.EMAIL_PORT
        self.username = settings.EMAIL_HOST_USER
        self.default_from =  settings.DEFAULT_FROM_EMAIL
        self.password = settings.EMAIL_HOST_PASSWORD
        self.use_tls = settings.EMAIL_USE_TLS
    
    def render_template(self, template_name, context):
        html_content = render_to_string(template_name, context)
        text_content = strip_tags(html_content)
        return text_content, html_content
    
    def set_attachment(self, file):
        part = MIMEBase('application', "octet-stream")
        part.set_payload(file.read())
        # extract filename from path
        encoders.encode_base64(part)
        filename = path.basename(file.name).split('/')[-1]
        part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
        return part
    
    def send_email(self, *args, **kwargs):
        print(f"kwargs: {kwargs}")
        print(f"args: {args}")
        print(f"self.host= {self.host}")
        print(f"self.port= {self.port}")
        print(f"self.username= {self.username}")

        # User may provide both text and html version of the message
        if kwargs.get("text", None) and kwargs.get("html", None):
            msg = MIMEMultipart('alternative')
            text_content = kwargs.get("text")
            html_content = kwargs.get("html")
            msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))
        # User provides plain text as message
        elif kwargs.get("text", None):
            msg = MIMEText(kwargs.get("text"), 'plain')
        # User provides html as message
        elif kwargs.get("html", None):
            msg = MIMEText(kwargs.get("html"), 'html')
        # User provides template name (path) to render
        elif kwargs.get("template", None):
            text_content, html_content = self.render_template(kwargs.get("template"), kwargs.get("context", {}))
            msg = MIMEMultipart('alternative')
            msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))
        
        # attachments are supplied as [{'file_content': ..., 'file_name': ...}, ...]
        if kwargs.get("attachments", None):
            msg = MIMEMultipart()
            if kwargs.get("attachments", None):
                for file in kwargs.get("attachments"):
                    part = self.set_attachment(file)
                    print(f"part: {part}")
                    msg.attach(part)            
        
        msg['Subject'] = kwargs.get("subject", "No subject")
        msg['From'] = self.username
        if kwargs.get("recipients", None) or kwargs.get("to", None):
            recipients = kwargs.get("recipients")
            if not isinstance(recipients, list):
                recipients = [recipients]
            msg['To'] = ', '.join(recipients)
        else:
            raise Exception("No recipients provided")
        
        with smtplib.SMTP_SSL(self.host, self.port) as smtp_server:
            smtp_server.login(self.username, self.password)
            smtp_server.sendmail(self.username, recipients, msg.as_string())
            smtp_server.quit()
        print("Message sent!")
    
    def run(self):
        while True:
            try:
                email_data = self.email_queue.get()
                self.send_email(**email_data)
                self.email_queue.task_done()
            except Exception as e:
                print(f"Error sending email: {e}")
    
    def send(self, *args, **kwargs):
        self.email_queue.put(kwargs)