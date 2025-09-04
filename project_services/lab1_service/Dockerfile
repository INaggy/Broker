FROM python:3.9-slim

WORKDIR /app

COPY app.py .

COPY Lab1.py .

COPY requirements.txt .

RUN pip install -r requirements.txt

CMD ["python", "app.py"]
