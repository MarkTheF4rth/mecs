FROM python:3

RUN pip install requests[security]
RUN pip install flask
RUN pip install flask-cors
RUN pip install pika

WORKDIR /usr/src/app
COPY webApi.py .

EXPOSE 5000

CMD ["python3", "-u", "/usr/src/app/webApi.py"]
