import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accesscontrol", "0001_initial"),
    ]

    operations = [
        # Remove the unique constraint on card_id so a card can have
        # multiple access log entries (required for event history).
        migrations.AlterField(
            model_name="accesslog",
            name="card_id",
            field=models.CharField(max_length=50),
        ),
        migrations.CreateModel(
            name="AnomalyAlert",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("card_id", models.CharField(max_length=50)),
                ("door_name", models.CharField(max_length=100)),
                (
                    "rule",
                    models.CharField(
                        choices=[
                            ("AFTER_HOURS", "After Hours Access"),
                            ("DENIAL_BURST", "Denial Burst"),
                            ("MULTI_DOOR", "Multi-Door Rapid Access"),
                            ("STAT_OUTLIER", "Statistical Outlier"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "risk_level",
                    models.CharField(
                        choices=[
                            ("HIGH", "High"),
                            ("MEDIUM", "Medium"),
                            ("LOW", "Low"),
                        ],
                        max_length=10,
                    ),
                ),
                ("description", models.TextField()),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("resolved", models.BooleanField(default=False)),
                (
                    "access_log",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="anomalies",
                        to="accesscontrol.accesslog",
                    ),
                ),
            ],
        ),
    ]
