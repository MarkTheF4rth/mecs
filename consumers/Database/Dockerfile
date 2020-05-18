FROM python:3

RUN pip install pika

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app
COPY databaseHelper.py .
COPY databaseSetup.py .
COPY storeEvents.py .

CMD ["python3", "/usr/src/app/storeEvents.py"]
