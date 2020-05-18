import os
import sys
import pika
import time

class Watcher:
    def __init__(self):
        '''Define queues and starting instance quantities'''
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = connection.channel()

        self.gateway_instances = 1

    def check_queues(self, threshold):
        '''count queue sizes, rescale if they exceed thresholds'''
        ringdump_queue = self.channel.queue_declare(queue = 'in.ringdump', auto_delete = True)
        fake_queue = self.channel.queue_declare(queue = 'in.fake', auto_delete = True)
        kibana_queue = self.channel.queue_declare(queue = 'in.kibana', auto_delete = True)
        storage_queue = self.channel.queue_declare(queue = 'out.storage', durable = True, auto_delete = True)
        web_queue = self.channel.queue_declare(queue = 'out.web', durable = True, auto_delete = True)

        ringdump_count = ringdump_queue.method.message_count
        fake_count = fake_queue.method.message_count
        kibana_count = kibana_queue.method.message_count

        if any((ringdump_count > threshold), (fake_count > threshold), (kibana_count > threshold)):
            self.gateway_instances += 1
            print("\n[x] Starting a new gateway...\n")
            os.system("docker service scale project_gateway="+str(self.gateway_instances))

        elif all(((ringdump_count == 0), (fake_count == 0), (kibana_count == 0), (self.gateway_instances > 1))):
            self.gateway_instances -= 1
            print("\n[x] Downscaling gateway...\n")
            os.system("docker service scale project_gateway="+str(self.gateway_instances))

    def watcher_loop(self, threshold=5, interval=1, *args):
        '''run check queues at a specific interval'''
        while True:
            self.check_queues(threshold)
            time.sleep(interval)

if __name__ == "__main__":
    watcher = Watcher()
    try:
        args = list(map(int, sys.argv[1:]))
        watcher.watcher_loop(*args)
    except ValueError:
        print('Unsupported types, please make sure you\'re entering integers')

