# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

#一个item分三个部分，第一存新闻的内容，第二个在爬评论时用来更新新闻的评论数目和参与人数
#前两个都是要往新闻内容那张表里存的
#最后一个是用来存新闻评论，它的newsid与新闻内容的news_id对应

class NewsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    news_id = scrapy.Field() #唯一标识
    news_title = scrapy.Field() #标题
    news_time = scrapy.Field() #localtime
    news_keywords = scrapy.Field() #关键词
    news_url = scrapy.Field() #链接
    news_source = scrapy.Field() #这个是新闻的真正来源
    news_from = scrapy.Field() #这个是从网易、新浪等爬下来的
    news_body = scrapy.Field() #新闻内容
    news_channel = scrapy.Field() #频道
    flag =scrapy.Field()

#用来更新评论数目和参与人数，与上面的新闻item是一对
class CmntNumItem(scrapy.Item):
    news_id = scrapy.Field()  # 唯一标识
    news_show = scrapy.Field()  # 评论数目
    news_total = scrapy.Field()  # 参与人数
    flag = scrapy.Field()

class CommentItem(scrapy.Item):
    agree = scrapy.Field()  #赞同
    against = scrapy.Field()
    area = scrapy.Field()
    channel = scrapy.Field() #频道
    content = scrapy.Field() #评论内容
    ip= scrapy.Field()
    level= scrapy.Field() #可是回复的层数
    mid= scrapy.Field() #这个评论的标识
    newsid= scrapy.Field() #新闻id
    nick= scrapy.Field() #昵称
    parent= scrapy.Field() #这条评论的父亲
    parent_nick= scrapy.Field()
    parent_uid= scrapy.Field() #uid不知道啥用
    rank= scrapy.Field()
    thread= scrapy.Field() #这个可能是评论的根结点
    time= scrapy.Field() #时间
    uid= scrapy.Field()
    usertype= scrapy.Field() #内容基本是wb，可能是微博上评论的
    flag = scrapy.Field()
