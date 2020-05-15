import pika
import os
import json
import time

#RabbitMQ setup
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.exchange_declare(exchange = 'events-in', exchange_type = 'direct')
channel.queue_declare(queue = 'in.kibana', auto_delete = True)
channel.queue_bind(exchange = 'events-in', queue = 'in.kibana', routing_key = 'in.kibana')

#open kibana dump
ringdump = open('../errors_last_15_minutes.csv')
print(" Sending events... press CTRL+C to terminate")

#set the interval at which events will be fired
interval = 1

#skip the first line
ringdump.readline()

#simulate event dispatch using their timestamps
try:
    while True:
        line = ringdump.readline()
        if not line:
            break
        
        time.sleep(interval)

        channel.basic_publish(exchange = 'events-in', routing_key = 'in.kibana', body = line)
        print(" [x] Sent event!") 
except KeyboardInterrupt:
    pass

print(" Closing connection...")

connection.close()