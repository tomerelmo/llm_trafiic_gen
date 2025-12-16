FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y curl wget gnupg ca-certificates && rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m playwright install --with-deps chromium

COPY src ./src
COPY entrypoint.sh ./entrypoint.sh

ENV PATH="/app:${PATH}" \
    PYTHONPATH=/app/src

ENTRYPOINT ["/app/entrypoint.sh"]
CMD []
