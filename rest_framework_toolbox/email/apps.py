from typing import Any
from django.apps import AppConfig


class EmailConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rest_framework_toolbox.email'
    label = 'rest_framework_toolbox_email'

    def __init__(self, app_name: str, app_module) -> None:
        super().__init__(app_name, app_module)
        self.service = None

    def ready(self) -> None:
        from  django.conf import settings
        from .server import SMTPService
        
        self.service = SMTPService(
            EMAIL_HOST = settings.EMAIL_HOST, 
            EMAIL_PORT = settings.EMAIL_PORT, 
            EMAIL_HOST_USER = settings.EMAIL_HOST_USER, 
            EMAIL_HOST_PASSWORD = settings.EMAIL_HOST_PASSWORD,
            EMAIL_USE_TLS = settings.EMAIL_USE_TLS
        )
        self.service.start()

from .server import SMTPService

email_service = SMTPService._instance
