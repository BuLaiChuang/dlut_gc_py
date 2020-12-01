import time
import random
import pika
from pika.exceptions import ChannelClosed, ConnectionClosed

# rabbitmq 配置信息
MQ_CONFIG = {
    "hostname": "210.30.97.163",
    "port": 5672,
    "vhost": "/",
    "username": "xuan",
    "password": "123456",
    "exchange": "exchange",
    "queue": "queue",
    "routing_key": "key" # 一对一发送
}


# 消息队列基类
class RabbitMQServer(object):
    def __init__(self):
        self.config = MQ_CONFIG  # 配置文件加载
        self.host = self.config.get("hostname")  # 主机
        self.port = self.config.get("port")  # 端口
        self.username = self.config.get("username")  # 用户名
        self.password = self.config.get("password")  # 密码
        self.vhost = self.config.get("vhost")  # 虚拟主机，VirtualHost之间相互隔离
        self.exchange = self.config.get("exchange")  # 交换机
        self.queue = self.config.get("queue")  # 队列
        self.routing_key = self.config.get("routing_key")  # 交换机和队列的绑定

        self.connection = None
        self.channel = None


    def reconnect(self, heartbeat=True):
        try:
            # 关闭旧的连接
            if self.connection and not self.connection.is_closed:
                self.connection.close()

            # 构造登录参数
            credentials = pika.PlainCredentials(self.username, self.password)
            parameters = pika.ConnectionParameters(self.host, self.port, self.vhost, credentials)

            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            # 声明交换机
            self.channel.exchange_declare(exchange=self.exchange, exchange_type="direct", durable=True)

            # 消费者实例
            if isinstance(self, RabbitComsumer):
                self.channel.queue_declare(queue=self.queue, exclusive=True, durable=True)
                # 绑定队列
                self.channel.queue_bind(exchange=self.exchange, queue=self.queue, routing_key=self.routing_key)
                # 表明最大阻塞未ack的消息数量
                self.channel.basic_qos(prefetch_count=1)
                self.channel.basic_consume(on_message_callback=self.consumer_callback, queue=self.queue, auto_ack=False)
            # 生产者实例
            elif isinstance(self, RabbitPublisher):
                self.channel.queue_declare(queue=self.queue, exclusive=False, durable=True)

        except Exception as e:
            print(e)


def excecute(body):
    pass


# 消费者
class RabbitComsumer(RabbitMQServer):
    def __init__(self):
        super(RabbitComsumer, self).__init__()

    def consumer_callback(self, channel, method, properties, body):
        result = execute(body)  # 模拟处理消息
        if channel.is_open:
            if result:
                channel.basic_ack(delivery_tag=method.delivery_tag)
            else:
                # 处理不成功时，发送no_ack
                channel.basic_nack(delivery_tag=method.delivery_tag, multiple=False, requeue=True)
        if not channel.is_open:
            print("Callback 接收频道关闭，无法ack")

    def start_consumer(self):
        while True:
            try:
                self.reconnect()
                self.channel.start_consuming()
            except ConnectionClosed as e:  # 保证连接断开重连
                self.reconnect()
                time.sleep(2)
            except ChannelClosed as e:  # 保证连接断开重连
                self.reconnect()
                time.sleep(2)
            except Exception as e:
                self.reconnect()
                time.sleep(2)


# 生产者
class RabbitPublisher(RabbitMQServer):
    def __init__(self):
        super(RabbitPublisher, self).__init__()

    def start_publish(self):
        self.reconnect()
        i = 1
        while True:
            message = {"value": i}
            try:
                self.channel.basic_publish(exchange=self.exchange, routing_key=self.routing_key, body=message)
                i += 1
                time.sleep(2)
            except ConnectionClosed as e:
                self.reconnect()
                time.sleep(2)
            except ChannelClosed as e:
                self.reconnect()
                time.sleep(2)
            except Exception as e:
                self.reconnect()
                time.sleep(2)