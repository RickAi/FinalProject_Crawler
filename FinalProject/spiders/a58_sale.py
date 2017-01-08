# -*- coding: utf-8 -*-
import re

import demjson
import scrapy

from FinalProject.items import SaleItem


class A58SaleSpider(scrapy.Spider):
    name = "58_sale"
    allowed_domains = ["58.com"]
    start_urls = ['http://bj.58.com/ershoufang/']

    def start_requests(self):
        requests = []
        for index in range(1, 2):
            request = scrapy.Request(self.start_urls[0] + "pn%s/" % index)
            requests.append(request)
        return requests

    def parse(self, response):
        for info in response.xpath('//body/div/div/div/table/tr/td/p/a'):
            house_href = info.xpath('attribute::href').extract()[0]
            house_url = house_href.split('?')[0]

            if not house_url.startswith(self.start_urls[0]):
                continue

            yield scrapy.Request(house_url, callback=self.parse_house_page, dont_filter=True)

    def parse_house_page(self, response):
        item = SaleItem()
        item['updated_date'] = response.xpath('//*[@id="main"]/div[1]/div[1]/div[2]/ul[1]/li[@class="time"]/text()').extract()[0].strip()
        item['title'] = response.xpath('//head/title/text()').extract()[0].strip()
        # 这里匹配城市信息
        city_query_1 = response.xpath('//head/meta[@name="location"]/attribute::content').extract()
        if city_query_1:
            item['city'] = city_query_1[0].split(';')[1].split('=')[1]
        else:
            city_query_2 = response.xpath('/html/head/script[2]/text()').re(r'"locallist"\:\[.*?\]')[0]
            city_query_2_json = demjson.decode('{' + city_query_2 + '}')
            item['city'] = city_query_2_json['locallist'][0]['name']

        # info_1匹配name,lon,lat,baidulon,baidulat
        info_1 = response.xpath('/html/head/script[2]/text()').re(r'"xiaoqu"\:\{.*?\}')[0]
        info_1_josn = demjson.decode('{' + info_1 + '}')['xiaoqu']
        item['house_name'] = info_1_josn['name']
        item['latitude'] = info_1_josn['baidulat']
        item['longitude'] = info_1_josn['baidulon']

        # info_2匹配面积,价格
        info_2 = response.xpath('//html').re(r'\{\"I\"\:1081.*?\}')[0]
        info_2_josn = demjson.decode(info_2)
        info_2_split = info_2_josn['V']
        item['house_area'] = info_2_split
        info_2 = response.xpath('//html').re(r'\{\"I\"\:1078.*?\}')[0]
        info_2_josn = demjson.decode(info_2)
        info_2_split = info_2_josn['V']
        item['total_price'] = info_2_split

        # 单价
        try:
            per_price_detail = response.xpath('//*[@id="main"]/div[1]/div[2]/div[2]/ul/li[1]/div[2]/text()').extract()[1].strip()
            item['per_price'] = re.findall(r'\d+', re.search(r'\d+元', per_price_detail).group(0))[0]
        except:
            item['per_price_detail'] = 0

        # 房间细节
        room_detail = response.xpath('//*[@id="main"]/div[1]/div[2]/div[2]/ul/li[4]/div[2]/text()').extract()[0].strip()
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

        # info_3匹配地址
        info_3 = response.xpath('//body/div/section/div/div/div/ul/li/text()').re(r'\<a\s*href.*a\>')
        temp_addr = ''
        for address in info_3:
            temp_addr = temp_addr + '-' + address

        item['url'] = response.request.url
        item['address'] = temp_addr.lstrip('-')
        item['source'] = '58'
        item['district'] = ''

        yield item
