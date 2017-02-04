# -*- coding: utf-8 -*-
import re

import demjson
import scrapy

from FinalProject.items import SaleItem


class A5i5jSaleSpider(scrapy.Spider):
    name = "5i5j_sale"
    allowed_domains = ["5i5j.com"]
    start_urls = ['http://bj.5i5j.com/exchange/']

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
        item = SaleItem()
        item['url'] = response.request.url
        item['title'] = response.xpath('//html/head/title/text()').extract()[0].split('_')[0]

        # 此XPath节点可以获得房屋的所有基本信息
        house_info_query = '//body/section/div/div/ul'

        area_query = 'li/ul/li[3]/text()'
        item['house_area'] = response.xpath(house_info_query).xpath(area_query).extract()[0]

        item['total_price'] = response.xpath('//*[@id="scroll"]/body/section[2]/div/div/ul/li[1]/span/text()').extract()[0]
        per_price_detail = response.xpath('//*[@id="scroll"]/body/section[2]/div/div/ul/li[2]/ul/li[2]/text()').extract()[1].strip()
        try:
            item['per_price'] = re.findall(r'\d+', re.search(r'\d+元', per_price_detail).group(0))[0]
        except:
            item['per_price'] = ''

        name_query = 'li[3]/text()'
        item['house_name'] = response.xpath(house_info_query).xpath(name_query).extract()[0].strip()

        histroy_price_query = '//body/section/div/section/div/script/text()'
        histroy_price_json = response.xpath(histroy_price_query).extract()[0].split(';')[1].split('=')[1]
        histroy_price_dejson = demjson.decode(histroy_price_json)
        histroy_price_data = histroy_price_dejson['xAxis'][0]['data']
        item['updated_date'] = histroy_price_data[0]

        # 房间细节
        room_detail = response.xpath('//*[@id="scroll"]/body/section[2]/div/div/ul/li[2]/ul/li[1]/text()').extract()[1].strip()
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

        # 这里请求房屋的地址和城市
        item['city'] = response.xpath('//body').re(r'mapCityName.*;?')[0].split('\"')[-2]
        # 这里请求房屋的地址和城市
        item['address'] = \
        response.xpath('//body/section/div/section/div[@class="xq-intro-info"]/ul/li[3]/text()').extract()[0]
        item['district'] = ''

        item['longitude'] = response.xpath('//body').re(r'mapY.*;?')[0].split('=')[-1].split(';')[0].replace(
            '"', '')
        item['latitude'] = response.xpath('//body').re(r'mapX.*;?')[0].split('=')[-1].split(';')[0].replace(
            '"', '')
        item['source'] = '5i5j'

        yield item
