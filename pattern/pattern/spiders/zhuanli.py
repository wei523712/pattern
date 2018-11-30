# -*- coding: utf-8 -*-
import scrapy
#import urllib.parse
import re
from pattern.items import PatternItem


class ZhuanliSpider(scrapy.Spider):
    name = 'zhuanli'
    #allowed_domains = ['epub.sipo.gov.cn']
    start_urls = ['http://epub.sipo.gov.cn/patentoutline.action']
    page = 1

    def start_requests(self):
        f = open('list.txt','r',encoding='utf-8')
        for per in f:
            company = per.strip()
            string = "PA,IN,AGC,AGT+='%" + company + "%' or PAA,TI,ABH+='" + company + "'"
            formdatas = {'showType':'1','strSources':'pig','strWhere':string,
                    'numSortMethod':'4','strLicenseCode':'','numIp':'0',
                    'numIpc':'','numIg':'0','numIgc':'','numIgd':'','numUg':'0',
                    'numUgc':'','numUgd':'','numDg':'0','numDgc':'',
                    'pageSize':'3','pageNow':'1'}
        #strSources   外观pdg    实用新型pug    发明授权pig    发明公布pip

            yield scrapy.FormRequest(url=self.start_urls[0],formdata=formdatas,callback=self.parse,meta={'data':formdatas})

    def parse(self, response):
        item = PatternItem()

        formdatas = response.meta['data']
        bigtag = response.xpath('//div[@class="w790 right"]/div[@class="cp_box"]')
        for tag in bigtag:
            fmlx = tag.xpath('./div[@class="cp_linr"]/h1/text()').re_first('[\u4E00-\u9FA5]+')
            mc = tag.xpath('./div[@class="cp_linr"]/h1/text()').re('[\u4E00-\u9FA5]+')[-1]
            sqggh = tag.xpath('./div[@class="cp_linr"]/ul/li[1]/text()').re_first('授权公告号：(.+)')
            sqggr = tag.xpath('./div[@class="cp_linr"]/ul/li[2]/text()').re_first('授权公告日：(.+)')
            sqh = tag.xpath('./div[@class="cp_linr"]/ul/li[3]/text()').re_first('申请号：(.+)')
            sqr = tag.xpath('./div[@class="cp_linr"]/ul/li[4]/text()').re_first('申请日：(.+)')
            tysqh = tag.xpath('./div[@class="cp_linr"]/ul/li[5]/text()').re_first('同一申请的已公布的文献号：(.+)')
            sqgbr = tag.xpath('./div[@class="cp_linr"]/ul/li[6]/text()').re_first('申请公布日：(.+)')
            zlqr = tag.xpath('./div[@class="cp_linr"]/ul/li[7]/text()').re_first('专利权人：(.+)')
            fmr = tag.xpath('./div[@class="cp_linr"]/ul/li[8]/text()').re_first('发明人：(.+)')
            dz = tag.xpath('./div[@class="cp_linr"]/ul/li[10]/text()').re_first('地址：(.+)')
            flh1 = tag.xpath('./div[@class="cp_linr"]/ul/li[11]/text()').extract_first()
            pattern = '分类号：(.+)'
            if flh1:
                flh = re.findall(pattern,flh1)[0]
            else:
                flh = '暂无信息'
            zy = tag.xpath('./div[@class="cp_linr"]/div[@class="cp_jsh"]/span[2]/text()').extract_first()
            qt1 = tag.xpath('./div[@class="cp_linr"]/ul/li[11]/div/ul')
            qt = qt1.xpath('string(.)').extract_first()

            item['pat_type'] = fmlx.strip() if fmlx else '暂无此信息'
            item['pat_name'] = mc.strip() if mc else '暂无此信息'
            item['auth_num'] = sqggh.strip() if sqggh else '暂无此信息'
            item['auth_date'] = sqggr.strip() if sqggr else '暂无此信息'
            item['appli_num'] = sqh.strip() if sqh else '暂无此信息'
            item['appli_date'] = sqr.strip() if sqr else '暂无此信息'
            item['same_request'] = tysqh.strip() if tysqh else '暂无此信息'
            item['request_date'] = sqgbr.strip() if sqgbr else '暂无此信息'
            item['patentee'] = zlqr.strip() if zlqr else '暂无此信息'
            item['inventor'] = fmr.strip() if fmr else '暂无此信息'
            item['address'] = dz.strip() if dz else '暂无此信息'
            item['class_number'] = flh.strip() if flh else '暂无此信息'
            item['abstract'] = zy if zy else '暂无此信息'
            item['others'] = qt.strip() if qt else '暂无此信息'

            yield item

        #翻页
        total_page = response.xpath('//div[@class="next"]/a/text()').re('\d+')
        if (total_page) and (self.page < int(total_page[-1])):
            self.page += 1
            urls = 'http://epub.sipo.gov.cn/patentoutline.action'

            formdatas['pageNow'] = str(self.page)
            yield scrapy.FormRequest(urls,callback=self.parse,formdata=formdatas,meta={'data':formdatas})

