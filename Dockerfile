FROM python:3.11-slim

WORKDIR /app

RUN mkdir -p /app/files

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 48000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "48000"]
