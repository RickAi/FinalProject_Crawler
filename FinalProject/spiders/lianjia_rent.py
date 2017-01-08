# -*- coding: utf-8 -*-
import re
import scrapy
from FinalProject.items import RentItem

class LianjiaSpider(scrapy.Spider):
    name = "lianjia_rent"
    allowed_domains = ["lianjia.com"]
    start_urls = ['http://bj.lianjia.com/zufang/']

    def start_requests(self):
        requests = []
        for index in range(1, 101):
            request = scrapy.Request(self.start_urls[0] + "pg%s/" % index)
            requests.append(request)
        return requests

    def parse(self, response):
        house_page_query = '//body/div/div/div/div/ul[@id="house-lst"]/li/div[@class="info-panel"]/h2/a[@href]'
        count = 1
        for info in response.xpath(house_page_query):
            house_page_href = info.xpath('attribute::href').extract()[0]
            updated_date = response.xpath('//*[@id="house-lst"]/li[%s]/div[2]/div[2]/div[2]/text()' % count) \
                .extract()[0].split(' ')[0].replace(".", "-")
            house_page_url = house_page_href

            count += 1
            yield scrapy.Request(house_page_url, callback=self.parse_house_page, dont_filter=True,
                                 meta={'updated_date': updated_date})

    def parse_house_page(self, response):
        item = RentItem()
        item['url'] = response.request.url
        item['title'] = response.xpath('//html/head/title/text()').extract()[0]

        try:
            room_detail = re.findall(r'\d+', re.search(r'\d室\d厅', item['title']).group(0))
            item['bedroom_count'] = room_detail[0]
            item['livingroom_count'] = room_detail[1]
        except:
            item['bedroom_count'] = str(-1)
            item['livingroom_count'] = str(-1)

        item['updated_date'] = response.request.meta['updated_date']
        item['city'] = response.xpath('//head/script/text()').re(r'city_name.*\'')[0].split('\'')[-2]
        item['address'] = ''
        item['district'] = ''

        info_parse_1 = response.xpath('//html').re(r'resblockName.*,')
        if info_parse_1:
            yield scrapy.Request(response.request.url, callback=self.parse_house_page_res, dont_filter=True,
                                 meta={'items': item})
        else:
            yield scrapy.Request(response.request.url, callback=self.parse_house_page_com, dont_filter=True,
                                 meta={'items': item})

    def parse_house_page_res(self, response):
        item = response.request.meta['items']
        # 这个类型的网页只能通过正则表达式匹配信息
        item['house_area'] = \
            re.findall(r'[-+]?([0-9]*\.[0-9]+|[0-9]+)', response.xpath('//html').re(r'area.*,')[0].split('\'')[1])[0]
        item['house_name'] = response.xpath('//html').re(r'resblockName.*,')[0].split('\'')[1]
        item['price'] = response.xpath('//html').re(r'totalPrice.*,')[0].split('\'')[1]
        if response.xpath('//html').re(r'resblockPosition.*,'):
            item['longitude'] = \
                response.xpath('//html').re(r'resblockPosition.*,')[0].split('\'')[1].split(',')[1]
            item['latitude'] = \
                response.xpath('//html').re(r'resblockPosition.*,')[0].split('\'')[1].split(',')[0]
        else:
            item['longitude'] = None
            item['latitude'] = None

        item['source'] = 'lianjia'

        yield item

    def parse_house_page_com(self, response):
        item = response.request.meta['items']
        house_price_query = '//body/div/section/div/div[@class="desc-text clear"]/dl/dd/span/strong[@class="ft-num"]/text()'
        item['price'] = str(response.xpath(house_price_query).extract()[0])

        house_area_query = '//body/div/section/div/div[@class="desc-text clear"]/dl/dd/span/i/text()'
        item['house_area'] = str(response.xpath(house_area_query).extract()[0].replace('/', '').strip()[:-1])

        house_name_query = '//body/div/section/div/div[@class="desc-text clear"]/dl[@class="clear"]/dd/a[1]'
        if response.xpath(house_name_query).xpath('attribute::target').extract():
            house_name_query = '//body/div/section/div/div[@class="desc-text clear"]/dl[@class="clear"]/dd/text()'
            item['house_name'] = response.xpath(house_name_query).extract()[0]
        else:
            item['house_name'] = response.xpath(house_name_query).xpath('text()').extract()[0]

        # 这里匹配经纬度
        lnglat_query = response.xpath('/html').re(r'coordinates.*?]')
        if lnglat_query:
            item['latitude'] = lnglat_query[0].split('[')[-1].split(',')[0]
            item['longitude'] = lnglat_query[0].split('[')[-1].split(',')[1][:-1]
        else:
            item['latitude'] = None
            item['longitude'] = None

        yield item
