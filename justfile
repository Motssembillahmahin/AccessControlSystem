default:
  just --list

run:
  python manage.py runserver
app *args:
    python manage.py startapp {{args}}
ruff *args:
  ruff check {{args}} src

lint:
  ruff format src
  just ruff --fix

# migrate
migrate:
    python manage.py migrate

# docker
up:
  docker-compose up -d

kill *args:
  docker-compose kill {{args}}

build:
  docker-compose build

ps:
  docker-compose ps

pre-commit:
  git add .
  pre-commit run --all-files
