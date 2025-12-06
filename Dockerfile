FROM python:3.14-alpine
RUN apk add uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY . .

CMD [ "uv", "run", "main.py" ]
