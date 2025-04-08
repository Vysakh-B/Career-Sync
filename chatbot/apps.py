from django.apps import AppConfig

class ChatbotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chatbot'

    def ready(self):
        # Import signals or Celery-related stuff here
        import django_celery_beat.schedulers  # ensures scheduler is registered
