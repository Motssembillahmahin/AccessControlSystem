from django.db import models


class AccessLog(models.Model):
    card_id = models.CharField(max_length=50)
    door_name = models.CharField(max_length=100)
    access_granted = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "GRANTED" if self.access_granted else "DENIED"
        return f"{self.card_id} - {self.door_name} - {status} - {self.timestamp}"


class AnomalyAlert(models.Model):
    class Rule(models.TextChoices):
        AFTER_HOURS = "AFTER_HOURS", "After Hours Access"
        DENIAL_BURST = "DENIAL_BURST", "Denial Burst"
        MULTI_DOOR = "MULTI_DOOR", "Multi-Door Rapid Access"
        STAT_OUTLIER = "STAT_OUTLIER", "Statistical Outlier"

    class RiskLevel(models.TextChoices):
        HIGH = "HIGH", "High"
        MEDIUM = "MEDIUM", "Medium"
        LOW = "LOW", "Low"

    access_log = models.ForeignKey(
        AccessLog,
        on_delete=models.SET_NULL,
        null=True,
        related_name="anomalies",
    )
    card_id = models.CharField(max_length=50)
    door_name = models.CharField(max_length=100)
    rule = models.CharField(max_length=20, choices=Rule.choices)
    risk_level = models.CharField(max_length=10, choices=RiskLevel.choices)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"[{self.risk_level}] {self.rule} — {self.card_id} at {self.timestamp}"