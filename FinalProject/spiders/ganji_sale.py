# -*- coding: utf-8 -*-
import datetime
import re

import demjson
import scrapy

from FinalProject.items import SaleItem


class GanjiSaleSpider(scrapy.Spider):
    name = "ganji_sale"
    allowed_domains = ["ganji.com"]
    start_urls = ['http://bj.ganji.com/fang5/']

    def start_requests(self):
        requests = []
        for index in range(1, 201):
            request = scrapy.Request(self.start_urls[0] + "o%s/" % index)
            requests.append(request)
        return requests

    def parse(self, response):
        house_page_query = '//body/div/div/div/ul/li/div/div/a[@class="list-info-title js-title"]'
        house_page_root = response.request.url.split('/')[2]
        for info in response.xpath(house_page_query):
            house_page_href = info.xpath('attribute::href').extract()[0]
            house_page_url = 'http://'+ house_page_root + house_page_href
            house_page_log = info.xpath('attribute::gjalog_fang').extract()[0]
            temp_time = house_page_log.split('@')[2]

            try:
                housePublishedTime = float(temp_time.split('=')[1])
            except:
                housePublishedTime = 0

            house_page_url = house_page_url.split('?')[0]
            yield scrapy.Request(house_page_url,callback=self.parse_house_page,meta={"time":housePublishedTime})

    def parse_house_page(self,response):
        item = SaleItem()

        item['url'] = response.request.url
        item['updated_date'] = datetime.datetime.fromtimestamp(response.request.meta['time']).strftime('%Y-%m-%d')
        item['title'] = response.xpath('//html/head/title/text()').extract()[0]

        try:
            item['city'] = response.xpath('//head/meta[@name="location"]/attribute::content').extract()[0].split(';')[1].split('=')[1]
        except:
            item['city'] = '北京'

        # 价格信息
        house_info_query = '//body/div/div/div/div/div/div/ul[@class="basic-info-ul"]'
        price_query = 'li/b[@class="basic-info-price"]/text()'
        item['total_price'] = response.xpath(house_info_query).xpath(price_query).extract()[0]

        per_price_detail = response.xpath('//*[@id="wrapper"]/div[2]/div[1]/div[2]/div/div/ul').extract()[0]
        try:
            item['per_price'] = re.findall(r'\d+', re.search(r'\d+元/㎡', per_price_detail).group(0))[0]
        except:
            item['per_price'] = ''

        # 房屋配置信息
        room_detail = response.xpath('//*[@id="wrapper"]/div[2]/div[1]/div[2]/div/div/ul').extract()[0]
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

        #此处匹配房屋面积
        house_area_query = response.xpath('/html').re(r'area=.*?@')
        if house_area_query:
            item['house_area'] = response.xpath('/html').re(r'area=.*?@')[0].split('=')[-1][:-1]
        else:
            item['house_area'] = -1

        item['house_name'] = ''
        #此处匹配房屋地址
        #有些页面有地址，有些页面只有小区。
        #所以首先以地址为第一匹配，如果没有匹配成功则换为小区区域。
        item['district'] = ''
        address_query = 'li[8]/span[@title]/text()'
        if response.xpath(house_info_query).xpath(address_query).extract():
            item['address'] = response.xpath(house_info_query).xpath(address_query).extract()[0]
        else:
            district_query = 'li[7]/a/text()'
            temp_district = response.xpath(house_info_query).xpath(district_query).extract()
            houseDistrict = ''
            #注意此处可能也匹配不到小区区域
            if temp_district:
                for dist in temp_district:
                    houseDistrict = houseDistrict + '-' + dist
                item['address'] = houseDistrict.lstrip('-')
            else:
                item['address'] = ''

        #此XPath节点匹配经纬度信息
        position_query = '//body/div/div/div/div/div/div[@id="map_load"]'
        house_position = response.xpath(position_query)
        house_position_1 = house_position.xpath('attribute::data-ref').extract()
        if house_position_1:
            house_position_json = demjson.decode(house_position_1[0])
            house_position_split = house_position_json['lnglat'].split(',')

            item['longitude'] = house_position_split[0][1:-1]
            item['latitude'] = house_position_split[1]
        else:
            return

        item['source'] = 'ganji'

        yield item