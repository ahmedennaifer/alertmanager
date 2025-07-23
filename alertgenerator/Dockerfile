FROM python:3.10-alpine AS builder

WORKDIR /app

RUN apk add --no-cache gcc musl-dev linux-headers

COPY pyproject.toml .

RUN python -m venv .venv && \
    .venv/bin/pip install --no-cache-dir -e . --extra-index-url https://download.pytorch.org/whl/cpu

FROM python:3.10-alpine

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY src/ ./src/

ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "src/main.py"]
