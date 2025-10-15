FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN cp .env.example .env

EXPOSE 5000

CMD ["python3", "app.py"]
