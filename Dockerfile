FROM python:3.14-alpine
RUN apk add uv

COPY . .

CMD [ "uv", "run", "main.py" ]
