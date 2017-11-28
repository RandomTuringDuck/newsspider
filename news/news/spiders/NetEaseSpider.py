import scrapy
import re
import json
from scrapy.selector import Selector
from news.items import NewsItem
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider,Rule
class SinaSpider(CrawlSpider):
    name = "sina"
    allowed_domins=['news.sina.com.cn']
    start_urls = [
        "http://api.roll.news.sina.com.cn/zt_list?channel=news&cat_1=shxw&cat_2==zqsk||=qwys||=shwx||=fz-shyf&level==1||=2&show_ext=1&show_all=1&show_num=22&tag=1&format=json&page=1&callback=newsloadercallback&_=1511894306077"
    ]

    def parse(self,response):
        body = response.body
        #begin = len("newsloadercallback(")
        data = body[21:-2] #21是上面字符的长度
        data = json.loads(data) #把data转成json格式
        print(len(data['result']['data']))
        for i in data['result']['data']:
            yield scrapy.Request(i['url'], callback=self.parse_article)

    #回调函数,用来获取网页详情
    def parse_article(self,response):
        item = NewsItem()
        self.get_id(response,item)
        item['news_url'] = response.url
        self.get_title(response,item)
        self.get_source(response,item)
        item['news_from'] = 'sina'
        self.get_time(response,item)
        self.get_body(response,item)
        print("item是", item)
        yield item

    #获取标题
    def get_title(self,response,item):
        title = response.xpath('//div[@class="page-header"]/h1/text()').extract()[0]
        if title:
            item['news_title']=title

    #获取来源
    def get_source(self,response,item):
        source = response.xpath('//span[@data-sudaclick="content_media_p"]/a/text()').extract()[0]
        if source:
            item['news_source']= source

    #获取id
    def get_id(self,response,item):
        id = response.xpath('//div[@class="page-header"]/h1/@docid').extract()[0]
        item['news_id']=id

    #获取文章内容
    def get_body(self,response,item):
        body = response.xpath('//div[@id="artibody"]/p/text()').extract()
        num = 0
        while num < len(body):
            body[num] = body[num].replace(u'\u3000',u'')
            num += 1
        item['news_body']=body

    #获取文章时间
    def get_time(self,response,item):
        time = response.xpath('//span[@id="navtimeSource"]/text()').extract()[0]
        if time:
            item['news_time']=time[:-2]