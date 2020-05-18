import requests
import pika
import json
import os


class postWebEvents:
    def __init__(self, amqp_url, api_endpoint):
        self.api_endpoint = api_endpoint
        #RabbitMQ setup
        parameters = pika.URLParameters(amqp_url)
        connection = pika.BlockingConnection(parameters)

        self.channel = connection.channel()
        self.channel.queue_declare(queue = 'out.web', durable = True, auto_delete = True)
        self.channel.basic_consume(queue = 'out.web', on_message_callback = self.postEvent)

        print(' Waiting for events... press CTRL+C to terminate')
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print(' Connection closed')
            connection.close()

    def postEvent(self, channel, method, properties, body):
        try:
            requests.post(url = self.api_endpoint, data = body)
        except requests.exceptions.RequestException as e:
            print(e)
        self.channel.basic_ack(delivery_tag = method.delivery_tag)
        print('[x] Event posted!')

if __name__ == "__main__":
    amqp_url = os.environ['AMQP_URL'] if 'AMQP_URL' in os.environ else 'http://localhost'
    api_endpoint = os.environ['API_ENDPOINT'] if 'API_ENDPOINT' in os.environ else 'http://localhost:5000/update'
    postweb = postWebEvents(amqp_url, api_endpoint)
