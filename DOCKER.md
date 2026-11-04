# Docker setup

Whole app runs in containers, one command, https only.

## Quick start

```
cp .env.example .env     # fill SECRET_KEY and POSTGRES_PASSWORD
docker compose up -d --build
```

Open https://localhost. Browser will warn about the certificate (self-signed), just continue.

`make` is only a shortcut for the same commands, you don't need it.

## Containers

| Name | Image | What it does |
|---|---|---|
| nginx | built from `docker/nginx/Dockerfile` | only entry point (port 443), https, serves built react app, passes `/api` and `/admin` to backend |
| backend | built from `docker/backend/Dockerfile` | django on daphne (ASGI), runs `migrate` and `collectstatic` on start |
| db | `postgres:16-alpine` | database, data in volume `postgres_data` |
| redis | `redis:7-alpine` | for django channels (websockets), not used yet |

Only nginx is open to the outside. The rest talk to each other by name (`backend`, `db`, `redis`) inside the docker network.

## Files

```
docker-compose.yml            all services, volumes, network
.env.example                  template of config, real .env is ignored by git
Makefile                      shortcuts (up, down, logs, clean, re)
docker/backend/Dockerfile     python image with our django code
docker/backend/entrypoint.sh  migrate + collectstatic + start daphne
docker/nginx/Dockerfile       builds react, adds nginx and tls certificate
docker/nginx/nginx.conf       https, proxy rules, react fallback
```

## Commands

```
docker compose up -d --build     start (rebuilds changed images)
docker compose down              stop, data stays
docker compose down -v           stop and delete database
docker compose logs -f backend   logs of one service
docker compose ps                what is running
```

Same with make: `make up`, `make down`, `make clean` (deletes database), `make re` (from scratch), `make logs`.

Admin user:

```
docker compose exec backend python manage.py createsuperuser
```

Then log in at https://localhost/admin/. Swagger is at https://localhost/api/docs/.

## .env

| Variable | Meaning |
|---|---|
| HTTPS_PORT | port on your machine, default 443 (if busy use 8443 and add it to `CSRF_TRUSTED_ORIGINS`) |
| SECRET_KEY | django secret, required (app won't start without it) |
| DEBUG | `False` in containers |
| ALLOWED_HOSTS | hosts django answers to |
| CSRF_TRUSTED_ORIGINS | needed for admin login over https |
| POSTGRES_DB / USER / PASSWORD | used by db container and by django |
| DB_HOST / DB_PORT | `db` / `5432` |

Never commit `.env`.

## After changing code

Code is copied into the image, so changes need a rebuild:

```
docker compose up -d --build backend     after backend change
docker compose up -d --build nginx       after frontend change
```

New python package: add it to `src/backend/requirements.txt` and rebuild backend.

## Notes for the team

**Backend (websockets):** `daphne` is already the server and redis is already running. Missing part: add channels to django, set `CHANNEL_LAYERS` with host `redis`. Nginx already passes `/ws/` to backend, so use that prefix in routing (or change it in `docker/nginx/nginx.conf`).

**Frontend:** call the api with relative paths (`/api/...`), nginx handles them, so no hardcoded host or port. Vite dev server (`npm run dev`) has no proxy to the backend, so for testing with api use docker.

**Running django without docker:** `SECRET_KEY` is required now. Copy `.env.example` to `.env`, remove the `POSTGRES_*` and `DB_*` lines and django uses sqlite like before.

## Problems

- `docker: command not found` in `make`: docker is not in PATH, add the docker `resources\bin` folder to PATH and open a new terminal.
- port 443 busy: set `HTTPS_PORT=8443` in `.env`, open https://localhost:8443.
- admin login gives 403: check `CSRF_TRUSTED_ORIGINS` matches the address and port in the browser.
- backend restarts in a loop: check `docker compose logs backend` (usually missing `SECRET_KEY` in `.env`).
- want clean start: `make re` (deletes database too).
