FROM python:3.14-alpine
RUN apk add uv --no-cache

WORKDIR /app

RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup appuser && \
    chown -R appuser:appgroup /app
USER appuser

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY . .

CMD [ "uv", "run", "main.py", "--no-dev" ]
