# pattern
使用scrapy框架爬取中国专利网信息             
前言
    本文中如有错误，请指正，谢谢！

背景

    默认情况下，scrapy.Request都是采用GET请求,但是我们也会遇到需要发送post请求的时候，如爬取专利网的专利信息时（http://epub.sipo.gov.cn/） 。
![1](https://github.com/wei523712/pattern/blob/master/pattern/img/1.png)
    因此，我们需要发送post请求，也不是scrapy.Request默认的GET请求。

码上分析

    使用FormRequest(url,formdata,callback)可以构造post请求。如果希望程序执行一开始就发送post请求，可以重写Spider类的start_requests(self)方法。同时，使用FormRequest.from_response()方法，可以实现模拟用户登录。
    进入专利网搜索页面，随便搜索一家公司，此处搜索百度，进入搜索列表页。点开开发者工具Network，然后换一页，可以看到Network中的请求。
![2](https://github.com/wei523712/pattern/blob/master/pattern/img/2.png)
从图中可以看到此处为post，字段如图右下角示。其中:

- strSources：外观 pdg 实用新型 pug 发明授权 pig 发明公布 pip ，此外我们提取发明授权的专利信息。
- numSortMethod：查找出的结果的排序方式，网页左下角有四种排序方式。
- pagesize：每页显示的数量，每页三条或者每页十条。
- pagenow：当前页数
- strwhere：要查找的公司名，有固定格式，"PA,IN,AGC,AGT+='%" + company(要查找的公司名) + "%' or PAA,TI,ABH+='" + company(要查找的公司名) + "'"                        
代码为：
```
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
            yield scrapy.FormRequest(url=self.start_urls[0],formdata=formdatas,callback=self.parse,meta={'data':formdatas})
 ```
    知道了怎么发送请求，接下来就可以去提取网页的总页数，以实现翻页。
    现在我们要提取页面显示的字段信息。打开Elements可以看到大部分要提取的字段信息的关键字和值 都是在一个标签中的，如图：          
    ![3](https://github.com/wei523712/pattern/blob/master/pattern/img/3.png)
    如果我们要单独把值拿出来，则需要通过正则表达式提取出来，此处我们在提取发明类型和专利名称时，使用re_first()方法，并且提取中文字符的正则为：[\u4E00-\u9FA5]+                
   代码：

    def parse(self, response):
        item = PatternItem()

        formdatas = response.meta['data']
        bigtag = response.xpath('//div[@class="w790 right"]/div[@class="cp_box"]')
        for tag in bigtag:
            #发明类型
            fmlx = tag.xpath('./div[@class="cp_linr"]/h1/text()').re_first('[\u4E00-\u9FA5]+')
            #专利名称
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
    提取到的数据如图所示：
![4](https://github.com/wei523712/pattern/blob/master/pattern/img/4.png)

