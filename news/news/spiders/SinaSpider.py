import scrapy
import json
import datetime
import logging
from news.items import NewsItem,CommentItem,CmntNumItem


class SinaSpider(scrapy.Spider):
    name = "sina"
    allowed_domins=['news.sina.com.cn']

    #这个是一开始运行的函数，按照日期构造api,新闻篇数直接弄个了定值1000，90,91,92是国内、国际、社会三个频道
    def start_requests(self):
        url = "http://roll.news.sina.com.cn/interface/rollnews_ch_out_interface.php?col=90,91,92&spec=&" \
              "type=&date=%s&ch=01&k=&offset_page=0&offset_num=0&num=1000&asc=&page=1"
        begin = datetime.date(2017, 1, 1)
        end = datetime.date.today()
        #获取begin到end的每一天，然后放到url中去请求
        for i in range((end - begin).days + 1):
            day = str(begin + datetime.timedelta(days=i))
            temp = url%(day)
            #请求url,回调函数是parse
            yield scrapy.Request(temp, self.parse)

    def parse(self,response):
        body = response.body
        #获取的是bytes数据，转成国标码,这个视情况而定
        body = str(body,'gbk')
        body = body[body.find("{"):-1]
        #eval函数是用来处理不太规范的json格式，将其转成字典
        data = eval(body, type('Dummy', (dict,), dict(__getitem__=lambda s,n:n))())
        url_list = data['list']
        print("一共有"+str(len(url_list))+"要爬")
        for i in url_list:
            if i['url'].startswith("http://video"):
                continue
            #去爬每篇文章
            yield scrapy.Request(i['url'], callback=self.parse_article)

    #用来获取新闻详情
    def parse_article(self,response):
        #爬新闻
        if "comment5" not in response.url:
            item = NewsItem()
            item['news_url'] = response.url
            item['news_from'] = 'sina'
            self.get_id_channel(response,item)
            self.get_title(response,item)
            self.get_source(response,item)
            self.get_time(response,item)
            self.get_body(response,item)
            self.get_keywords(response,item)
            comment_url = "http://comment5.news.sina.com.cn/page/info?version=1&channel=%s&newsid=" \
                      "comos-%s&group=0&compress=0&ie=utf-8&oe=utf-8&page=%s&page_size=%s&format=json"
            item['flag'] = "news"
            #构造评论api
            now = comment_url % (item['news_channel'], item['news_id'],1,200)
            req = scrapy.Request(now, callback=self.parse_article)
            req.meta['newsid']=item['news_id'] #往回调函数传值
            yield req
            yield item

        #爬评论，因为sina限制每页只能爬200个评论，干脆就爬200个了，不再多爬了，其他网站视情况而定
        elif "comment5" in response.url:
            cmnt = response.body
            data = json.loads(cmnt)
            citem = CmntNumItem()
            #这里从评论中获取评论数目和参与人数，用来更新News
            if data['result'].get('count') is None:
                citem['news_show'] = 0
                citem['news_total'] = 0
            else:
                citem['news_show'] = data['result']['count'].get('show', 0)
                citem['news_total'] = data['result']['count'].get('total', 0)
            citem['news_id']=response.meta['newsid']
            citem['flag']='update'
            yield citem
            #下面是产生评论的Item
            if data['result'].get('cmntlist',None) is not None:
                cmlist = data['result']['cmntlist']
                item = CommentItem()
                print('这一页有多少评论',len(cmlist))
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
