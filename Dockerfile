From python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY day5_stream.py .

EXPOSE 8000

CMD ["uvicorn","day5_stream:app", "--host","0.0.0.0","--port","8000"]