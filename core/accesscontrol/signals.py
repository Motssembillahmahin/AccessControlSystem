import subprocess
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import AccessLog


@receiver(post_save, sender=AccessLog)
def log_access_creation(sender, instance, created, **kwargs):
    if created:
        status = "GRANTED" if instance.access_granted else "DENIED"
        log_message = f"[{instance.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] - CREATE: Access log created for card {instance.card_id}. Status: {status}."

        subprocess.run([
            'echo', log_message
        ], shell=True)

        with open('system_events.log', 'a') as f:
            f.write(log_message + '\n')


@receiver(post_delete, sender=AccessLog)
def log_access_deletion(sender, instance, **kwargs):
    log_message = f"[{instance.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] - DELETE: Access log (ID: {instance.id}) for card {instance.card_id} was deleted."

    subprocess.run([
        'echo', log_message
    ], shell=True)

    with open('system_events.log', 'a') as f:
        f.write(log_message + '\n')