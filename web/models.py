from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Weibo(models.Model):
    '''所有微博'''
    wb_type_choices = (
        (0,'new'),
        (1,'forward'),
        (2,'collect'),
    )
    wb_type = models.IntegerField(choices=wb_type_choices,default=0)
    forward_or_collect_from = models.ForeignKey('self',related_name="forward_or_collects",blank=True,null=True,on_delete=models.CASCADE)
    user = models.ForeignKey('UserProfile',on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    text = models.CharField(max_length=140)
    hot = models.IntegerField(max_length=11,default=0)
    pictures_link_id = models.CharField(max_length=128,blank=True,null=True)
    video_link_id = models.CharField(max_length=128,blank=True,null=True)
    perm_choice = ((0,'public'),
                   (1,'private'),
                   (2,'friends'))
    perm = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

class Topic(models.Model):
    '''话题'''
    name = models.CharField(max_length=140)
    date = models.DateTimeField()
    def __str__(self):
        return self.name
class Category(models.Model):
    '''微博分类'''

    name = models.CharField(max_length=32)
    def __str__(self):
        return self.name

class Comment(models.Model):
    '''评论'''
    to_weibo = models.ForeignKey(Weibo,on_delete=models.CASCADE)
    p_comment = models.IntegerField(max_length=64)
    user = models.ForeignKey('UserProfile',on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    parent_name = models.CharField(max_length=64)
    hot = models.IntegerField(max_length=11, default=1)
    comment_type_choices = ((0,'comment'),(1,'thumb_up'))
    comment_type = models.IntegerField(choices=comment_type_choices,default=0)
    comment = models.CharField(max_length=140)
    date  = models.DateTimeField(auto_created=True)

    def __str__(self):
        return self.comment

class Tags(models.Model):
    '''标签'''
    name = models.CharField(max_length=64)
    def __str__(self):
        return self.name

class UserProfile(models.Model):
    '''用户信息'''

    user = models.OneToOneField(User)
    name = models.CharField(max_length=64)
    password = models.CharField(max_length=64)
    brief = models.CharField(max_length=140,blank=True,null=True)
    sex_type = ((1,'Male'),(0,'Female'))
    sex = models.IntegerField(choices=sex_type,default=1)
    age = models.PositiveSmallIntegerField(blank=True,null=True)
    email = models.EmailField()
    tags = models.ManyToManyField(Tags)
    head_img = models.ImageField(upload_to='static/Commons/Images/user_face/')
    attention=models.TextField(max_length=1000)
    at_message=models.TextField(max_length=1000)


    follow_list = models.ManyToManyField('self',blank=True,related_name="my_followers",symmetrical=False)

    #registration_date = models.DateTimeField(auto_created=True)
    def __str__(self):
        return self.name
