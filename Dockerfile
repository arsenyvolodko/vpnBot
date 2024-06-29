FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    wireguard-tools \
    iproute2 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry==1.7.1

ENV POETRY_VIRTUALENVS_CREATE=false

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-ansi
COPY . .

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH='/app'

RUN chmod +x /app/wireguard_tools/sync_config.sh
RUN chmod +x /app/wireguard_tools/up_wg_configs.sh

RUN mkdir /app/vpnBot/tmp_client_files
RUN chmod -R 755 /app/vpnBot/tmp_client_files