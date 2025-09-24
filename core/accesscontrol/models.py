from django.db import models

class AccessLog(models.Model):
    card_id = models.CharField(max_length=50, unique=True)
    door_name = models.CharField(max_length=100)
    access_granted = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "GRANTED" if self.access_granted else "DENIED"
        return f"{self.card_id} - {self.door_name} - {status} - {self.timestamp}"