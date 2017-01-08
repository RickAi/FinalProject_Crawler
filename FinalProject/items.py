# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class SaleItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    bedroom_count = scrapy.Field()
    livingroom_count = scrapy.Field()
    wc_count = scrapy.Field()
    kitchen_count = scrapy.Field()
    house_area = scrapy.Field()
    house_name = scrapy.Field()
    updated_date = scrapy.Field()
    address = scrapy.Field()
    district = scrapy.Field()
    city = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    per_price = scrapy.Field()
    total_price = scrapy.Field()
    source = scrapy.Field()

class RentItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    bedroom_count = scrapy.Field()
    livingroom_count = scrapy.Field()
    house_area = scrapy.Field()
    house_name = scrapy.Field()
    updated_date = scrapy.Field()
    address = scrapy.Field()
    district = scrapy.Field()
    city = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    price = scrapy.Field()
    source = scrapy.Field()
