
# Access Control System

A Django REST API for logging and managing door access events with real-time system event tracking.

## Features

- **RESTful API** - Full CRUD operations for access logs
- **Real-time Event Logging** - Automatic system event tracking via Django signals
- **Advanced Filtering** - Filter by card ID, door name, and access status
- **Docker Support** - Containerized deployment ready
- **Comprehensive Testing** - Full test coverage for all endpoints
## Installation

 **1. Clone and setup**
   ```bash
   git clone <repository-url>
   cd AccessControlSystem
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
 **2. Install dependencies**
   ```bash
   uv sync
   ```
**3. Database Management**

- Create migrations
   ```bash
   python manage.py migrate
   ```
- Apply migrations

    ```bash
   python manage.py migrate
    ```

## Run Server
```bash
python manage.py runserver
```
## Running Tests

To run tests, run the following command

```bash
python manage.py test core.accesscontrol.tests

```


## Docker Deployment

Build image
```bash
docker build -t access-control-system .
```
Run container
``` bash
docker run -d -p 8000:8000 access-control-system
```