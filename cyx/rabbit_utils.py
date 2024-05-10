import pika
import pika.adapters.blocking_connection
from cyx.common import config


class Consumer:
    queue_name: str
    connection: pika.BlockingConnection
    channel: pika.adapters.blocking_connection.BlockingChannel

    def __init__(self, msg_type):
        self.queue_name = f'{config.rabbitmq.msg}.{msg_type}'
        self.do_init()

    def basic_get(self):
        if self.connection.is_closed:
            self.do_init()
        method, properties, body = self.channel.basic_get(queue=self.queue_name , auto_ack=False)
        if method:
            self.channel.basic_ack(delivery_tag=method.delivery_tag, multiple=True)
        return method,properties,body

    def do_init(self):
        auth = pika.PlainCredentials("guest", "guest")

        connection_parameters = pika.ConnectionParameters(
            host=config.rabbitmq.server, port=config.rabbitmq.port,
            virtual_host="/",
            credentials=auth,
            heartbeat=30,
            retry_delay=10,
            blocked_connection_timeout=10
        )
        # xyzdsc-2024.cloud.google.drive.sync
        # Define the queue to consume messages from

        # Establish connection and channel
        self.connection = pika.BlockingConnection(connection_parameters)
        self.channel = self.connection.channel()
        # channel.queue_declare(queue=queue_name, auto_delete=auto_ack)
        self.channel.queue_declare(queue=self.queue_name, auto_delete=False)
