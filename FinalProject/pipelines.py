# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import csv
import MySQLdb

from FinalProject.items import RentItem, SaleItem

class MysqlPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, RentItem):
            return self.process_rent_item(item, spider)
        elif isinstance(item, SaleItem):
            return self.process_sale_item(item, spider)

    def process_rent_item(self, item, spider):
        if item['price'] == 0 or item['latitude'] is None or item['longitude'] is None:
            return item

        DBKWARGS = spider.settings.get('DBKWARGS')
        DB_TABLE = spider.settings.get('DB_TABLE')
        con = MySQLdb.connect(**DBKWARGS)
        cur = con.cursor()
        sql = (
            "insert into " + DB_TABLE + "(url,title,bedroom_count,livingroom_count,house_area,house_name,updated_date,address,district,city,latitude,longitude,price,source) "
            "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
        lis = (item['url'], item['title'], item['bedroom_count'], item['livingroom_count'], item['house_area'],
               item['house_name'], item['updated_date'], item['address'], item['district'], item['city'],
               item['latitude'], item['longitude'],
               item['price'], item['source'])
        try:
            cur.execute(sql, lis)
        except Exception as e:
            print("insert error:" + str(e))
            con.rollback()
        else:
            con.commit()
        cur.close()
        con.close()

        return item

    def process_sale_item(self, item, spider):
        if item['per_price'] == 0 or item['total_price'] == 0 or item['latitude'] is None or item['longitude'] is None:
            return item

        DBKWARGS = spider.settings.get('DBKWARGS')
        DB_TABLE = spider.settings.get('DB_TABLE')
        con = MySQLdb.connect(**DBKWARGS)
        cur = con.cursor()
        sql = (
            "insert into " + DB_TABLE + "(url,title,bedroom_count,livingroom_count,wc_count,kitchen_count,house_area,house_name,updated_date,address,district,city,latitude,longitude,per_price,total_price,source) "
            "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
        lis = (item['url'], item['title'], item['bedroom_count'], item['livingroom_count'], item['wc_count'], item['kitchen_count'], item['house_area'],
               item['house_name'], item['updated_date'], item['address'], item['district'], item['city'],
               item['latitude'], item['longitude'],
               item['per_price'], item['total_price'], item['source'])
        try:
            cur.execute(sql, lis)
        except Exception as e:
            print("insert error:" + str(e))
            con.rollback()
        else:
            con.commit()
        cur.close()
        con.close()

        return item

class CSVPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, RentItem):
            return self.process_rent_item(item, spider)
        elif isinstance(item, SaleItem):
            return self.process_sale_item(item, spider)

    def process_rent_item(self, item, spider):
        # 打开写入的文件和CSV写入模块
        self.file = open('data.csv', 'a')
        csvWriter = csv.writer(self.file)

        line = (item['url'], item['title'], item['bedroom_count'], item['livingroom_count'], item['house_area'],
                item['house_name'], item['updated_date'], item['address'], item['district'], item['city'],
                item['latitude'], item['longitude'],
                item['price'], item['source'])
        csvWriter.writerow(line)
        self.file.close()

        return item

    def process_sale_item(self, item, spider):
         # 打开写入的文件和CSV写入模块
        self.file = open('data.csv', 'a')
        csvWriter = csv.writer(self.file)

        line = (item['url'], item['title'], item['bedroom_count'], item['livingroom_count'],
                item['kitchen_count'], item['wc_count'], item['house_area'],
                item['house_name'], item['updated_date'], item['address'], item['district'], item['city'],
                item['latitude'], item['longitude'], item['per_price'], item['total_price'], item['source'])
        csvWriter.writerow(line)
        self.file.close()

        return item
