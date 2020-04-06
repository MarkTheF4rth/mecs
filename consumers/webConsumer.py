import requests
import pika
import json

API_ENDPOINT = 'http://localhost:5000/update'

def postEvent(channel, method, properties, body):
    try:
        requests.post(url = API_ENDPOINT, data = body)
    except requests.exceptions.RequestException as e:
        print(e)
    channel.basic_ack(delivery_tag = method.delivery_tag)
    print('[x] Event posted!')

#RabbitMQ setup
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue = 'out.web', durable = True, auto_delete = True)
channel.basic_consume(queue = 'out.web', on_message_callback = postEvent)

print(' Waiting for events... press CTRL+C to terminate')
channel.start_consuming()