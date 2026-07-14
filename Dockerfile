FROM python:3.13-slim

WORKDIR /workspace/app

RUN apt-get update && apt-get install -y git
RUN pip install --no-cache-dir uv

COPY app/pyproject.toml app/uv.lock ./
RUN uv sync

COPY ./app .

EXPOSE 8000

CMD ["uv", "run", "fastapi", "dev", "main.py", "--host", "0.0.0.0", "--port", "8000"]
