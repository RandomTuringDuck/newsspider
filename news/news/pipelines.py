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
        if item.get('news_id',None) is None:
            return item
        flag = {'news_id':item['news_id']}
        self.mongodb.update({flag},{'$set':dict(item)},upsert=True)
        return None

