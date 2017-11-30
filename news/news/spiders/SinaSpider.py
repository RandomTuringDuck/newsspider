import scrapy
import re
import math
import time
import json
import requests
import datetime
import logging
from news.items import NewsItem,CommentItem
class SinaSpider(scrapy.Spider):
    name = "sina"
    allowed_domins=['news.sina.com.cn']

    def pretreat(self,url):
        res = requests.get(url)
        res.encoding='gb2312'
        data = str(res.text)
        data = data[data.find("{"):-1]
        #因为取回来的json数据不规范，用eval来处理一下
        data = eval(data, type('Dummy', (dict,), dict(__getitem__=lambda s, n: n))())
        #返回一共有多少条新闻
        return data['count']

    def start_requests(self):
        #url = "http://api.roll.news.sina.com.cn/zt_list?channel=news&cat_1=shxw&cat_2==zqsk||=qwys||=shwx||=fz-shyf&level==1||=2&show_ext=1&show_all=1&show_num=22&tag=1&format=json&page=%s&callback=newsloadercallback&_=1511894306077"
        url = "http://roll.news.sina.com.cn/interface/rollnews_ch_out_interface.php?col=90,91,92&spec=&" \
              "type=&date=%s&ch=01&k=&offset_page=0&offset_num=0&num=%s&asc=&page=1"
        begin = datetime.date(2017, 5, 1)
        end = datetime.date.today()
        #获取begin到end的每一天，然后放到url中去请求
        for i in range((end - begin).days + 1):
            day = str(begin + datetime.timedelta(days=i))
            temp = url%(day,1)
            #获取这一天的新闻数
            num = self.pretreat(temp)
            temp = url%(day,str(num))
            yield scrapy.Request(temp, self.parse)

    def parse(self,response):
        body = response.body
        #获取的是bytes数据，转成国标码
        body = str(body,'gbk')
        body = body[body.find("{"):-1]
        data = eval(body, type('Dummy', (dict,), dict(__getitem__=lambda s,n:n))())
        list = data['list']
        for i in list:
            request = scrapy.Request(i['url'], callback=self.parse_article)
            request.meta['sjc']=i['time']
            yield request

    #回调函数,用来获取网页详情
    def parse_article(self,response):
        if "comment5" not in response.url:
            item = NewsItem()
            item['news_url'] = response.url
            item['news_from'] = 'sina'
            item['news_sjc'] = response.meta['sjc']
            self.get_id_channel(response,item)
            self.get_title(response,item)
            self.get_source(response,item)
            self.get_time(response,item)
            self.get_body(response,item)
            self.get_keywords(response,item)
            comment_url = "http://comment5.news.sina.com.cn/page/info?version=1&channel=%s&newsid=" \
                      "comos-%s&group=0&compress=0&ie=gbk&oe=gbk&page=%s&page_size=200"
            now = comment_url % (item['news_channel'], item['news_id'], 1)
            tmp = requests.get(now).text
            #tmp = self.html_decode(tmp)
            tmp = json.loads(tmp)
            item['news_show'] = tmp['result']['count']['show']
            item['news_total'] = tmp['result']['count']['total']
            item['flag']="news"
            page = math.ceil(item['news_show'] / 200)  # 向上取整
            yield item
            for i in range(1, page + 1):
                now = comment_url % (item['news_channel'], item['news_id'], i)
                yield scrapy.Request(now, callback=self.parse_article)

        elif "comment5" in response.url:
            cmnt = response.body
            data = json.loads(cmnt)
            cmlist = data['result']['cmntlist']
            item = CommentItem()
            for i in range(len(cmlist)):
                item['flag']="comment"
                item['agree']=cmlist[i]['agree']
                item['against']=cmlist[i]['against']
                item['area']=cmlist[i]['area']
                item['channel']=cmlist[i]['channel']
                item['content']=cmlist[i]['content']
                item['ip']=cmlist[i]['ip']
                item['level']=cmlist[i]['level']
                item['mid']=cmlist[i]['mid']
                item['newsid'] = cmlist[i]['newsid'].strip('comos-')
                item['nick'] = cmlist[i]['nick']
                item['parent'] = cmlist[i]['parent']
                item['parent_nick'] = cmlist[i]['parent_nick']
                item['parent_uid'] = cmlist[i]['parent_uid']
                item['rank'] = cmlist[i]['rank']
                item['thread'] = cmlist[i]['thread']
                item['time'] = cmlist[i]['time']
                item['uid'] = cmlist[i]['uid']
                item['usertype'] = cmlist[i]['usertype']
                yield item

    #获取关键词
    def get_keywords(self,response,item):
        keywords = response.xpath('//div[@class="article-keywords"]/a/text()').extract()
        if keywords:
            item['news_keywords']= keywords

    #获取标题
    def get_title(self,response,item):
        title = response.xpath('//div[@class="page-header"]/h1/text()').extract()
        if len(title):
            item['news_title']=title[0]

    #获取来源
    def get_source(self,response,item):
        source = response.xpath('//span[@data-sudaclick="content_media_p" or @data-sudaclick="media_name"]/a/text()').extract()
        if len(source):
            item['news_source']= source[0]

    #获取id
    def get_id_channel(self,response,item):
        id = response.xpath('//meta[@name="publishid"]/@content').extract()
        if len(id):
            item['news_id']=id[0]
        channel = response.xpath('//meta[@name="comment"]/@content').extract()
        if len(channel):
            tmp = channel[0].split(":")
            item['news_channel']=tmp[0]


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
        time = response.xpath('//span[@id="navtimeSource"]/text()').extract()
        if len(time):
            item['news_time']=time[0][:-2]

    def sina_api_process(self,res):
        """
        json格式清理，处理api 的response 返回的json,包括1.json数据说明 2.会引起错误的特殊字符
        """
        try:
            data=res.decode("gbk").encode("utf-8")
            value=data[14:-1]
            value=value.replace("'s "," s ")
            keylist=["serverSeconds","last_time","path","title","cType","count","offset_page","offset_num","list","channel","url","type","pic"]
            #关键字+ 空格作为识别键值关键字的格式
            for i in keylist:
                value=value.replace(i+" ","\""+i+"\"")
            value=value.replace("time :","\"time\":")
            value=value.replace("id :","\"id\":")
            #去除会引起错误的 特殊字符
            badwords=["\b"]
            for i in badwords:
                value=value.replace(i,"")
            value=value.replace("'", "\"")
            return value
        except Exception as ex :
            logging.error("error  1:Parse ERROR"+str(ex))