#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from core.custom_queue import msgQueue
from core.Backends import db_method
from web import models
from core import redis_helper


class wb_handle:

    def __init__(self):
        self.q = msgQueue()
        self.redis = redis_helper.redis_helper()

    def callback(self,ch, method, properties, body):
        print("收到消息:" % body)
        data = json.loads(body.decode())
        data['uid'] = 1
        data['perm'] = 0
        data['type'] = 0
        db_wb_obj = db_method.save_weibo_db(data)
        print(db_wb_obj.id)
        self.push_to_followers(data,db_wb_obj)

    def watch_new_wbs(self):
        self.q.make_conn()
        self.q.channel.queue_declare(queue='weibo')

        self.q.channel.basic_consume(self.callback,
                                     no_ack=True,
                                     queue='weibo')

        print('[x] 发现新消息')
        self.q.channel.start_consuming()

    def push_to_followers(self,data,db_wb_obj):
        """
        取出微博id
        反向查询出所有粉丝 (根据uid 拿到用户对象  反查他的粉丝)
        循环粉丝
        若粉丝最近登录
        则创建一个粉丝id为名字的队列
        把微博id写进去
        """
        print(" [x] start_push_message")

        data['wb_id'] = db_wb_obj.id    # 当前微博在数据库的位置
        wb_user = models.UserProfile.objects.get(id=data['uid'])

        for follower in wb_user.my_followers.select_related():

            recent_f = self.redis.r.get(follower.id)
            print(" [x] recent_login_user: ", recent_f)
            queue_name = "uid_%s" % follower.id

            if recent_f:
                from core import custom_queue
                q = custom_queue.msgQueue()
                q.make_conn()

                q.channel.queue_declare(queue=queue_name)
                q.channel.basic_publish(exchange='',
                                        routing_key=queue_name,
                                        body=json.dumps(data))

                print(" [x] end push message", data, queue_name)


