# -*- coding: utf-8 -*-
import datetime
import re
import demjson
import scrapy

from FinalProject.items import RentItem


class GenjiRentSpider(scrapy.Spider):
    name = "ganji_rent"
    allowed_domains = ["ganji.com"]
    start_urls = ['http://bj.ganji.com/fang1/']

    def start_requests(self):
        requests = []
        for index in range(1, 201):
            request = scrapy.Request(self.start_urls[0] + "m1o%s/" % index)
            requests.append(request)
        return requests

    def parse(self, response):
        house_page_root = response.request.url.split('/')[2]
        for info in response.xpath('//*[@id="f_mew_list"]/div[7]/div[1]/div[2]/div[1]/div'):
            house_page_href = info.xpath('dl/dd[1]/a/attribute::href').extract()[0]
            house_page_url = 'http://' + house_page_root + house_page_href
            house_page_log = info.xpath('dl/dt/div/a/attribute::gjalog_fang').extract()[0]
            temp_time = house_page_log.split('@')[3]

            try:
                housePublishedTime = float(temp_time.split('=')[1])
            except:
                housePublishedTime = 0

            house_page_url = house_page_url.split('?')[0]
            yield scrapy.Request(house_page_url, callback=self.parse_house_page, meta={"time": housePublishedTime})

    def parse_house_page(self, response):
        item = RentItem()

        item['url'] = response.request.url
        item['updated_date'] = datetime.datetime.fromtimestamp(response.request.meta['time']).strftime('%Y-%m-%d')
        item['title'] = response.xpath('//html/head/title/text()').extract()[0]
        item['city'] = \
        response.xpath('//head/meta[@name="location"]/attribute::content').extract()[0].split(';')[1].split('=')[1]

        item['price'] = \
        response.xpath('//*[@id="f_detail"]/div[5]/div[2]/div[2]/div[1]/ul/li[1]/span[2]/text()').extract()[0]
        area_detail = response.xpath('//*[@id="f_detail"]/div[5]/div[2]/div[2]/div[1]/div[2]/span[2]/text()').extract()[
            0]
        try:
            item['house_area'] = re.findall(r'\d+', re.search(r'\d+㎡', area_detail).group(0))[0]
        except:
            item['house_area'] = '-1'

        # 房屋配置
        try:
            room_detail = response.xpath('//*[@id="f_detail"]/div[5]/div[2]/div[2]/div[1]/div[2]/span[1]/text()').extract()[0].strip()
        except:
            room_detail = response.xpath('//*[@id="wrapper"]/div[2]/div[1]/div[3]/div/div[2]/ul/li[3]/text()').extract()[0].strip()

        try:
            item['bedroom_count'] = re.findall(r'\d+', re.search(r'\d室', room_detail).group(0))[0]
        except:
            item['bedroom_count'] = str(-1)
        try:
            item['livingroom_count'] = re.findall(r'\d+', re.search(r'\d厅', room_detail).group(0))[0]
        except:
            item['livingroom_count'] = str(-1)

        item['house_name'] = ''
        item['address'] = ''
        item['district'] = ''

        # 此XPath节点匹配经纬度信息
        position_query = '//body/div/div/div/div/div/div[@id="map_load"]'
        house_position = response.xpath(position_query)
        house_position_1 = house_position.xpath('attribute::data-ref').extract()
        if house_position_1:
            house_position_json = demjson.decode(house_position_1[0])
            house_position_split = house_position_json['lnglat'].split(',')
            item['longitude'] = house_position_split[0][1:-1]
            item['latitude'] = house_position_split[1]
        else:
            item['longitude'] = ''
            item['latitude'] = ''
            return

        item['source'] = 'ganji'

        yield item
