from django.apps import AppConfig
import os

class TrackingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tracking'
    # scheduling adding score tasks
    def ready(self):
        if os.environ.get("RUN_MAIN"):
            import tracking.signals
            from .scheduler import start
            print("Starting Scheduler from appconfig")
            start()