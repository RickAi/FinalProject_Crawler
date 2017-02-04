# -*- coding: utf-8 -*-
import scrapy


class A5i5jSaleSpider(scrapy.Spider):
    name = "5i5j_sale"
    allowed_domains = ["5i5j.com"]
    start_urls = ['http://5i5j.com/']

    def parse(self, response):
        pass
