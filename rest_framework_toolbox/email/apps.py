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
        from .server import SMTPService
        self.service = SMTPService()
        self.service.start()

from .server import SMTPService

email_service = SMTPService._instance
