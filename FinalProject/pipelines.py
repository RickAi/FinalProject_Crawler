# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import csv
import MySQLdb


class MysqlPipeline(object):
    def process_item(self, item, spider):
        DBKWARGS = spider.settings.get('DBKWARGS')
        con = MySQLdb.connect(**DBKWARGS)
        cur = con.cursor()
        sql = (
            "insert into HouseRent(url,title,bedroom_count,livingroom_count,house_area,house_name,updated_date,address,district,city,latitude,longitude,price,source) "
            "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
        lis = (item['url'], item['title'], item['bedroom_count'], item['livingroom_count'], item['house_area'],
               item['house_name'], item['updated_date'], item['address'], item['district'], item['city'], item['latitude'], item['longitude'],
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


class CSVPipeline(object):
    def process_item(self, item, spider):
        # 打开写入的文件和CSV写入模块
        self.file = open('lianjia_rent.csv', 'a')
        csvWriter = csv.writer(self.file)

        line = (item['url'], item['title'], item['bedroom_count'], item['livingroom_count'], item['house_area'],
               item['house_name'], item['updated_date'], item['address'], item['district'], item['city'], item['latitude'], item['longitude'],
               item['price'], item['source'])
        csvWriter.writerow(line)

        return item
