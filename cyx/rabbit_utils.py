import pika
import pika.adapters.blocking_connection
from cyx.common import config
import json
class MesssageBlock:
    data: dict|None
    app_name:str|None
    method: None
    properties:None
    body: None

class Consumer:
    queue_name: str
    connection: pika.BlockingConnection
    channel: pika.adapters.blocking_connection.BlockingChannel

    def __init__(self, msg_type):
        self.queue_name = f'{config.rabbitmq.msg}.{msg_type}'
        self.do_init()

    def basic_get(self,delete_after_get=True):
        if self.connection.is_closed:
            self.do_init()
        method, properties, body = self.channel.basic_get(queue=self.queue_name , auto_ack=False)
        if method:
            if delete_after_get:
                self.channel.basic_ack(delivery_tag=method.delivery_tag, multiple=True)
        return method,properties,body

    def do_init(self):
        print(f"{config.rabbitmq.username}")
        auth = pika.PlainCredentials(
            config.rabbitmq.username, config.rabbitmq.password
        )

        connection_parameters = pika.ConnectionParameters(
            host=config.rabbitmq.server,
            port=config.rabbitmq.port,
            virtual_host="/",
            credentials=auth,
            heartbeat=30,
            retry_delay=10,
            blocked_connection_timeout=10,

        )
        # xyzdsc-2024.cloud.google.drive.sync
        # Define the queue to consume messages from

        # Establish connection and channel
        self.connection = pika.BlockingConnection(connection_parameters)
        self.channel = self.connection.channel()
        # channel.queue_declare(queue=queue_name, auto_delete=auto_ack)
        self.channel.queue_declare(queue=self.queue_name, auto_delete=False)

    def get_msg(self,delete_after_get=True)->MesssageBlock|None:
        ret = MesssageBlock()
        method, properties, body = self.basic_get(delete_after_get)
        if not method:
            return None
        dic_body = json.loads(body)
        ret.app_name= dic_body.get("app_name")
        ret.data = dic_body.get("data")
        ret.properties=properties
        ret.method = method
        ret.body = body
        return ret

    def raise_message(self, app_name:str,data):
        #self.__channel__.basic_publish(exchange='', routing_key=self.get_real_msg(message_type), body=msg, )
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body=json.dumps(dict(
                app_name= app_name,
                data = data
            ))

        )
    def resume(self, msg:MesssageBlock):
        #self.__channel__.basic_publish(exchange='', routing_key=self.get_real_msg(message_type), body=msg, )
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body=json.dumps(dict(
                app_name= msg.app_name,
                data = msg.data
            ))

        )
