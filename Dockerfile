FROM python:3.13-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

EXPOSE 8000
