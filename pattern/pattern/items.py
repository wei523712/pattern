# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PatternItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pat_type = scrapy.Field()        #专利类型
    pat_name = scrapy.Field()        #专利名称
    auth_num = scrapy.Field()        #授权公告号
    auth_date = scrapy.Field()       #授权公告日
    appli_num = scrapy.Field()       #申请号
    appli_date = scrapy.Field()      #申请日
    same_request = scrapy.Field()    #同一申请的已公布的文献号
    request_date = scrapy.Field()    #申请公布日
    patentee = scrapy.Field()        #专利权人
    inventor = scrapy.Field()        #发明人
    address = scrapy.Field()         #地址
    class_number = scrapy.Field()    #分类号
    abstract = scrapy.Field()        #摘要
    others = scrapy.Field()          #其它
