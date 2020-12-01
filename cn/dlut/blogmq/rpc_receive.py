import pika
import time

credentials = pika.PlainCredentials('xuan', '123456')  # mq用户名和密码
# 虚拟队列需要指定参数 virtual_host，如果是默认的可以不填。
connection = pika.BlockingConnection(pika.ConnectionParameters(host='210.30.97.163', port=5672, virtual_host='/', credentials=credentials))
channel = connection.channel()

result = channel.queue_declare(queue = 'rpc_queue',durable=True)

# 计算斐波那契
# def fib(n):
#     if n == 0:
#         return 0
#     elif n == 1:
#         return 1
#     else:
#         return fib(n - 1) + fib(n - 2)

# 调用盛夏代码查询相关的论文
def shengxia(n):
    return n*10

def on_request(ch, method, props, body):
    n = int(body)
    print(" [.] shengxia(%s)" % n)
    response = shengxia(n)
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