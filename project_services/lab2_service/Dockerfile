FROM python:3.9-slim

WORKDIR /app

COPY app.py .

COPY neo4j_sync.py .

COPY requirements.txt .

RUN pip install -r requirements.txt

CMD ["python", "app.py"]
