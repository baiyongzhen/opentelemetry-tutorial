# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

RUN mkdir -p /app
WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY . /app

#CMD ["opentelemetry-instrument", "flask", "run","--port", "8082" "--host", "0.0.0.0"]
#EXPOSE 8082