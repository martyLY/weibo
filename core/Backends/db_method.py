#!/usr/bin/env python
# -*- coding: utf-8 -*-
from web import models


def save_weibo_db(data):
    # 持久化队列里面的微博
    # 供队列使用
    wb_type = data.get('type', None)  # 类型
    user = data.get('uid', None)    # 用户id
    text = data.get('content', None)    # 文博正文
    perm = data.get('perm', None)   # 权限
    date = data.get('time', None)    # 时间

    user_obj = models.UserProfile.objects.get(id=user)  # user_obj
    wb_dic = {'wb_type': wb_type, 'user': user_obj, 'text': text, 'perm': perm, 'date': date, }
    n = models.Weibo.objects.create(**wb_dic)
    n.save()
    return n


def fetch_user_by_name(user):
    # 给搜索页面使用的获取微博用户的方法
    obj = models.UserProfile.objects.get(name=user)
    user_dic = {}
    name = obj.name
    gender = obj.sex
    url = None
    user_dic['name'] = name
    user_dic['gender'] = gender
    user_dic['url'] = url
    return user_dic


def fetch_weibo_by_keyword(keyword):
    # 给搜索页面使用的获取所有微博消息的方法
    # 默认获取公开微博,返回微博列表
    print('search keyword is', keyword)
    obj = models.Weibo.objects.filter(text__contains=keyword, perm=0).values('user__name', 'text', 'date').order_by('date')
    return obj


def fetch_weibo_by_user_name(user_name):
    # 供用户个人主页使用的方法,
    # 抽取特定用户所有微博,按照从新到旧排序
    ret = models.Weibo.objects.filter(user__name=user_name).all().values().order_by('-date')
    return ret


def fetch_user_info_by_name(user_name):
    # 登录方法使用
    # 查询到用户信息 uid name 加到session
    data = {}
    obj = models.User.objects.get(username=user_name)
    data['uid'] = obj.userprofile.user_id
    data['name'] = obj.userprofile.name
    return data

