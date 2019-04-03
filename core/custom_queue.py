import pika
import json
from Weibo import settings
# 发布者队列
# from web import models

class msgQueue:
    """docstring for msgQueue"""

    def __init__(self):
        self.connection = None

    def make_conn(self):
        # 连接rabbitmq服务器
        # self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.127.129'))
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='127.0.0.1'))

        self.channel = self.connection.channel()

    def publish_wb(self, wb_data):
        # 声明消息队列，消息将在这个队列中进行传递。如果将消息发送到不存在的队列，rabbitmq将会自动清除这些消息。如果队列不存在，则创建
        self.channel.queue_declare(queue='weibo')
        # RabbitMQ提供了一种直接向Queue发送消息的快捷方法：直接使用未命名的exchange，不用绑定routing_key，直接用它指定队列名。
        self.channel.basic_publish(exchange='', routing_key='weibo', body=json.dumps(wb_data))
        # 打印发布成功的消息
        print('[x] Sent %s' %(wb_data))
        # self.connection.close()

    #定义接收到返回消息的处理方法
    def on_response(self, ch, method, props, body):
        self.new_wb_list.append(json.loads(body.decode()))
        self.response = True


    def get_new_wb_count(self, queue_name):
        # 声明消息队列，消息将在这个队列中进行传递。如果将消息发送到不存在的队列，rabbitmq将会自动清除这些消息。如果队列不存在，则创建
        msg = self.channel.queue_declare(queue=queue_name)
        return msg.method.message_count

    def get_new_wb(self, queue_name):
        # 获取此用户队列中的新微博列表
        self.response = None
        self.new_wb_list = []
        # 声明消息队列，消息将在这个队列中进行传递。如果将消息发送到不存在的队列，rabbitmq将会自动清除这些消息。如果队列不存在，则创建
        self.channel.queue_declare(queue=queue_name)
        # 根据队列名称获取队列内微博
        self.channel.basic_consume(self.on_response,no_ack=True, queue=queue_name)
        #接收返回的数据
        # while self.response is None:
            # 队列阻塞
        self.connection.process_data_events()
        self.connection._flush_output()
        # 关闭连接
        self.connection.close()
        return self.new_wb_list
