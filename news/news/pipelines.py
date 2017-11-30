# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo


class NewsPipeline(object):

    def __init__(self):
        HOST = '127.0.0.1'
        POST = 27017
        client = pymongo.MongoClient(HOST,POST)
        self.mongodb = client.news


    def process_item(self, item, spider):
        news_item = dict(item)
        if spider.name == "sina":
            if news_item['flag'] == "news":
                flag = {'news_id': item['news_id']}
                self.mongodb.sina.update(flag,{'$set':news_item},True)
            elif news_item['flag'] == "comment":
                flag = {'mid':item['mid']}
                self.mongodb.sinacmt.update(flag,{'$set':news_item},True)
            elif news_item['flag']=='update':
                flag = {'news_id': item['news_id']}
                del news_item['flag']
                self.mongodb.sina.update(flag, {'$set': news_item})
        return None



