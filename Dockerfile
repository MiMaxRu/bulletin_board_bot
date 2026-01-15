FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Use pip to install minimal runtime dependencies for faster, simpler builds
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "app.main"]
