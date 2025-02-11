FROM python:3.12-slim

RUN pip install --no-cache-dir poetry

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --without dev

COPY log_analyzer/ log_analyzer/
COPY logger/ logger/
COPY log/ log/
COPY config/ config/

VOLUME ["/app/log", "/app/reports", "/app/config", "/app/app_logs"]
ENTRYPOINT ["poetry", "run", "python", "-m", "log_analyzer.log_analyzer"]
