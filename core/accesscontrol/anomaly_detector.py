"""
Anomaly Detector
----------------
Z-score + rule-based hybrid engine that checks every new AccessLog entry
for suspicious patterns. Called from the post_save Django signal — zero
extra infrastructure required.

Rules
-----
AFTER_HOURS    Access between 20:00–06:00 UTC                              MEDIUM
DENIAL_BURST   Same card denied ≥3 times within 10 minutes                 HIGH
MULTI_DOOR     Same card accesses ≥3 different doors within 5 minutes      HIGH
STAT_OUTLIER   Current-hour access count is >3σ above card's own baseline  MEDIUM

The STAT_OUTLIER rule is the "AI" piece: it learns each card's personal
hourly access baseline and flags deviations — not a global threshold, but
a per-entity behavioural model.
"""

import math
from datetime import timedelta

from django.db.models import Count
from django.db.models.functions import TruncHour

# ── Thresholds ─────────────────────────────────────────────────────────────────
AFTER_HOURS_START = 20          # 8 PM UTC
AFTER_HOURS_END = 6             # 6 AM UTC
DENIAL_BURST_THRESHOLD = 3      # denials within window
DENIAL_BURST_WINDOW = 10        # minutes
MULTI_DOOR_THRESHOLD = 3        # distinct doors within window
MULTI_DOOR_WINDOW = 5           # minutes
Z_SCORE_THRESHOLD = 3.0         # standard deviations above mean
MIN_HISTORY_HOURS = 5           # minimum hourly buckets for z-score


def _std_dev(values: list) -> float:
    """Population standard deviation."""
    n = len(values)
    if n < 2:
        return 0.0
    mean = sum(values) / n
    return math.sqrt(sum((v - mean) ** 2 for v in values) / n)


class AnomalyDetector:
    """
    Run all anomaly rules against a single AccessLog instance.

    Usage:
        detector = AnomalyDetector(access_log_instance)
        alerts = detector.check_all()   # returns list of AnomalyAlert instances
    """

    def __init__(self, access_log):
        self.log = access_log
        self.card_id = access_log.card_id
        self.door_name = access_log.door_name
        self.ts = access_log.timestamp
        self.granted = access_log.access_granted

    def check_all(self) -> list:
        """Run every rule and return a (possibly empty) list of saved AnomalyAlert objects."""
        from .models import AccessLog, AnomalyAlert  # avoid circular import at module level

        findings = [
            self._check_after_hours(),
            self._check_denial_burst(AccessLog),
            self._check_multi_door(AccessLog),
            self._check_stat_outlier(AccessLog),
        ]

        created = []
        for finding in findings:
            if finding is None:
                continue
            rule, risk_level, description = finding
            alert = AnomalyAlert.objects.create(
                access_log=self.log,
                card_id=self.card_id,
                door_name=self.door_name,
                rule=rule,
                risk_level=risk_level,
                description=description,
            )
            created.append(alert)

        return created

    # ── Rules ──────────────────────────────────────────────────────────────────

    def _check_after_hours(self):
        hour = self.ts.hour
        outside = hour >= AFTER_HOURS_START or hour < AFTER_HOURS_END
        if not outside:
            return None
        return (
            "AFTER_HOURS",
            "MEDIUM",
            f"Card {self.card_id} accessed '{self.door_name}' at "
            f"{self.ts.strftime('%H:%M UTC')} — outside normal hours (06:00–20:00 UTC).",
        )

    def _check_denial_burst(self, AccessLog):
        if self.granted:
            return None
        window_start = self.ts - timedelta(minutes=DENIAL_BURST_WINDOW)
        count = AccessLog.objects.filter(
            card_id=self.card_id,
            access_granted=False,
            timestamp__gte=window_start,
            timestamp__lte=self.ts,
        ).count()
        if count < DENIAL_BURST_THRESHOLD:
            return None
        return (
            "DENIAL_BURST",
            "HIGH",
            f"Card {self.card_id} was denied {count} times within "
            f"{DENIAL_BURST_WINDOW} minutes — possible forced entry attempt.",
        )

    def _check_multi_door(self, AccessLog):
        window_start = self.ts - timedelta(minutes=MULTI_DOOR_WINDOW)
        doors = set(
            AccessLog.objects.filter(
                card_id=self.card_id,
                timestamp__gte=window_start,
                timestamp__lte=self.ts,
            ).values_list("door_name", flat=True)
        )
        if len(doors) < MULTI_DOOR_THRESHOLD:
            return None
        return (
            "MULTI_DOOR",
            "HIGH",
            f"Card {self.card_id} accessed {len(doors)} different doors "
            f"within {MULTI_DOOR_WINDOW} minutes — possible tailgating or credential sharing.",
        )

    def _check_stat_outlier(self, AccessLog):
        current_hour_start = self.ts.replace(minute=0, second=0, microsecond=0)

        # How many times has this card accessed anything in the current hour?
        current_count = AccessLog.objects.filter(
            card_id=self.card_id,
            timestamp__gte=current_hour_start,
            timestamp__lte=self.ts,
        ).count()

        # Historical hourly access counts (all hours before the current one)
        historical = list(
            AccessLog.objects.filter(
                card_id=self.card_id,
                timestamp__lt=current_hour_start,
            )
            .annotate(hour=TruncHour("timestamp"))
            .values("hour")
            .annotate(count=Count("id"))
            .values_list("count", flat=True)
        )

        if len(historical) < MIN_HISTORY_HOURS:
            return None

        mean = sum(historical) / len(historical)
        std = _std_dev(historical)

        if std == 0:
            return None

        z = (current_count - mean) / std
        if z <= Z_SCORE_THRESHOLD:
            return None

        return (
            "STAT_OUTLIER",
            "MEDIUM",
            f"Card {self.card_id} has {current_count} accesses this hour — "
            f"{z:.1f}σ above its personal baseline of {mean:.1f} accesses/hour.",
        )
