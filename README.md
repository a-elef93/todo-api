# todo-api

[![CI](https://github.com/a-elef93/todo-api/actions/workflows/ci.yml/badge.svg)](https://github.com/a-elef93/todo-api/actions/workflows/ci.yml)

A small REST API for managing to-do items, built with **Flask** and **PostgreSQL**, containerized with **Docker Compose** and shipped through a **GitHub Actions** CI/CD pipeline to **GitHub Container Registry (GHCR)**.

The application itself is intentionally simple. The focus of this project is the delivery workflow around it: containers, health-gated startup, automated tests, secret handling, and an image that is only published when every check passes.

## Tech stack

| Area | Tools |
|---|---|
| Application | Python 3.11, Flask, psycopg2 |
| Database | PostgreSQL 16 |
| Containers | Docker, Docker Compose |
| Tests | pytest, unittest.mock |
| CI/CD | GitHub Actions, GHCR |

## API

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Liveness check, returns `ok` (does not touch the database) |
| `POST` | `/todos` | Create a todo. Body: `{"title": "buy milk"}`. Returns `201` |
| `GET` | `/todos` | List all todos |

Example:

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"title":"buy milk"}' localhost:5000/todos
# {"id":1,"title":"buy milk"}

curl localhost:5000/todos
# [{"id":1,"title":"buy milk"}]
```

## Run it locally

Requirements: Docker with the Compose plugin.

1. Clone the repository:

   ```bash
   git clone https://github.com/a-elef93/todo-api.git
   cd todo-api
   ```

2. Create a `.env` file with the database settings (it is git-ignored and never committed):

   ```
   DB_NAME=tododb
   DB_USER=todo
   DB_PASSWORD=choose-a-password
   ```

3. Start the stack:

   ```bash
   docker compose up -d --build
   curl localhost:5000/health
   ```

The PostgreSQL data lives in a named volume, so todos survive `docker compose down` and `docker compose up`. Use `docker compose down -v` to wipe the data as well.

## Run the tests

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt pytest
pytest -v
```

The unit tests replace the database connection with a mock, so they need no running database and finish in a fraction of a second.

## CI/CD pipeline

Every push to `main` triggers the workflow in `.github/workflows/ci.yml`:

```
        push to main
             |
     +-------+--------+
     |                |
 unit-test           test              (run in parallel)
 pytest            docker compose up
                   + smoke test
     |                |
     +-------+--------+
             |
           push                        (only if both passed)
   build image -> GHCR (latest + commit SHA)
```

| Job | What it does |
|---|---|
| `unit-test` | Installs dependencies on a clean runner and runs pytest |
| `test` | Builds and starts the full stack with Compose, then smoke-tests the live API (`/health`, `POST /todos`, `GET /todos`) with retries to absorb startup timing. Prints the container logs if anything fails |
| `push` | Runs only if both previous jobs succeed. Logs in to GHCR and publishes the image |

Verified behavior: when a unit test or the smoke test fails, the `push` job is skipped and no image is published.

### Pull the published image

```bash
docker pull ghcr.io/a-elef93/todo-api:latest
```

Each build is also tagged with the commit SHA (`ghcr.io/a-elef93/todo-api:<sha>`), which allows tracing an image back to the exact commit and rolling back to a known good version.

## Design decisions

- **Health-gated startup.** The database service has a `pg_isready` healthcheck and the app waits for it with `depends_on: condition: service_healthy`, avoiding a race where the app starts before PostgreSQL accepts connections.
- **No credentials in the repository.** Database settings come from environment variables. Locally they are read from a git-ignored `.env`; in CI the password comes from a GitHub Actions secret.
- **Least privilege in CI.** Only the `push` job gets `packages: write`, and it authenticates with the short-lived `GITHUB_TOKEN` generated for the run.
- **Fast, isolated unit tests.** The database is mocked, so the unit stage fails quickly and independently of the smoke test.
- **Cache-friendly Dockerfile.** `requirements.txt` is copied and installed before the application code, so code changes do not reinstall dependencies.

## Project structure

```
.
├── app.py                  # Flask application
├── test_app.py             # Unit tests (mocked database)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml      # app + PostgreSQL
└── .github/workflows/
    └── ci.yml              # CI/CD pipeline
```
[![CI](https://github.com/a-elef93/todo-api/actions/workflows/ci.yml/badge.svg)](https://github.com/a-elef93/todo-api/actions/workflows/ci.yml)

# to-do api
A small REST API for managing to-do items, built with Flask and PostgreSQL, containerized with Docker Compose and shipped through a GitHub Actions CI/CD pipeline to GitHub Container Registry (GHCR).

The application itself is intentionally simple. The focus of this project is the delivery workflow around it: containers, health-gated startup, automated tests, secret handling, and an image that is only published when every check passes.

Tech stack
Area	Tools
Application	Python 3.11, Flask, psycopg2
Database	PostgreSQL 16
Containers	Docker, Docker Compose
Tests	pytest, unittest.mock
CI/CD	GitHub Actions, GHCR
API
Method	Endpoint	Description
GET	/health	Liveness check, returns ok (does not touch the database)
POST	/todos	Create a todo. Body: {"title": "buy milk"}. Returns 201
GET	/todos	List all todos

Example:

bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"title":"buy milk"}' localhost:5000/todos
# {"id":1,"title":"buy milk"}

curl localhost:5000/todos
# [{"id":1,"title":"buy milk"}]
Run it locally

Requirements: Docker with the Compose plugin.

Clone the repository:
bash
   git clone https://github.com/a-elef93/todo-api.git
   cd todo-api
Create a .env file with the database settings (it is git-ignored and never committed):
   DB_NAME=tododb
   DB_USER=todo
   DB_PASSWORD=choose-a-password
Start the stack:
bash
   docker compose up -d --build
   curl localhost:5000/health

The PostgreSQL data lives in a named volume, so todos survive docker compose down and docker compose up. Use docker compose down -v to wipe the data as well.

Run the tests
bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt pytest
pytest -v

The unit tests replace the database connection with a mock, so they need no running database and finish in a fraction of a second.

CI/CD pipeline

Every push to main triggers the workflow in .github/workflows/ci.yml:

        push to main
             |
     +-------+--------+
     |                |
 unit-test           test              (run in parallel)
 pytest            docker compose up
                   + smoke test
     |                |
     +-------+--------+
             |
           push                        (only if both passed)
   build image -> GHCR (latest + commit SHA)
Job	What it does
unit-test	Installs dependencies on a clean runner and runs pytest
test	Builds and starts the full stack with Compose, then smoke-tests the live API (/health, POST /todos, GET /todos) with retries to absorb startup timing. Prints the container logs if anything fails
push	Runs only if both previous jobs succeed. Logs in to GHCR and publishes the image

Verified behavior: when a unit test or the smoke test fails, the push job is skipped and no image is published.

Pull the published image
bash
docker pull ghcr.io/a-elef93/todo-api:latest

Each build is also tagged with the commit SHA (ghcr.io/a-elef93/todo-api:<sha>), which allows tracing an image back to the exact commit and rolling back to a known good version.

Design decisions
Health-gated startup. The database service has a pg_isready healthcheck and the app waits for it with depends_on: condition: service_healthy, avoiding a race where the app starts before PostgreSQL accepts connections.
No credentials in the repository. Database settings come from environment variables. Locally they are read from a git-ignored .env; in CI the password comes from a GitHub Actions secret.
Least privilege in CI. Only the push job gets packages: write, and it authenticates with the short-lived GITHUB_TOKEN generated for the run.
Fast, isolated unit tests. The database is mocked, so the unit stage fails quickly and independently of the smoke test.
Cache-friendly Dockerfile. requirements.txt is copied and installed before the application code, so code changes do not reinstall dependencies.
Project structure
.
├── app.py                  # Flask application
├── test_app.py             # Unit tests (mocked database)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml      # app + PostgreSQL
└── .github/workflows/
    └── ci.yml              # CI/CD pipeline
