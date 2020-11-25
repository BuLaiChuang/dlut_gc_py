#!/usr/bin/env python
import pika
import time

credentials = pika.PlainCredentials('xuan', '123456')  # mq用户名和密码
connection = pika.BlockingConnection(pika.ConnectionParameters(host = '210.30.97.163',port = 5672,virtual_host = '/',credentials = credentials))
channel=connection.channel()

channel.queue_declare(queue='task_queue', durable=True)
print(' [*] Waiting for messages. To exit press CTRL+C')

# 当工作者（worker）完成了任务，就发送一个响应。
#下面的代码，我们发现即使使用CTRL+C杀掉了一个工作者（worker）进程，消息也不会丢失。当工作者（worker）挂掉这后，所有没有响应的消息都会重新发送。
def callback(ch, method, properties, body):
    print(" [x] Received %r" % body.decode())
    time.sleep(body.count(b'.'))
    print(" [x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)

#可以使用basic.qos方法，并设置prefetch_count=1。这样是告诉RabbitMQ，再同一时刻，不要发送超过1条消息给一个工作者（worker）
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='task_queue', on_message_callback=callback)

channel.start_consuming()