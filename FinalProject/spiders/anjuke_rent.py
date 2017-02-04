# -*- coding: utf-8 -*-
import re

import scrapy

from FinalProject.items import RentItem


class AnjukeRentSpider(scrapy.Spider):
    name = "anjuke_rent"
    allowed_domains = ["anjuke.com"]
    start_urls = ['http://bj.zu.anjuke.com/fangyuan/']

    def start_requests(self):
        requests = []
        for index in range(1, 201):
            request = scrapy.Request(self.start_urls[0] + "p%s-x1/" % index)
            requests.append(request)
        return requests

    def parse(self, response):
        for info in response.xpath('//*[@id="list-content"]/div'):
            try:
                page_url_query = 'div[1]/h3/a/attribute::href'
                house_page_url = info.xpath(page_url_query).extract()[0]
                yield scrapy.Request(house_page_url, callback=self.parse_house_page)
            except:
                continue

    def parse_house_page(self, response):
        item = RentItem()
        item['url'] = response.request.url
        item['title'] = response.xpath('//html/head/title/text()').extract()[0]
        item['city'] = response.xpath('//body/div/div/div/div/div/div/span[@class="city"]/text()').extract()[0]

        # 匹配房屋地址
        item['address'] = ''
        item['district'] = ''

        # 价格
        item['price'] = response.xpath('//*[@id="content"]/div[2]/div[2]/div[1]/div[2]/div[2]/div[1]/div[1]/dl[1]/dd/strong/span/text()').extract()[0]

        area_detail = response.xpath('//*[@id="content"]/div[2]/div[2]/div[1]/div[2]/div[2]/div[1]/div[2]/dl[3]/dd/text()').extract()[0]
        item['house_area'] = re.findall(r'\d+', re.search(r'\d+', area_detail).group(0))[0]

        # 匹配房屋小区名称
        item['house_name'] = response.xpath('//*[@id="content"]/div[2]/div[2]/div[1]/div[2]/div[2]/div[1]/div[1]/dl[5]/dd/a/text()').extract()[0]

        # 这里看开始通过正则表达匹配经纬度
        lat = response.xpath('/html').re(r'l1=.*?&')
        lng = response.xpath('/html').re(r'l2=.*?&')
        if lat:
            item['latitude'] = lat[0].split('=')[-1][:-1]
            item['longitude'] = lng[0].split('=')[-1][:-1]
        else:
            item['latitude'] = ''
            item['longitude'] = ''

        # 房屋配置
        room_detail = response.xpath('//*[@id="content"]/div[2]/div[2]/div[1]/div[2]/div[2]/div[1]/div[1]/dl[3]/dd/text()').extract()[0].strip()
        try:
            item['bedroom_count'] = re.findall(r'\d+', re.search(r'\d室', room_detail).group(0))[0]
        except:
            item['bedroom_count'] = str(-1)
        try:
            item['livingroom_count'] = re.findall(r'\d+', re.search(r'\d厅', room_detail).group(0))[0]
        except:
            item['livingroom_count'] = str(-1)

        # 发布日期
        update_detail = response.xpath('//*[@id="content"]/div[2]/div[2]/div[1]/div[2]/div[2]/div[2]/div[4]/text()').extract()[0]
        try:
            year = re.findall(r'\d+', re.search(r'\d+年', update_detail).group(0))[0]
            month = re.findall(r'\d+', re.search(r'\d+月', update_detail).group(0))[0]
            day = re.findall(r'\d+', re.search(r'\d+日', update_detail).group(0))[0]
            item['updated_date'] = year + '-' + month + '-' + day
        except:
            item['updated_date'] = ''

        item['source'] = 'anjuke'
        yield item
