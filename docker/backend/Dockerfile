FROM python:3.12-slim

# no .pyc files and no output buffering, so logs show up right away
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# requirements first, so docker can cache this layer when only code changes
COPY src/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/backend/ .

COPY docker/backend/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# daphne listens here, nginx connects to it
EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
