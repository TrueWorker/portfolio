# -*- coding: utf-8 -*-
import requests
import json
import sys
import re

from lxml import html, etree
from time import sleep, time

requests.urllib3.disable_warnings()
session = requests.Session()


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

##Проверяем время
def time_check(tree):
	time = []
	for times in tree.xpath('//div[@class="services small worktime"]//div[@class="price text18 td"]/span/text()'):
		time.append(times)
		unique_times = set(time)
		if len(unique_times) == 1:
			uniq = list(unique_times)
			wt = ("Ежедневно: {}".format(uniq[0]))
		else:
			wt = []
			days = tree.xpath('//div[@class="services small worktime"]/div[@class="line"]')
			for day in days:
				name = day.xpath('./div[@class="name text18 td"]/span/text()')[0]
				time = day.xpath('./div[@class="price text18 td"]/span/text()')[0]
				wt.append(u'{}: {}'.format(name, time))
		return(wt)

##Берём адреса

def parse(url):
	rubrics = ['184105812']
	main_name = u'Чио Чио'
	city_data = []
	response = req(url)


	list_cities = open('cities.txt', mode='r', encoding='utf-8').readlines()
	list_cities = [_.strip().lower() for _ in list_cities if _.strip()]

	#list_first_3b = list(set([x.decode('utf-8').strip()[:3].lower() for x in list_cities]))

	tree = html.fromstring(response.content)
	for city in tree.xpath('//div[@class="cities"]/a'):
		city_name = city.xpath('./text()')[0]
		city_url = city.xpath('./@href')[0]
		city_data.append({'city_n': city_name, 'url': city_url})


	for cu in city_data:
		if cu['city_n'].lower() not in list_cities:
			continue
		cu['url'] = re.sub('(\?city)', '/uslugi', cu['url'])
		response = req(cu['url'])
		tree = html.fromstring(response.text)


		for url_point in tree.xpath(u'//div[@class="leftMenu"]/a/@href'):
			point = re.sub('/uslugi', url_point, cu['url'])
			response = req(point)
			tree = html.fromstring(response.text)

			address = tree.xpath(u'//div[contains(@class, "spotName")]/text()')[0]
			address = u'г.{}, {}'.format(cu['city_n'], address)

			wt = time_check(tree)

			coord = re.findall(r"center: \[(\d.+)],", response.text)[0].split(', ')
			lat = coord[0]
			lon = coord[1]


			
			item = {
				'name': [{'lang': 'ru', 'value': main_name, 'type': 'MAIN'}],
				'address': [{'one_line':address, 'lang': 'ru'}],
				'lat': lat,
				'lon': lon,
				'url': [{"type": "MAIN", "value":'https://chio-chio.ru/'}],
				'actualization_date': int(time()),
				'working_time': {'lang': 'ru', 'value': wt},
				'phone': [{'value': '8 800 600 65 16', 'type': 'phone'}],
				'rubric_id': [{'value': _.strip()} for _ in rubrics]
			}
			print(json.dumps(item, ensure_ascii=False))


if __name__ == '__main__':
	url_req = 'https://chio-chio.ru/'
	parse(url_req)
