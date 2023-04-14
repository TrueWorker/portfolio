# -*- coding: utf-8 -*-
import requests
import json
import sys
import re

from lxml import html, etree
from time import sleep, time

requests.urllib3.disable_warnings()
session = requests.Session()
session.cookies.set('LANG', 'ru')


def req(url, data=None, method='GET', decode='utf-8', headers=None, params=None):
	if not headers:
		headers = {
			'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 YaBrowser/20.9.3.189 (beta) Yowser/2.5 Safari/537.36'}
	tries = 0
	while tries < 10:
		try:
			if method.lower() == 'get':
				resp = session.get(url, headers=headers, timeout=60, data=data, params=params, verify=False)
			else:
				resp = session.post(url, headers=headers, timeout=60, data=data, params=params, verify=False)
			if resp.status_code > 400:
				raise Exception(u'{}: {}\n{}'.format(resp.status_code, url, resp.text))
			resp.encoding = decode
			return resp
		except Exception as e:
			sys.stderr.write('try {}\n'.format(tries))
			sys.stderr.write(u'{}\n'.format(e))
			tries += 1
			sleep(5)
	raise Exception('Ошибка соединения')



##Чистим адреса
def clear_data(inf):
	if inf:
		inf = re.sub(r'</?br>', ' ', inf)
		inf = re.sub(r'</?[pb]>', ' ', inf)
		inf = re.sub(r'</?nobr>', ' ', inf)
		inf = re.sub(r'\d{6},?', '', inf)
		inf = re.sub(r'["«»]', '', inf)
		inf = re.sub(r'&nbsp;', ' ', inf)
		inf = re.sub(r'(?:, ?)+', ', ', inf)
		inf = inf.replace('–', '-')
		inf = re.sub(r'\s+', ' ', inf)
		inf = re.sub(r'\\n','', inf)
	return inf.strip()



##Берём адреса

def parse(url):
	rubrics = ['184107799', '184107395']
	main_name = u'Alma+'
	city_urls = []
	url_point = 'https://www.almatv.kz/ajax/office.php'
	response = req(url)


	tree = html.fromstring(response.content)
	for city in tree.xpath('//fieldset/ul//a/@href'):
		city_urls.append(city)


	for cu in city_urls:
		#headers = {}
		url_city = 'https://www.almatv.kz/support/offices/{}'.format(cu)
		response = req(url_city)
		tree = html.fromstring(response.content)


		for point in tree.xpath(u'//ul[@class="side_nav"]/li/@data-id'):
			data = {'id': point}
			response = req(url_point, data, 'POST')
			tree = html.fromstring(response.text)

			address = tree.xpath(u'//div[@class="contact_info"]/span[@class="contact_info__office_desc"]//text()')[0]
			phone = tree.xpath(u'//div[@class="contact_info__col"]/span/a/text()')[0]

			coord = re.findall(r"center: \[(\d.+)],", response.text)[0].split(',')
			lat = coord[0]
			lon = coord[1]

			working_hours = []
			first_hours = tree.xpath(u'//li[@class="opening_times__item"]/span[@class="opening_times__desc"]/text()')[0]
			st_hours = tree.xpath(u'//li[@class="opening_times__item opening_times__item--half"]/span[@class="opening_times__desc"]/text()')[0]
			sn_hours = tree.xpath(u'//li[@class="opening_times__item opening_times__item--weekend"]/span[@class="opening_times__desc"]/text()')[0]
			wt_wd = u'Пн-Пт: {}'.format(first_hours)
			wt_st = u'Cб: {}'.format(st_hours)
			wt_sn = u'ВС: {}'.format(sn_hours)
			wt = u'{}, {}, {}'.format(wt_wd,wt_st,wt_sn)
			
			item = {
				'name': [{'lang': 'ru', 'value': main_name, 'type': 'MAIN'}],
				'address': [{'one_line':address, 'lang': 'ru'}],
				'lat': lat,
				'lon': lon,
				'url': [{"type": "MAIN", "value":'https://www.almatv.kz/'}],
				'actualization_date': int(time()),
				'working_time': {'lang': 'ru', 'value': wt},
				'phone': [{'value': phone, 'type': 'phone'}],
				'rubric_id': [{'value': _.strip()} for _ in rubrics]
			}
			print(json.dumps(item, ensure_ascii=False))
	'''
	points = re.findall(r'BX_GMapAddPlacemark\(markers, bounds, ({.+})', response)
	#print(points)
	for d in points:
		point_dict = d.replace('\'', '"')

		# получаем адрес
		lon = re.findall(r"\"LON\":\"([\d\.]+)\"",point_dict)[0]
		lat = re.findall(r"\"LAT\":\"([\d\.]+)\"",point_dict)[0]

		address = re.findall(r"\<div class=\\\"adress\\\">(.*?)<\\/div>",point_dict)[0]
		address = clear_data(address)

		wt = re.findall(r"<div class=\\\"wrap_worktime\\\">(.*?)<\\/div>",point_dict)[0]
		wt = clear_data(wt)


		item = {
			'name': [{'lang': 'ru', 'value': u'Классика', 'type': 'MAIN'}],
			'address': [{'one_line':address, 'lang': 'ru'}],
			'lat': lat,
			'lon': lon,
			'url': [{"type": "MAIN", "value":'https://klassika-apteka.ru/'}],
			'actualization_date': int(time()),
			'working_time': {'lang': 'ru', 'value': wt},
			'phone': [{'value': phone, 'type': 'phone'}],
			'rubric_id': [{'value': '184105932'}]
		}
		print(json.dumps(item, ensure_ascii=False))
	'''
if __name__ == '__main__':
	url_req = 'https://www.almatv.kz/support/offices'
	parse(url_req)
