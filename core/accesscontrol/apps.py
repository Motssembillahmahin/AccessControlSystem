from django.apps import AppConfig

class AccesscontrolConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.accesscontrol'

    def ready(self):
        import core.accesscontrol.signals