FROM python:3

RUN pip install pika
RUN pip install requests

WORKDIR /usr/src/app
COPY  webConsumer.py .

CMD ["python3", "-u", "/usr/src/app/webConsumer.py"]
