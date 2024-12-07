FROM python:3.11-slim

# Install dependencies required to build psycopg2 from source
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

CMD ["flask", "run"]