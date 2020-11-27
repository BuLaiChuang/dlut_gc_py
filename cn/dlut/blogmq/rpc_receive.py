import pika
import time

connection = pika.BlockingConnection(pika.ConnectionParameters(
    host='localhost'))

channel = connection.channel()

channel.queue_declare(queue='rpc_queue')

# 计算斐波那契
def fib(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)


def on_request(ch, method, props, body):
    n = int(body)

    print(" [.] fib(%s)" % n)
    response = fib(n)

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to, # 从props中取出客户端放的reply_to
                     properties=pika.BasicProperties(correlation_id= \
                                                         props.correlation_id),# 客户端发的唯一标识符
                     body=str(response))
    ch.basic_ack(delivery_tag=method.delivery_tag) # 执行完

# 一次只处理一个任务，处理完后再拿
channel.basic_qos(prefetch_count=1)
channel.basic_consume(on_request, queue='rpc_queue')

print(" [x] Awaiting RPC requests")
channel.start_consuming()