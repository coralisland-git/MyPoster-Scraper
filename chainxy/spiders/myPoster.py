# from __future__ import unicode_literals
import scrapy

import json

import os

import scrapy

from scrapy.spiders import Spider

from scrapy.http import FormRequest

from scrapy.http import Request

from chainxy.items import ChainItem

from scrapy import signals

from scrapy.xlib.pydispatch import dispatcher

from lxml import etree

from lxml import html

import pdb


class myPoster(scrapy.Spider):

	name = 'myPoster'

	domain = ''

	history = []

	total_count = 0

	def __init__(self):

		pass

	
	def start_requests(self):

		url = 'https://www.mein-plakat.de/suche#suchId=912uoo9405m'

		yield scrapy.Request(url=url, callback=self.parse, dont_filter=True) 


	def parse(self, response):

		self.check = raw_input(" Checking Duplicated (Y/N) : ")

		in_city = raw_input(" City : ")

		url = "https://www.mein-plakat.de/packages/meinplakat_design/themes/meinplakat/ajax/index.php?methodName=getCities&q="+self.validate(in_city)

		yield scrapy.Request(url, callback=self.parse_address)


	def parse_address(self, response):

		try:

			city_code = json.loads(response.body)[0]['value']

			url = "https://www.mein-plakat.de/packages/meinplakat_design/themes/meinplakat/ajax/index.php?methodName=getResults"

			formdata = {
				"cities[]": city_code,
				"startDate": "0",
				"endDate": "0",
				"qualityRanking": "0",
				"tkpFrom": "0",
				"tkpTo": "100",
				"nightEffect": "0",
				"searchTerm": "",
				"currentPage": "1",
				"bounds": "false",
				"mapView": "false",
			}

			yield scrapy.FormRequest(url, callback=self.parse_list, formdata=formdata, meta={ 'city_code' : city_code }, dont_filter=True)

		except Exception as e:

			pass


	def parse_list(self, response):

		data = json.loads(response.body)

		current_page = data['currentPage']

		total_page = data['totalPages']

		post_list = data['items']

		for post in post_list:

			if self.check.lower() == 'y':

				if post['streetName'] not in self.history: 

					self.history.append(post['streetName'])

					yield scrapy.Request(post['url'], callback=self.parse_detail, meta={'name':post['streetName']})
			else :

				yield scrapy.Request(post['url'], callback=self.parse_detail, meta={'name':post['streetName']})


		if current_page != total_page:

			next_page = int(current_page) + 1

			formdata = {
				"cities[]": response.meta['city_code'],
				"startDate": "0",
				"endDate": "0",
				"qualityRanking": "0",
				"tkpFrom": "0",
				"tkpTo": "100",
				"nightEffect": "0",
				"searchTerm": "",
				"currentPage": str(next_page),
				"bounds": "false",
				"mapView": "false",
			}

			yield scrapy.FormRequest(response.url, callback=self.parse_list, formdata=formdata, meta={ 'city_code' : response.meta['city_code'] }, dont_filter=True)


	def parse_detail(self, response):

		url = response.xpath('//div[@class="details-picture"]//img/@src').extract_first()

		yield scrapy.Request(url, callback=self.parse_img, meta={ 'name' : response.meta['name']})


	def parse_img(self, response):

		name = 'images/' + self.validate(response.meta['name']).replace('/', '-').replace(' ', '_').replace('.', '') + '.jpg'

		with open(name, 'wb') as f:

			f.write(response.body)
		

	def validate(self, item):

		try:

			return item.replace('\n', '').replace('\t','').replace('\r', '').encode('ascii','ignore').strip()

		except:

			pass


	def eliminate_space(self, items):

	    tmp = []

	    for item in items:

	        if self.validate(item) != '':

	            tmp.append(self.validate(item))

	    return tmp