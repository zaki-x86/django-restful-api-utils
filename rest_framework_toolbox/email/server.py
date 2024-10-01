import threading
import queue
import smtplib
from os import path, getenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from dotenv import load_dotenv
from datetime import datetime, timedelta



# Set those up in .env
# EMAIL_HOST = 'smtp.gmail.com'   # Here I am using gmail smtp server 
# EMAIL_PORT = 587       # gmail smtp server port
# EMAIL_HOST_USER = 'username@mail.com'  # Use your email account
# EMAIL_HOST_PASSWORD = 'xxxxxxxxxxxxxxxx' # For gmail use app password
# EMAIL_USE_TLS = True     # for SSL communication use EMAIL_USE_SSL

class SMTPService(threading.Thread):
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(SMTPService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.email_queue = queue.Queue()
        self.daemon = True
        self.count = 0
        self.logger = None
        
        EMAIL_HOST = kwargs.pop('EMAIL_HOST', 'smtp.gmail.com')
        EMAIL_PORT = kwargs.pop('EMAIL_PORT', 465)
        EMAIL_HOST_USER = kwargs.pop('EMAIL_HOST_USER', None)
        EMAIL_HOST_PASSWORD = kwargs.pop('EMAIL_HOST_PASSWORD', None)
        DEFAULT_FROM_EMAIL = kwargs.pop('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)
        EMAIL_USE_TLS = kwargs.pop('EMAIL_USE_TLS', True)

        self.lock = threading.Lock()

        load_dotenv()

        self.host = getenv(
            'EMAIL_HOST', EMAIL_HOST)
        self.port = getenv(
            'EMAIL_PORT', EMAIL_PORT)
        self.username = getenv(
            'EMAIL_HOST_USER', EMAIL_HOST_USER)
        self.default_from =  getenv(
            'DEFAULT_FROM_EMAIL', DEFAULT_FROM_EMAIL)
        self.password = getenv(
            'EMAIL_HOST_PASSWORD', EMAIL_HOST_PASSWORD)
        self.use_tls = getenv(
            'EMAIL_USE_TLS', 
            EMAIL_USE_TLS)

        if not self.host or not self.port or not self.username or not self.password:
            raise Exception("Email credentials not provided")
    
    def set_attachment(self, file):
        part = MIMEBase('application', "octet-stream")
        part.set_payload(file.read())
        # extract filename from path
        encoders.encode_base64(part)
        filename = path.basename(file.name).split('/')[-1]
        part.add_header('Content-Disposition', f'attachment; filename="{filename}"')

        return part
    
    def send_email(self, *args, **kwargs):
        msg = MIMEMultipart()
        # User may provide both text and html version of the message
        if kwargs.get("text", None) and kwargs.get("html", None):
            msg = MIMEMultipart('alternative')
            text_content = kwargs.get("text")
            html_content = kwargs.get("html")
            msg.attach(MIMEText(html_content, 'html'))
            msg.attach(MIMEText(text_content, 'plain'))
        # User provides plain text as message
        elif kwargs.get("text", None):
            msg.attach(MIMEText(kwargs.get("text"), 'plain'))
        # User provides html as message
        elif kwargs.get("html", None):
            msg = msg.attach(MIMEText(kwargs.get("html"), 'html'))
        # User provides template name (path) to render
        else:
            raise Exception("No message content provided")

        # attachments are supplied as [FILE, ...] where FILE implements .read() and .name
        if kwargs.get("attachments", None):
            if kwargs.get("attachments", None):
                for file in kwargs.get("attachments"):
                    if getattr(file, 'read', None) and getattr(file, 'name', None):
                        part = self.set_attachment(file)
                    else:
                        raise Exception("Invalid file object provided")
                    msg.attach(part)            
        
        if kwargs.get("recipients", None) or kwargs.get("to", None):
            recipients = kwargs.get("recipients")
            if not recipients:
                recipients = kwargs.get("to")
            if not isinstance(recipients, list):
                recipients = [recipients]
            msg['To'] = ', '.join(recipients)
        else:
            raise Exception("No recipients provided")
        
        msg['Subject'] = kwargs.get("subject", "No subject")
        if self.username or self.default_from:
            if not self.username:
                self.username = self.default_from
            msg['From'] = self.username
        else:
            raise Exception("No from address provided")
        
        with smtplib.SMTP_SSL(self.host, self.port) as smtp_server:
            smtp_server.login(self.username, self.password)
            smtp_server.sendmail(self.username, recipients, msg.as_string())
            smtp_server.quit()
            print("Message sent!")
    
    def run(self):
        while True:
            try:
                if self.email_queue.empty():
                    continue
                if self.count == 5000:
                    continue
                
                email_data = self.email_queue.get()
                self.send_email(**email_data)
                self.email_queue.task_done()
                self.increment_counter() 
            except Exception as e:
                print(f"Error sending email: {e}")
    
    def send(self, *args, **kwargs):
        #TODO validate `kwargs
        self.email_queue.put(kwargs)
        
    def increment_counter(self):
        with self.lock:  # Lock to ensure atomic increment
            self.count += 1
            print(f"Emails sent: {self.count}")
