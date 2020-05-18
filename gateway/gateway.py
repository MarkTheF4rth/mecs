import pika
import os
import json
import sys
import time
import datetime
import pandas as pd
import numpy as np
from io import BytesIO
    
class Translator():
    channel = None

    """ Open Connection """
    def __init__(self, amqp_url):
        # Connect to RabbitMQ server
        print('URL: %s' % (amqp_url,))
        parameters = pika.URLParameters(amqp_url)
        connection = pika.BlockingConnection(parameters)
        self.channel = connection.channel()
        self.channel.queue_declare(queue = 'in.ringdump', auto_delete = True)
        self.channel.queue_declare(queue = 'in.kibana', auto_delete = True)
        self.channel.queue_declare(queue = 'in.fake', auto_delete = True)

        self.channel.exchange_declare(exchange = 'events-out', exchange_type = 'fanout')
        self.channel.queue_declare(queue = 'out.storage', durable = True, auto_delete = True)
        self.channel.queue_declare(queue = 'out.web', durable = True, auto_delete = True)
        self.channel.queue_bind(exchange = 'events-out', queue = 'out.storage')    
        self.channel.queue_bind(exchange = 'events-out', queue = 'out.web')  

        #don't dispatch a message to a consumer until it has acknowledged the previous one
        self.channel.basic_qos(prefetch_count = 1)

        print('[x] Waiting for messages, to cancel press Ctrl + C')

        # Callback setup
        self.channel.basic_consume(queue = 'in.ringdump', on_message_callback = self.callback_ringdump)
        self.channel.basic_consume(queue = 'in.kibana', on_message_callback = self.callback_kibana)
        self.channel.basic_consume(queue = 'in.fake', on_message_callback = self.callback_fake)
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            pass

    """ Receives the message and calls for modification """
    def callback_ringdump(self, ch, method, properties, body):
        self.modify_ringdump(body)
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def callback_kibana(self, ch, method, properties, body):
        self.modify_kibana(body)
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def callback_fake(self, ch, method, properties, body):
        self.modify_fake(body)
        ch.basic_ack(delivery_tag = method.delivery_tag)

    """ Ring dump modification - dropping unnecessary attributes """
    # rindgump's attributes are in the same order as in the template
    # deletion of keys should be enough to match UnifiedDataModel
    def modify_ringdump(self, message):
        print("[x] Received ringdump event")

        event = json.loads(message)
        event_template = set(['time',
                              'node',
                              'event',
                              'level'])

        # Remove key, value if not in the template
        for attribute in list(event):
            if not attribute in event_template:
                del event[attribute]

        json_message = json.dumps(event)
        self.send(json_message)

    """ Kibana dump modification - renaming, adding labels and dropping unnecessary attributes """
    def modify_kibana(self, message):
        print("[x] Received kibana event")

        # columns names - for labeling, list of labels that has been renamed:
        # @host -> node, @log_message -> event, @timestamp -> time
        col_names = ['node', 'event', 'time', '_id', '_index', '_score',
                    '_type', 'event_timestamp', 'host', 'logsource', 'message',
                    'syslog_facility', 'syslog_facility_code', 'syslog_hostname', 'syslog_pri',
                    'syslog_severity', 'syslog_severity_code', 'syslog_timestamp', 'tags', 'type']

        kibana_line = BytesIO(message)
        # create a dataframe object, it is because I need labels
        df = pd.read_csv(kibana_line, sep = ',', names = col_names)
        # take only the necessary labels and re-arrange them
        df = df.loc[:, ['time', 'node', 'event']]
        #convert time column from date string to unix timestamp
        df['time'] = time.mktime(datetime.datetime.strptime(str(df.iloc[0]['time']), '%b %d, %Y @ %H:%M:%S.%f').timetuple())
        # create 'level' column and insert nan value
        df['level'] = "Normal"
        #convert the entire dataframe to a json object, then only take the first row
        df_message = df.to_json(orient = 'records')
        json_dict = json.loads(df_message)

        message = json.dumps(json_dict[0])
        self.send(message)
        
    """ Fake dump modification - adding, converting the attributes """
    def modify_fake(self, message):
        print("[x] Received fake event")
    
        event = json.loads(message)
        event['node'] = event['data_center'] + '-' + event['subsection']
        event_template = set(['time', 'node', 'event', 'level'])

        for attribute in list(event):
            if not attribute in event_template:
                del event[attribute]

         # Convert the numerical values to categorical values
        level_template = {1: 'Normal', 2: 'Warning', 3: 'Minor', 4: 'Major' , 5: 'Critical' , 6: 'Fatal'}

        event['level'] = level_template[event['level']]

        json_message = json.dumps(event)
        self.send(json_message)

    """  Adds modified json to the queue 'out' """
    def send(self, message):
        self.channel.basic_publish(exchange = 'events-out',
                              routing_key = '',
                              body = message,
                              properties = pika.BasicProperties(
                                  delivery_mode = 2, # make message persistent
                              ))
        print()
        print(message)
        print("[x] Sent event!")
        print()

if __name__ == "__main__":
    amqp_url = os.environ['AMQP_URL'] if 'AMQP_URL' in os.environ else 'http://localhost'
    translator = Translator(amqp_url)
