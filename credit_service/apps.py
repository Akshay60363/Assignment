from django.apps import AppConfig


class CreditServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'credit_service'
    
    def ready(self):
        import credit_service.tasks  # noqa