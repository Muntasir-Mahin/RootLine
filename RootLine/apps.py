from django.apps import AppConfig


class RootlineConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "RootLine"

    def ready(self):
        import RootLine.signals