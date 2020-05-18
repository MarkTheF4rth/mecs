"""
Simulates sending ring events to the queue
Run conditions:
    python3 ringdumpEvents.py
    python3 ringdumpEvents.py <path/to/ringdump.json>
if no path is specified, assumes it is in the cwd
"""

import pika
import os
import sys
import json
import time

class RingDumpEvents:
    def __init__(self, amqp_url, file_loc):
        #RabbitMQ setup
        print('URL: %s' % (amqp_url,))
        parameters = pika.URLParameters(amqp_url)
        self.connection = pika.BlockingConnection(parameters)

        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange = 'events-in', exchange_type = 'direct')
        self.channel.queue_declare(queue = 'in.ringdump', auto_delete = True)
        self.channel.queue_bind(exchange = 'events-in', queue = 'in.ringdump', routing_key = 'in.ringdump')

        self.file_loc = file_loc


    def message_loop(self):
        """simulate event dispatch using differences in event time"""
        print(" Sending events... press CTRL+C to terminate")
        ringdump = open(self.file_loc, 'r')
        last_event = 0
        line = "placeholder"

        # read the file in reverse order
        while line:
            try:
                line = ringdump.readline()
                event = json.loads(line)
                if 'time' not in event:
                    # not all events have a timestamp, ignore them
                    continue

                # wait until next event is set to run, limit to 1 second to prevent elongated quiet periods
                limiter = lambda x, y: (x-y if (x-y < 1) else 1)
                time.sleep(limiter(event['time'], last_event))

                self.channel.basic_publish(exchange = 'events-in', routing_key = 'in.ringdump', body = line)
                print(" [x] Sent event!")

                last_event = event['time']
            except KeyboardInterrupt:
                self.connection.close()
                print(" Closing connection...")
                break

if __name__ == "__main__":
    amqp_url = os.environ['AMQP_URL'] if 'AMQP_URL' in os.environ else 'http://localhost'
    file_loc = sys.argv[1] if len(sys.argv) > 1 else "ringdump.json"
    ringdump_events = RingDumpEvents(amqp_url, file_loc)
    ringdump_events.message_loop()
