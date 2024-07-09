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

# log_dir = os.path.join(
#     pathlib.Path(__file__).parent.parent.parent.__str__(),
#     "logs",
#     cyx.common.msg.MSG_FILE_UPLOAD
#
# )
# print(f"logs to {log_dir}")
# logs = cy_kit.create_logs(
#     log_dir=log_dir,
#     name=pathlib.Path(__file__).stem
# )

from cyx.cache_service.memcache_service import MemcacheServices
memcache_service = cy_kit.singleton(MemcacheServices)
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

    def consume(self, handler, msg_type: str,auto_ack=False):
        """
        Start RabbitMQ consumer.
        """
        self.__try_connect__()
        self.msg_type = msg_type
        print(f"msg will consume is {self.__msg__}.{self.msg_type}")

        def callback(ch, method, properties, body: bytes):
            txt_json = body.decode('utf-8')
            print(txt_json)
            data = dict()
            try:
                data = json.loads(txt_json)
                resource = data.get("resource")
                parent_msg = data.get("parent_msg")
                parent_tag =data.get("parent_tag")
                require_tracking =data.get("require_tracking") or False
                msg = MessageInfo()
                msg.Data = data.get('data')
                msg.MsgType = msg_type
                msg.AppName = data.get('app_name')
                msg.tags = dict(method=method, ch=ch, properties=properties)
                msg.resource= resource
                msg.parent_msg = parent_msg
                msg.parent_tag = parent_tag
                msg.require_tracking = require_tracking
                handler(msg)
            except Exception as ex:
                print(str(ex))
                if isinstance(self.__channel__,pika.adapters.blocking_connection.BlockingChannel):
                    if self.__channel__.is_open:
                        self.__channel__.basic_ack(delivery_tag=method.delivery_tag)
                return




        import pika.adapters.blocking_connection
        if not self.__is_declare__:
            while self.__channel__ is None:
                self.__try_connect__()
                time.sleep(10)
            assert isinstance(self.__channel__,pika.adapters.blocking_connection.BlockingChannel)
            self.__channel__.queue_declare(queue=self.get_real_msg(msg_type), auto_delete=auto_ack)
            self.__is_declare__ = True
        assert isinstance(self.__channel__, pika.adapters.blocking_connection.BlockingChannel)
        def on_cancel(*args,**kwargs):
            print(args)
        def on_return(*args,**kwargs):
            print(args)
        self.__channel__.add_on_cancel_callback(on_cancel)
        self.__channel__.add_on_return_callback(on_return)
        self.__channel__.basic_consume(queue=self.get_real_msg(msg_type), on_message_callback=callback,auto_ack=auto_ack)



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

                    self.__channel__.queue_declare(queue=msg_type, auto_delete=True)
                    self.__channel__.start_consuming()
                    ok = True
                except pika.exceptions.ConnectionWrongStateError as e:
                    ok = False
                    time.sleep(5)
                    print(f"re-connect {self.__server__}")
        except pika.exceptions.StreamLostError as e:
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

        self.channel.basic_consume(queue=f"{self.__msg__}.{message_type}", on_message_callback=callback, auto_ack=False)
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

    def delete(self, item: MessageInfo,is_error_reason=False):
        if item.deleted is None or item.deleted==False:
            self.delete_msg(item)
            item.deleted=True
    def reject(self, item: MessageInfo):
        if item.deleted is None or item.deleted==False:
            self.reject_msg(item)
            item.deleted=True
    def reject_msg(self, item):

        try:
            key_check = f'{item.Data.get("_id")}/{item.tags["method"].delivery_tag}'
            print(f"delete msg {key_check}")
            from pika.adapters.blocking_connection import BlockingChannel,BlockingConnection
            # fx= Channel()
            # fx.open()
            chanel = item.tags['ch']
            if isinstance(chanel,BlockingChannel):
                if chanel.is_open:
                    # chanel.basic_nack(delivery_tag=item.tags['method'].delivery_tag)
                    chanel.basic_reject(delivery_tag=item.tags['method'].delivery_tag)


            # if item.tags['ch'].is_open:
            #
            #     item.tags['ch'].basic_ack(delivery_tag=item.tags['method'].delivery_tag)
            # else:
            #     item.tags['ch'].open()
            #     item.tags['ch'].basic_ack(delivery_tag=item.tags['method'].delivery_tag)
        except pika.exceptions.StreamLostError as e:
            return
        except pika.exceptions.ChannelWrongStateError as e:
            print(e)
            print(f"delete msg {item} error")

        except Exception as e:
            print(e)
            print(f"delete msg {item} error")
            raise e
    def delete_msg(self, item: MessageInfo):
        """
        somehow to implement thy source here ...
        """

        try:
            from pika.adapters.blocking_connection import BlockingChannel,BlockingConnection
            channel = item.tags['ch']
            if isinstance(channel,BlockingChannel):
                if channel.is_open:
                    # chanel.basic_nack(delivery_tag=item.tags['method'].delivery_tag)
                    # channel.basic_nack(delivery_tag=item.tags['method'].delivery_tag,multiple=True)
                    channel.basic_ack(item.tags['method'].delivery_tag)



            # if item.tags['ch'].is_open:
            #
            #     item.tags['ch'].basic_ack(delivery_tag=item.tags['method'].delivery_tag)
            # else:
            #     item.tags['ch'].open()
            #     item.tags['ch'].basic_ack(delivery_tag=item.tags['method'].delivery_tag)
        except pika.exceptions.StreamLostError as e:
            return
        except pika.exceptions.ChannelWrongStateError as e:
            print(e)
            print(f"delete msg {item} error")
        except pika.exceptions.ChannelClosedByBroker as e:
            print(e)
            print(f"delete msg {item} error")
            pass
        except Exception as e:
            print(e)
            print(f"delete msg {item} error")
            raise e

    def emit(
            self,
            app_name: str,
            message_type: str,
            data: typing.Optional[typing.Union[dict,cy_docs.DocumentObject]],
            parent_msg=None,
            parent_tag=None,
            resource=None,
            require_tracking: bool=False
    ):
        """
        somehow to implement thy source here ...
        """
        # self.channel.exchange_declare(exchange='logs', exchange_type=message_type)
        self.__try_connect__()
        if require_tracking:
            msg = cy_kit.to_json(
                dict(
                    app_name=app_name,
                    data=data,
                    is_process=True,
                    parent_msg = parent_msg,
                    parent_tag = parent_tag,
                    resource  = resource
                )
            )
        else:
            msg = cy_kit.to_json(
                dict(
                    app_name=app_name,
                    data=data,
                    parent_msg = parent_msg,
                    parent_tag = parent_tag,
                    resource  = resource
                )
            )
        try:
            if self.__channel__ is None:
                raise Exception(f"Can not connect to RabbitMQ {self.__server__}:{self.__port__} username {self.__username__}, pass={self.__password__}")
            print(f"msg to {self.__server__}:{self.__port__}\nmsg={self.get_real_msg(msg_type=message_type)} in app={app_name}")
            if self.__channel__:
                self.__channel__.queue_declare(queue=self.get_real_msg(message_type), auto_delete=False)
            else:
                self.__try_connect__()
                self.__channel__.queue_declare(queue=self.get_real_msg(message_type), auto_delete=False)
            self.__channel__.basic_publish(exchange='', routing_key=self.get_real_msg(message_type), body=msg, )
            print(f"{resource} {message_type}")
            # print(
            #     f"msg to {self.__server__}:{self.__port__}\nmsg={self.get_real_msg(msg_type=message_type)} in app={app_name} is OK")
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
    def emit_child_message(self, parent_message:MessageInfo, message_type:str, resource:str):
        self.emit(
            app_name=parent_message.AppName,
            data=parent_message.Data,
            parent_msg=parent_message.MsgType,
            parent_tag=parent_message.tags["method"].delivery_tag,
            resource=resource,
            message_type= message_type
        )
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





