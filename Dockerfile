FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y gettext && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install gunicorn

COPY . /app/
COPY start.sh /app/
RUN chmod +x /app/start.sh

EXPOSE 8000

RUN mkdir -p /app/media /app/staticfiles

CMD ["/app/start.sh"]
