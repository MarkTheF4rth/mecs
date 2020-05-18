"""
Simulates sending kibana events to the queue
Run conditions:
    python3 kibanaEvents.py
    python3 kibanaEvents.py <path/to/kibana.csv>
if no path is specified, assumes it is in the cwd
"""

import pika
import os
import sys
import json
import time

class KibanaEvents:
    def __init__(self, amqp_url, file_loc):
        #RabbitMQ setup
        print('URL: %s' % (amqp_url,))
        parameters = pika.URLParameters(amqp_url)
        self.connection = pika.BlockingConnection(parameters)

        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange = 'events-in', exchange_type = 'direct')
        self.channel.queue_declare(queue = 'in.kibana', auto_delete = True)
        self.channel.queue_bind(exchange = 'events-in', queue = 'in.kibana', routing_key = 'in.kibana')

        self.file_loc = file_loc
        # time between events being fired out
        self.interval = 1 

    def message_loop(self):
        """simulate event dispatch using their timestamps"""
        #open kibana dump
        kibana = open(self.file_loc)
        line = kibana.readline() # skip the first line

        print(" Sending events... press CTRL+C to terminate")
        while line:
            try:
                line = kibana.readline()
    
                self.channel.basic_publish(exchange = 'events-in', routing_key = 'in.kibana', body = line)
                print(" [x] Sent event!") 
                time.sleep(self.interval)
            except KeyboardInterrupt:
                self.connection.close()
                print(" Connection closed")
                break


if __name__ == "__main__":
    amqp_url = os.environ['AMQP_URL'] if 'AMQP_URL' in os.environ else 'http://localhost'
    file_loc = sys.argv[1] if len(sys.argv) > 1 else "errors_last_15_minutes.csv"
    kibana_events = KibanaEvents(amqp_url, file_loc)
    kibana_events.message_loop()
