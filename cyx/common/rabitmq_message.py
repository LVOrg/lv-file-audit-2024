import json
import threading
import time

import cy_docs
import cy_kit
from cyx.common.msg import MessageInfo
import cyx.common.msg
import typing
import cyx.common
import pika
import os
import pathlib

log_dir = os.path.join(
    pathlib.Path(__file__).parent.parent.parent.__str__(),
    "logs",
    cyx.common.msg.MSG_FILE_UPLOAD

)
print(f"logs to {log_dir}")
logs = cy_kit.create_logs(
    log_dir=log_dir,
    name=pathlib.Path(__file__).stem
)


class RabitmqMsg:
    """
    Definition RabbitMQ Producer and Consumer \n
    Định nghĩa RabbitMQ Producer và Consumer

    """
    def __try_connect__(self):
        """
        Sometime RabbitMQ was fail with unknown reason. The function will re-connect \n
        Đôi khi RabbitMQ bị lỗi mà không rõ lý do. Function sẽ kết nối lại

        :return:
        """
        self.__channel__:pika.BlockingChannel =None
        try:
            if isinstance(self.__channel__,pika.BlockingConnection):
                try:
                    self.__channel__.close()
                    self.__channel__ = None
                except:
                    pass
            if not self.__channel__ or not self.__channel__.connection.is_open:
                self.__credentials__ = pika.PlainCredentials(self.__username__, self.__password__)

                self.__parameters__ = pika.ConnectionParameters(
                    host=self.__server__,
                    port=self.__port__,
                    virtual_host='/',
                    credentials=self.__credentials__,
                    heartbeat=30,
                    retry_delay=10
                )
                self.__connection__ = pika.BlockingConnection(self.__parameters__)
                self.__channel__ = self.__connection__.channel()
            return True
        except Exception as e:
            return False

    def __init__(self):
        print("Init rabbitmq")
        self.msg_type = None
        self.__channel__: pika.adapters.blocking_connection.BlockingChannel = None
        self.__connection__: pika.BlockingConnection = None
        self.__parameters__ = None
        self.__is_declare__ = False
        self.config = cyx.common.config

        if self.config.get("rabbitmq") is None or not isinstance(self.config.get("rabbitmq"), dict):
            raise Exception("It looks like thou forget set rabbitmq")

        self.__server__ = self.config.get("rabbitmq").get("server")
        self.__port__ = int(self.config.get("rabbitmq").get("port", 5672))
        self.__username__ = self.config.get("rabbitmq").get("username", "guest")
        self.__password__ = self.config.get("rabbitmq").get("password", "guest")
        self.__msg__ = self.config.get("rabbitmq").get("msg", "msg")
        self.__try_connect__()

    def reset_status(self, message_type: str):
        """
            Reset status
            :param message_type:
            :return:
                """
        raise NotImplemented

    def get_type(self) -> str:
        """
            somehow to implement thy source here ...
                """
        return "RabbitMQ"

    def consume(self, handler, msg_type: str):
        """
        Start RabbitMQ consumer.
        """
        self.__try_connect__()
        self.msg_type = msg_type
        print(f"msg will consume is {self.__msg__}.{self.msg_type}")

        def callback(ch, method, properties, body: bytes):
            txt_json = body.decode('utf-8')
            logs.info(txt_json)
            data = json.loads(txt_json)

            msg = MessageInfo()
            msg.Data = data.get('data')
            msg.MsgType = msg_type
            msg.AppName = data.get('app_name')
            msg.tags = dict(method=method, ch=ch, properties=properties)
            try:
                handler(msg)
                logs.info(f"{txt_json} was complete")
            except Exception as e:
                logs.exception(e)
                msg.tags = None
                # self.re_emit(msg)
            #self.delete(msg)

        if not self.__is_declare__:
            while self.__channel__ is None:
                self.__try_connect__()
                time.sleep(10)
            self.__channel__.queue_declare(queue=self.get_real_msg(msg_type), auto_delete=False)
            self.__is_declare__ = True
        self.__channel__.basic_consume(queue=self.get_real_msg(msg_type), on_message_callback=callback, auto_ack=False)


        try:
            self.__channel__.start_consuming()
        except pika.exceptions.ConnectionClosedByBroker as e:
            """
            Sometime RabbitMQ was fail with unknown reason. The function will re-connect
            Đôi khi RabbitMQ bị lỗi mà không rõ lý do. Chức năng sẽ kết nối lại

            """
            time.sleep(1)
            print(f"re-connect {self.__server__}")
            ok = False
            count = 0
            while not ok and count < 10000:
                """
                Try reconnect ten times, time after time is 5 seconds
                Thử kết nối lại mười lần, hết lần này đến lần khác là 5 giây


                """
                count += 1
                self.__channel__ = None
                self.__try_connect__()
                try:

                    self.__channel__.queue_declare(queue=msg_type, auto_delete=False)
                    self.__channel__.start_consuming()
                    ok = True
                except pika.exceptions.ConnectionWrongStateError as e:
                    ok = False
                    time.sleep(5)
                    print(f"re-connect {self.__server__}")


    def get_message(self, message_type: str, max_items: int) -> typing.List[cyx.common.msg.MessageInfo]:
        """
        somehow to implement thy source here ...
        """

        def callback(ch, method, properties, body):
            print(" [x] Received %r" % body)

        self.channel.basic_consume(queue=f"{self.__msg__}.{message_type}", on_message_callback=callback, auto_ack=True)
        # fx= self.channel.basic_consume(queue=message_type, auto_ack=True)
        # print(' [*] Waiting for messages. To exit press CTRL+C')
        self.channel.start_consuming()

    def lock(self, item: MessageInfo):
        """
        somehow to implement thy source here ...
        """
        raise NotImplemented

    def is_lock(self, item: MessageInfo):
        """
        somehow to implement thy source here ...
        """
        raise NotImplemented

    def unlock(self, item: MessageInfo):
        """
        somehow to implement thy source here ...
        """
        raise NotImplemented

    def delete(self, item: MessageInfo):
        if item.deleted is None or item.deleted==False:
            self.delete_msg(item)
            item.deleted=True

    def delete_msg(self, item: MessageInfo):
        """
        somehow to implement thy source here ...
        """

        try:
            print(f"delete msg {item}")
            if item.tags['ch'].is_open:

                item.tags['ch'].basic_ack(delivery_tag=item.tags['method'].delivery_tag)
            else:
                pass
        except pika.exceptions.StreamLostError as e:
            return
        except pika.exceptions.ChannelWrongStateError as e:
            print(e)
            print(f"delete msg {item} error")

        except Exception as e:
            print(e)
            print(f"delete msg {item} error")
            raise e

    def emit(self, app_name: str, message_type: str, data: typing.Optional[typing.Union[dict,cy_docs.DocumentObject]]):
        """
        somehow to implement thy source here ...
        """
        # self.channel.exchange_declare(exchange='logs', exchange_type=message_type)
        self.__try_connect__()

        msg = cy_kit.to_json(
            dict(
                app_name=app_name,
                data=data
            )
        )
        try:
            print(f"msg to {self.__server__}:{self.__port__}\nmsg={message_type} in app={app_name}")
            if not self.__is_declare__:
                if self.__channel__:
                    self.__channel__.queue_declare(queue=self.get_real_msg(message_type))
                    self.__is_declare__ = True
                else:
                    self.__try_connect__()

            self.__channel__.basic_publish(exchange='', routing_key=self.get_real_msg(message_type), body=msg, )
        except pika.exceptions.StreamLostError as e:
            print("Error:")
            print(e)
            self.__channel__ = None
            self.__try_connect__()
            if not self.__is_declare__:
                self.__channel__.queue_declare(queue=self.get_real_msg(message_type))
                self.__is_declare__ = True
            self.__channel__.basic_publish(exchange='', routing_key=self.get_real_msg(message_type), body=msg, )
        except AssertionError as e:
            print("Error:")
            print(e)
            self.__channel__ = None
            self.__try_connect__()
            if not self.__is_declare__:
                self.__channel__.queue_declare(queue=self.get_real_msg(message_type))
                self.__is_declare__ = True
            self.__channel__.basic_publish(exchange='', routing_key=self.get_real_msg(message_type), body=msg, )



        except Exception as e:
            raise e

        # message = ' '.join(sys.argv[1:]) or "info: Hello World!"

    def re_emit(self, msg: MessageInfo):
        """
        somehow to implement thy source here ...
        """
        def run_re_emit( owner,msg):
            time.sleep(60*60)
            data = msg.Data
            count = msg.Data.get("resume_count", 0)
            if count < 3:
                count += 1
                msg.Data["resume_count"] = count
                owner.emit(
                    app_name=msg.AppName,
                    message_type=owner.msg_type,
                    data=msg.Data

                )
        th=threading.Thread(target=run_re_emit,args=(self,msg,))
        th.start()

    def close(self):
        """
            somehow to implement thy source here ...
                """
        print(f"{self.get_type()} is closing")
        self.channel.close()

    def get_real_msg(self,msg_type):
        if self.__msg__ is not None:
            ret = f"{self.__msg__}.{msg_type}"
            print(f"real msg is: {ret}")
            return ret
        else:
            print(f"msg will raise {msg_type}")
            return msg_type
