FROM python:3.11-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY keybroker ./keybroker

RUN mkdir -p /etc/keybroker /var/lib/keybroker /var/log/keybroker

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -fsS http://localhost:8000/healthz || exit 1

CMD ["uvicorn", "keybroker.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
