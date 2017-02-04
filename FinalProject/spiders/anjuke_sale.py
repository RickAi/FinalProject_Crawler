# -*- coding: utf-8 -*-
import re
import scrapy

from FinalProject.items import SaleItem


class AnjukeSaleSpider(scrapy.Spider):
    name = "anjuke_sale"
    allowed_domains = ["anjuke.com"]
    start_urls = ['http://beijing.anjuke.com/sale/']

    def start_requests(self):
        requests = []
        for index in range(1, 201):
            request = scrapy.Request(self.start_urls[0] + "p%s/" % index)
            requests.append(request)
        return requests

    def parse(self, response):
        for info in response.xpath('//*[@id="houselist-mod"]/li'):
            page_url_query = 'div/div[@class="house-title"]/a/attribute::href'
            house_page_url = info.xpath(page_url_query).extract()[0]
            house_page_url = house_page_url.split('?')[0]
            yield scrapy.Request(house_page_url, callback=self.parse_house_page)

    def parse_house_page(self, response):
        item = SaleItem()
        item['url'] = response.request.url
        item['title'] = response.xpath('//html/head/title/text()').extract()[0]
        item['city'] = response.xpath('//body/div/div/div/div/div/div/span[@class="city"]/text()').extract()[0]

        # 匹配房屋地址
        item['address'] = response.xpath('//*[@id="content"]/div[2]/div[1]/div[3]/div/div/div[1]/div[1]/dl[2]/dd/p/text()[2]').extract()[0].replace('－', '').strip()
        item['district'] = ''

        # 价格
        per_price_detail = \
        response.xpath('//*[@id="content"]/div[2]/div[1]/div[3]/div/div/div[1]/div[3]/dl[2]/dd/text()').extract()[0]
        item['per_price'] = re.findall(r'\d+', re.search(r'\d+', per_price_detail).group(0))[0]
        total_price_detail = \
        response.xpath('//*[@id="content"]/div[2]/div[1]/div[3]/div/div/div[1]/div[3]/dl[3]/dd/text()').extract()[
            0].strip()
        item['total_price'] = re.findall(r'\d+', re.search(r'\d+', total_price_detail).group(0))[0]

        area_detail = \
        response.xpath('//*[@id="content"]/div[2]/div[1]/div[3]/div/div/div[1]/div[2]/dl[2]/dd').extract()[0]
        item['house_area'] = re.findall(r'\d+', re.search(r'\d+', area_detail).group(0))[0]

        # 匹配房屋小区名称
        title_detail = response.xpath('//*[@id="content"]/div[2]/h3/text()').extract()[0].strip()
        item['house_name'] = title_detail.split(' ')[0]

        # 这里看开始通过正则表达匹配经纬度
        lat = response.xpath('/html').re(r'lat=.*?&')
        lng = response.xpath('/html').re(r'lng=.*?&')
        if lat:
            item['latitude'] = lat[0].split('=')[-1][:-1]
            item['longitude'] = lng[0].split('=')[-1][:-1]
        else:
            item['latitude'] = ''
            item['longitude'] = ''

        # 房屋配置
        room_detail = response.xpath('//*[@id="content"]/div[2]/div[1]/div[3]/div/div/div[1]/div[2]/dl[1]/dd/text()').extract()[0].strip()
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

        # 发布日期
        update_detail = response.xpath('//*[@id="content"]/div[2]/div[1]/div[3]/h4/span/text()').extract()[0]
        try:
            year = re.findall(r'\d+', re.search(r'\d+年', update_detail).group(0))[0]
            month = re.findall(r'\d+', re.search(r'\d+月', update_detail).group(0))[0]
            day = re.findall(r'\d+', re.search(r'\d+日', update_detail).group(0))[0]
            item['updated_date'] = year + '-' + month + '-' + day
        except:
            item['updated_date'] = ''

        item['source'] = 'anjuke'
        yield item