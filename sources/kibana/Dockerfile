# Dockerfile for the publisher application.
FROM python:3

RUN pip install pika

# Without this setting, Python never prints anything out.
ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app
COPY errors_last_3_hours.csv .
COPY kibanaEvents.py .

CMD ["python3", "/usr/src/app/kibanaEvents.py"]
