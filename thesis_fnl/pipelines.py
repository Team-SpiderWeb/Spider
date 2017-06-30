# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from __future__ import print_function
import mysql.connector
from mysql.connector import errorcode

class ThesisFnlPipeline(object):
	link_string = ""
	last_linkid = 0

	page_table = 'page'
	link_table = 'link'
	conf = {
		'host': 'localhost',
		'user': 'root',
		'password': 'belle',
		'database': 'thsst',
		'raise_on_warnings': True,
	}

	def __init__(self, **kwargs):
		self.cnx = self.mysql_connect()

	def open_spider(self, spider):
		print("spider open")

	def process_item(self, item, spider):
		print("Saving item into db ...")
		
		item['link'] = u','.join(item['link'])
		self.link_string = item['link'].split(",")

		self.save(dict(item))

		return item

	def close_spider(self, spider):
		self.mysql_close()
    
	def mysql_connect(self):
		try:
			return mysql.connector.connect(**self.conf)
		except mysql.connector.Error as err:
			if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
				print("Something is wrong with your user name or password")
			elif err.errno == errorcode.ER_BAD_DB_ERROR:
				print("Database does not exist")
			else:
				print(err)
    
    
	def save(self, row): 
		cursor = self.cnx.cursor()
		page_query = ("INSERT INTO " + self.page_table + 
			"(url, author, date, title, content) "
			"VALUES (%(url)s, %(author)s, %(date)s, %(title)s, %(content)s)")

		# Insert new page row
		cursor.execute(page_query, row)
		lastRecordId = cursor.lastrowid
		self.last_linkid = format(lastRecordId)
		
		self.cnx.commit()
		cursor.close()

		# Insert new links row
		for link_insert in self.link_string:
			cursor = self.cnx.cursor()
			cursor.execute("INSERT INTO " + self.link_table + 
				"(idpage, link) "
				"VALUES (%s, %s)", (self.last_linkid, link_insert))
			self.cnx.commit()
			cursor.close()

	def mysql_close(self):
		self.cnx.close()

