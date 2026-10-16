FROM python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

COPY pyproject.toml ./
COPY src ./src

RUN pip install --no-cache-dir "mistralai-workflows>=3.10" "mistralai"

CMD ["python", "-m", "lead_router.worker"]
