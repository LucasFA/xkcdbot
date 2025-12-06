FROM python:3.14-alpine

COPY . .
RUN apk add uv

CMD [ "uv", "run", "main.py" ]
