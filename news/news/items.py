# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    news_id = scrapy.Field() #唯一标识
    news_title = scrapy.Field()
    news_time = scrapy.Field()
    news_url = scrapy.Field()
    news_source = scrapy.Field() #这个是新闻的真正来源
    news_from = scrapy.Field() #这个是从网易、新浪等爬下来的
    news_body = scrapy.Field() #新闻内容
    news_total = scrapy.Field() #参与人数
    news_comment_count = scrapy.Field() #跟帖数
