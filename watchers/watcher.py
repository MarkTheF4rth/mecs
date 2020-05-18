import pika
import time
import os
import signal
import subprocess
import atexit
import sys

#max number of messages in a queue at any moment
threshold = int(sys.argv[1]) if len(sys.argv) > 1 else 10
#time interval for checking the queues (in seconds)
interval = int(sys.argv[2]) if len(sys.argv) > 2 else 2
#started scripts
new_scripts = []

def check_queues():
    ringdump_queue = channel.queue_declare(queue = 'in.ringdump', auto_delete = True)
    fake_queue = channel.queue_declare(queue = 'in.fake', auto_delete = True)
    kibana_queue = channel.queue_declare(queue = 'in.kibana', auto_delete = True)
    storage_queue = channel.queue_declare(queue = 'out.storage', durable = True, auto_delete = True)
    web_queue = channel.queue_declare(queue = 'out.web', durable = True, auto_delete = True)

    ringdump_count = ringdump_queue.method.message_count
    fake_count = fake_queue.method.message_count
    kibana_count = kibana_queue.method.message_count
    storage_count = storage_queue.method.message_count
    web_count = web_queue.method.message_count

    print()
    print(" [x] Ringdump queue: " + str(ringdump_count) + " events... " + ("OK!" if ringdump_count <= threshold else "NOT OK!"))
    print(" [x] Fake queue: " + str(fake_count) + " events... " + ("OK!" if fake_count <= threshold else "NOT OK!"))
    print(" [x] Kibana queue: " + str(kibana_count) + " events... " + ("OK!" if kibana_count <= threshold else "NOT OK!"))
    print(" [x] Storage queue: " + str(storage_count) + " events... " + ("OK!" if storage_count <= threshold else "NOT OK!"))
    print(" [x] Web queue: " + str(web_count) + " events... " + ("OK!" if web_count <= threshold else "NOT OK!"))
    print()

    if (ringdump_count > threshold) or (fake_count > threshold) or (kibana_count > threshold):
        print()
        print(" [x] Starting a new gateway...")
        print()
        new_scripts.append(subprocess.Popen(['python3', '../gateway/gateway.py']))

    if storage_count > threshold:
        print()
        print(" [x] Starting a new storage worker...")
        print()
        new_scripts.append(subprocess.Popen(['python3', '../consumers/Database/storeEvents.py']))
    
    if web_count > threshold:
        print()
        print(" [x] Starting a new web worker...")
        print()
        new_scripts.append(subprocess.Popen(['python3', '../consumers/WebConsumer/webConsumer.py']))

def kill_all_children():
    for script in new_scripts:
        script.terminate()
    

#RabbitMQ setup
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

#clean up processes on exit
atexit.register(kill_all_children)

last_check = time.time()

print(" [x] Watching queues, press CTRL + C to cancel...")
try:
    while True:
        check_queues()
        time.sleep(interval)   
except KeyboardInterrupt:
    pass