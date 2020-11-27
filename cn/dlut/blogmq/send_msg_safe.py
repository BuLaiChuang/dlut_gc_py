import pika
import time
# n RabbitMQ a message can never be sent directly to the queue, it always needs to go through an exchange.
import sys

credentials = pika.PlainCredentials('xuan', '123456')  # mq用户名和密码
# 虚拟队列需要指定参数 virtual_host，如果是默认的可以不填。
connection = pika.BlockingConnection(pika.ConnectionParameters(host = '210.30.97.163',port = 5672,virtual_host = '/',credentials = credentials))
channel=connection.channel()

message = ' '.join(sys.argv[1:]) or "Hello World! %s" % time.time()

channel.basic_publish(exchange='',
                      routing_key='task_queue',
                      body=message,
                      properties=pika.BasicProperties(
                          delivery_mode=2,  # make message persistent
                      )
                      )
print(" [x] Sent %r" % message)
connection.close()