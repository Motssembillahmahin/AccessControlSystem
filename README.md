# Access Control System

A Django REST API for logging and managing door access events with **real-time AI-powered anomaly detection**. Every access event is automatically analysed for suspicious behaviour — after-hours access, denial bursts, rapid multi-door traversal, and statistical deviations from a card's own historical baseline.

---

## Features

- **Full CRUD API** — create, read, update, and delete access log entries
- **Real-time anomaly detection** — 4 rules run automatically on every new event via Django signals, with zero added latency
- **Per-entity statistical baseline** — the Z-score rule learns each card's personal access pattern and flags deviations, not just global thresholds
- **Anomaly alert management** — list, filter, and resolve alerts via dedicated endpoints
- **Advanced filtering** — filter logs and alerts by card ID, door name, risk level, rule type, and resolved status
- **Event audit log** — all access events and anomaly detections written to `system_events.log`
- **Docker support** — containerised deployment ready

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Django 5.2 + Django REST Framework |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Filtering | django-filter |
| Anomaly Detection | Pure Python (Z-score + rule-based) |
| Dependency Management | uv |
| Linting | ruff |

---

## Architecture

```
POST /api/logs/
        ↓
  AccessLog saved to DB
        ↓ (Django post_save signal)
  log_access_creation()
        ↓
  AnomalyDetector.check_all()
        ├── AFTER_HOURS   check
        ├── DENIAL_BURST  check
        ├── MULTI_DOOR    check
        └── STAT_OUTLIER  check (Z-score vs card's personal baseline)
                ↓ (if triggered)
        AnomalyAlert.objects.create(...)
        AnomalyAlert written to system_events.log
```

---

## Anomaly Detection Rules

| Rule | Condition | Risk Level |
|------|-----------|-----------|
| `AFTER_HOURS` | Access between 20:00–06:00 UTC | MEDIUM |
| `DENIAL_BURST` | Same card denied ≥3 times in 10 minutes | HIGH |
| `MULTI_DOOR` | Same card accesses ≥3 different doors in 5 minutes | HIGH |
| `STAT_OUTLIER` | Current-hour access count is >3σ above card's historical hourly average | MEDIUM |

The `STAT_OUTLIER` rule builds a **per-card baseline** from historical data. If card `EMP-042` normally accesses 2 doors/hour but suddenly makes 15 accesses in one hour, that card is flagged — regardless of whether 15 is unusual for other cards.

---

## Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv)
- Docker & Docker Compose (optional)

---

## Installation

```bash
git clone https://github.com/Motssembillahmahin/AccessControlSystem.git
cd AccessControlSystem
make install
make migrate
make run
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | fallback key | Django secret key |
| `DEBUG` | `True` | Debug mode |
| `ALLOWED_HOSTS` | `127.0.0.1, localhost` | Allowed hosts |

---

## Usage

All commands run through `make`. Run `make help` to list every target.

```bash
make help           # List all commands
make install        # Install dependencies
make run            # Start dev server at http://localhost:8000
make migrate        # Apply migrations
make test           # Run test suite
make lint           # Lint with ruff
make format         # Format with ruff
make docker-up      # Start Docker services
make docker-down    # Stop Docker services
```

---

## API Reference

Interactive docs available at `http://localhost:8000/api/` (DRF browsable API).

### Access Logs

#### `POST /api/logs/`
Record a new door access event.

```json
{
  "card_id": "EMP-042",
  "door_name": "Server Room",
  "access_granted": true
}
```

**Response `201`:**
```json
{
  "id": 1,
  "card_id": "EMP-042",
  "door_name": "Server Room",
  "access_granted": true,
  "timestamp": "2026-04-03T14:22:00Z"
}
```

#### `GET /api/logs/`
List all access logs. Supports filtering:

| Query param | Example | Description |
|------------|---------|-------------|
| `card_id` | `?card_id=EMP-042` | Filter by card |
| `door_name` | `?door_name=Server+Room` | Filter by door |
| `access_granted` | `?access_granted=false` | Filter by status |
| `search` | `?search=EMP` | Full-text search |

#### `GET /api/logs/{id}/`
Retrieve a single log entry.

#### `PUT /api/logs/{id}/`
Update a log entry.

#### `DELETE /api/logs/{id}/`
Delete a log entry.

---

### Anomaly Alerts

#### `GET /api/anomalies/`
List all anomaly alerts, newest first.

| Query param | Example | Description |
|------------|---------|-------------|
| `card_id` | `?card_id=EMP-042` | Filter by card |
| `risk_level` | `?risk_level=HIGH` | `HIGH`, `MEDIUM`, `LOW` |
| `rule` | `?rule=DENIAL_BURST` | Filter by rule type |
| `resolved` | `?resolved=false` | Filter by resolved status |

**Response `200`:**
```json
[
  {
    "id": 3,
    "access_log": 17,
    "card_id": "EMP-042",
    "door_name": "Server Room",
    "rule": "DENIAL_BURST",
    "risk_level": "HIGH",
    "description": "Card EMP-042 was denied 4 times within 10 minutes — possible forced entry attempt.",
    "timestamp": "2026-04-03T02:14:00Z",
    "resolved": false
  }
]
```

#### `GET /api/anomalies/stats/`
Aggregated summary across all alerts.

**Response `200`:**
```json
{
  "total_alerts": 12,
  "unresolved_alerts": 5,
  "by_risk_level": { "HIGH": 4, "MEDIUM": 8 },
  "by_rule": { "AFTER_HOURS": 6, "DENIAL_BURST": 3, "MULTI_DOOR": 2, "STAT_OUTLIER": 1 },
  "top_risky_cards": [
    { "card_id": "EMP-042", "alert_count": 3 }
  ]
}
```

#### `PATCH /api/anomalies/{id}/resolve/`
Mark an alert as resolved.

**Response `200`:** Returns the updated alert object with `resolved: true`.

---

## Project Structure

```
AccessControlSystem/
├── Makefile                              # All project commands
├── requirements.txt                      # Python dependencies
├── config/
│   ├── settings/base.py                  # Django settings
│   └── urls.py                           # Root URL config
└── core/
    └── accesscontrol/
        ├── models.py                     # AccessLog + AnomalyAlert models
        ├── anomaly_detector.py           # Detection engine (Z-score + rules)
        ├── signals.py                    # post_save hook → runs detector
        ├── views.py                      # API views
        ├── serializers.py                # DRF serializers
        ├── urls.py                       # URL routing
        ├── tests.py                      # Test suite
        └── migrations/
            ├── 0001_initial.py
            └── 0002_remove_unique_card_id_add_anomalyalert.py
```

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit atomically with conventional prefixes (`feat:`, `fix:`, `chore:`, etc.)
4. Push and open a pull request against `main`
