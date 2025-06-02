FROM python:3.11-slim

# Install build dependencies for Rust-based packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    rustc \
    cargo \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .


CMD ["sh","/bin/sh"]