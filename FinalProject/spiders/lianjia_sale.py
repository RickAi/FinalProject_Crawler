# -*- coding: utf-8 -*-
import re

import scrapy
from FinalProject.items import SaleItem

class LianjiaSaleSpider(scrapy.Spider):
    name = "lianjia_sale"
    allowed_domains = ["lianjia.com"]
    start_urls = ['http://bj.lianjia.com/ershoufang/']

    def start_requests(self):
        requests = []
        for index in range(1, 101):
            request = scrapy.Request(self.start_urls[0] + "pg%s/" % index)
            requests.append(request)
        return requests

    def parse(self, response):
        house_page_query = '/html/body/div[4]/div[1]/ul/li/div[1]/div[1]/a'
        for info in response.xpath(house_page_query):
            house_page_url = info.xpath('attribute::href').extract()[0]
            yield scrapy.Request(house_page_url, callback=self.parse_house_page, dont_filter=True)

    def parse_house_page(self, response):
        item = SaleItem()
        item['title'] = response.xpath('//html/head/title/text()').extract()[0]
        item['city'] = response.xpath('//head/script/text()').re(r'city_name.*\'')[0].split('\'')[-2]
        item['updated_date'] = response.xpath('//*[@id="introduction"]/div/div/div[2]/div[2]/ul/li[1]/text()').extract()[0]

        # 房间细节
        room_detail = response.xpath('//*[@id="introduction"]/div/div/div[1]/div[2]/ul/li[1]/text()').extract()[0]
        try:
            item['bedroom_count'] = re.findall(r'\d+', re.search(r'\d室', room_detail).group(0))[0]
        except:
            item['bedroom_count'] = str(-1)
        try:
            item['livingroom_count'] = re.findall(r'\d+', re.search(r'\d厅', room_detail).group(0))[0]
        except:
            item['livingroom_count'] = str(-1)
        try:
            item['kitchen_count'] = re.findall(r'\d+', re.search(r'\d厨', room_detail).group(0))[0]
        except:
            item['kitchen_count'] = str(-1)
        try:
            item['wc_count'] = re.findall(r'\d+', re.search(r'\d卫', room_detail).group(0))[0]
        except:
            item['wc_count'] = str(-1)

        # other infos
        item['url'] = response.request.url
        item['district'] = ''
        item['address'] = ''
        item['source'] = 'lianjia'

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
        item['house_name'] = response.xpath('//html').re(r'resblockName.*,')[0].split('\'')[1]
        item['total_price'] = response.xpath('//html').re(r'totalPrice.*,')[0].split('\'')[1]
        item['per_price'] = response.xpath('//html').re(r'price.*,')[0].split('\'')[1]
        item['house_area'] = response.xpath('//html').re(r'area.*,')[0].split('\'')[1]
        if response.xpath('//html').re(r'resblockPosition.*,'):
            item['latitude'] = \
            response.xpath('//html').re(r'resblockPosition.*,')[0].split('\'')[1].split(',')[1]
            item['longitude'] = \
            response.xpath('//html').re(r'resblockPosition.*,')[0].split('\'')[1].split(',')[0]
        else:
            item['latitude'] = None
            item['longitude'] = None

        yield item

    def parse_house_page_com(self, response):
        item = response.request.meta['items']
        house_price_query = '//body/div/section/div/div[@class="desc-text clear"]/dl/dd/span/strong[@class="ft-num"]/text()'
        item['total_price'] = response.xpath(house_price_query).extract()[0]

        house_area_query = '//body/div/section/div/div[@class="desc-text clear"]/dl/dd/span/i/text()'
        item['house_area'] = response.xpath(house_area_query).extract()[0].replace('/', '').strip()[:-1]

        house_name_query = '//body/div/section/div/div[@class="desc-text clear"]/dl/dd/a[@data-el="community"]/text()'
        if response.xpath(house_name_query).extract():
            item['house_name'] = response.xpath(house_name_query).extract()[0]
        else:
            house_name_query = '//body/div/section/div/div[@class="desc-text clear"]/dl[@class="clear"]/dd/text()'
            item['house_name'] = response.xpath(house_name_query).extract()[0]

        # 这里匹配经纬度
        lnglat_query = response.xpath('/html').re(r'coordinates.*?]')
        if lnglat_query:
            item['latitude'] = lnglat_query[0].split('[')[-1].split(',')[0]
            item['longitude'] = lnglat_query[0].split('[')[-1].split(',')[1][:-1]
        else:
            item['latitude'] = None
            item['longitude'] = None

        yield item
