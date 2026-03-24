FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git \
 && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
