FROM python:3

RUN pip install pika
RUN pip install pandas

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app
COPY gateway.py .

CMD ["python3", "/usr/src/app/gateway.py"]
