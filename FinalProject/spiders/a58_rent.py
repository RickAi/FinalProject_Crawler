# -*- coding: utf-8 -*-
import datetime
import re

import demjson
import scrapy
import time
from FinalProject.items import RentItem

class A58RentSpider(scrapy.Spider):
    name = "58_rent"
    allowed_domains = ["58.com"]
    start_urls = ['http://bj.58.com/zufang/']

    def start_requests(self):
        requests = []
        for index in range(1, 2):
            request = scrapy.Request("http://bj.58.com/zufang/pn%s/" % index)
            requests.append(request)
        return requests

    def parse(self, response):
        house_page_query = '/html/body/div[3]/div[1]/div[5]/div[2]/ul/li/div[2]/h2/a'
        for info in response.xpath(house_page_query):
            house_href = info.xpath('attribute::href').extract()[0]
            house_url = house_href.split('?')[0]

            if not house_url.startswith('http://bj.58.com/zufang/'):
                continue

            # 把发布时间sortid的信息提取进housePublishedTime
            query_1 = 'ancestor::*/ancestor::*/attribute::sortid'
            housePublishedTime = info.xpath(query_1).extract()[0]

            yield scrapy.Request(house_url, callback=self.parse_house_page, meta={'time': housePublishedTime},
                                 dont_filter=True)

    def parse_house_page(self, response):
        item = RentItem()

        item['updated_date'] = time.strftime("%Y-%m-%d", time.localtime(int(response.request.meta['time'])/1000))
        item['url'] = response.request.url
        item['title'] = response.xpath('//head/title/text()').extract()[0].strip()
        # 这里匹配城市信息
        city_query_1 = response.xpath('//head/meta[@name="location"]/attribute::content').extract()
        if city_query_1:
            item['city'] = city_query_1[0].split(';')[1].split('=')[1]
        else:
            city_query_2 = response.xpath('/html/head/script[1]/text()').re(r'"locallist"\:\[.*?\]')[0]
            city_query_2_json = demjson.decode('{' + city_query_2 + '}')
            item['city'] = city_query_2_json['locallist'][0]['name']

        # room category
        try:
            room_detail = response.xpath('/html/body/div[4]/div[2]/div[2]/div[1]/div[1]/ul/li[2]/span[2]/text()').extract()[0]
            room_detail = re.findall(r'\d+', re.search(r'\d室\d厅', room_detail).group(0))
            item['bedroom_count'] = room_detail[0]
            item['livingroom_count'] = room_detail[1]
        except:
            item['bedroom_count'] = str(-1)
            item['livingroom_count'] = str(-1)

        # info_1匹配name,lon,lat,baidulon,baidulat
        info_1 = response.xpath('/html/head/script[1]/text()').re(r'"xiaoqu"\:\{.*?\}')[0]
        info_1_josn = demjson.decode('{' + info_1 + '}')['xiaoqu']
        item['house_name'] = info_1_josn['name']
        item['latitude'] = info_1_josn['baidulat']
        item['longitude'] = info_1_josn['baidulon']

        # info_2匹配面积
        info_2 = response.xpath('//html').re(r'\{\"I\"\:1025.*?\}')[0]
        info_2_josn = demjson.decode(info_2)
        info_2_area = info_2_josn['V']
        item['house_area'] = info_2_area

        # info_3匹配价格
        info_3 = response.xpath('//html/head').re(r'\{\"I\"\:1016.*?\}')[0]
        info_3_josn = demjson.decode(info_3)
        info_3_price = info_3_josn['V']
        item['price'] = info_3_price

        # info_4匹配地址
        info_4 = response.xpath('//body/div/div/div/ul[@class="house-primary-content"]/li/div/a/text()').extract()
        temp_addr = ''
        for address in info_4:
            temp_addr = temp_addr + '-' + address
        item['address'] = temp_addr
        item['district'] = ''
        item['source'] = '58'

        yield item
