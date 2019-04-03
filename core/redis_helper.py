#!/usr/bin/env python
# -*- coding: utf-8 -*-
import redis


class redis_helper:

    def __init__(self):
        self.pool = redis.ConnectionPool(host='127.0.0.1', port=6379, password='123456')

        # self.pool = redis.ConnectionPool(host='192.168.127.129', port=6379)
        self.r = redis.Redis(connection_pool=self.pool)
