# -*- coding: utf-8 -*-
import re

import scrapy

from FinalProject.items import RentItem

class A5i5jRentSpider(scrapy.Spider):
    name = "5i5j_rent"
    allowed_domains = ["5i5j.com"]
    start_urls = ['http://bj.5i5j.com/rent/']

    def start_requests(self):
        requests = []
        for index in range(1, 201):
            request = scrapy.Request(self.start_urls[0] + "pn%s/" % index)
            requests.append(request)
        return requests

    def parse(self, response):
        house_page_query = '//body/section/div/div/div/ul[@class="list-body"]/li'
        house_page_root = response.request.url.split('/')[2]
        for info in response.xpath(house_page_query):
            house_page_href = info.xpath('a/attribute::href').extract()[0]
            house_page_url = 'http://' + house_page_root + house_page_href
            yield scrapy.Request(house_page_url, callback=self.parse_house_page)

    def parse_house_page(self, response):
        item = RentItem()
        item['title'] = response.xpath('//html/head/title/text()').extract()[0].split('_')[0].strip()
        item['url'] = response.request.url

        if response.xpath('//*[@id="scroll"]/body/section[2]/div/div/ul/li[1]/span[2]/text()').extract()[0] != '整租':
            return

        try:
            room_detail = response.xpath('//*[@id="scroll"]/body/section[2]/div/div/ul/li[2]/ul/li[1]/text()').extract()[0]
            room_detail = re.findall(r'\d+', re.search(r'\d室\d厅', room_detail).group(0))
            item['bedroom_count'] = room_detail[0]
            item['livingroom_count'] = room_detail[1]
        except:
            item['bedroom_count'] = str(-1)
            item['livingroom_count'] = str(-1)

        # 此XPath节点可以获得房屋的所有基本信息
        house_info_query = '//body/section/div/div/ul'

        price_query = 'li[1]/span/text()'
        item['price'] = response.xpath(house_info_query).xpath(price_query).extract()[0]

        area_query = 'li/ul/li[3]/text()'
        item['house_area'] = response.xpath(house_info_query).xpath(area_query).extract()[0]

        name_query = 'li[3]/text()'
        item['house_name'] = response.xpath(house_info_query).xpath(name_query).extract()[0].strip()

        try:
            item['updated_date'] = response.xpath('//*[@id="scroll"]/body/section[3]/div/section[1]/dl[1]/dd/p[6]/text()').extract()[0]
        except:
            item['updated_date'] = ''

        # 这里请求房屋的地址和城市
        item['address'] = response.xpath('//body/section/div/section/div[@class="xq-intro-info"]/ul/li[3]/text()').extract()[0]
        item['city'] = response.xpath('//body').re(r'mapCityName.*;?')[0].split('\"')[-2]
        item['address'] = ''
        item['district'] = ''

        item['latitude'] = response.xpath('//body').re(r'mapY.*;?')[0].split('=')[-1].split(';')[0].replace('"', '')
        item['longitude'] = response.xpath('//body').re(r'mapX.*;?')[0].split('=')[-1].split(';')[0].replace('"', '')

        item['source'] = '5i5j'

        yield item
