# coding=utf-8
import requests
import json
import re
from lxml import html, etree
from time import sleep, time


requests.urllib3.disable_warnings()
session = requests.Session()



##Чистим адреса
def clear_data(inf):
	if inf:
		inf = re.sub(r'</?br>', ' ', inf)
		inf = re.sub(r'</?[pb]>', ' ', inf)
		inf = re.sub(r'</?nobr>', ' ', inf)
		inf = re.sub(r'\d{5},?', '', inf)
		inf = re.sub(r'["«»]', '', inf)
		inf = re.sub(r'&nbsp;', ' ', inf)
		inf = re.sub(r'(?:, ?)+', ', ', inf)
		inf = inf.replace('–', '-')
		inf = re.sub(r'\s+', ' ', inf)
		inf = re.sub(r'Zажигалка','', inf)
	return inf.strip()



##Функция где есть доступ к контенту
def req(url):
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
		'Accept-Language': 'ru,en-US;q=0.7,en;q=0.3',
		'Accept-Encoding': 'gzip, deflate, br',
		'Referer': 'https://russtriptease.com/',
		'Connection': 'keep-alive',
		'Cookie': 'c2d_widget_id={%2201980bc31a9aba625de2291802f12756%22:%22[chat]%20f5a8c9ab82cace8c9264%22}; PHPSESSID=UNPEkMl06wf6kJi3eHk4bPhFflH3fFyA; _ga_REDTYNER1M=GS1.1.1679923159.4.1.1679928977.0.0.0; _ga=GA1.1.1736718789.1679927851; _gid=GA1.2.1147385698.1679927851; _ym_uid=167992785158665493; _ym_d=1679927851; BX_USER_ID=6ca4645ac804b286f531e03e12cf2e59; _ym_visorc=w; _ym_isad=2; isShown=true'
	}

	response = requests.get(url, headers=headers)
	tree = html.fromstring(response.content)
	return tree

rubrics = ['184106368', '184106384']

##Берем список городов и удаляем дубли
cities = []

url = 'https://russtriptease.com'

response = requests.get(url)
tree = html.fromstring(response.content)

for city in tree.xpath('//header[1]//div[@class="b-location__item"]/a/@data-set-city'):
	cities.append(city)

cities = list(set(cities))



##Обходим все города и забераем адреса
for href in cities:
	url_city = 'https://russtriptease.com/{}/zazhigalka/contacts/'.format(href)

	tree = req(url_city)

	address = tree.xpath(
		'//div[@class="b-contacts-block__item"][2]//div[@class="b-contacts-block__text"]/text()')[0]
	address = clear_data(address)

	city = tree.xpath('//span[@class="b-location__info"]/span[contains(@class,"name")]/text()')[0]
	city = clear_data(city)
	if city not in address:
		address = u'{}, {}'.format(city, address)

	wt = tree.xpath(
		'//div[@class="b-contacts-block__item"][1]//div[@class="b-contacts-block__text"]/text()')[0]

	country = u'Россия'

	lat = tree.xpath('//div[@id="map"]/@data-ln')[0]
	lon = tree.xpath('//div[@id="map"]/@data-lg')[0]

	phone = tree.xpath(
		'//div[@class="b-contacts-links__item"][1]/a/text()')[0]
##Пишем в json
	item = {
		'name': [{'lang': 'ru', 'value': u'Zажигалка', 'type': 'MAIN'}],
		'address': [{'one_line':u'{}, {}'.format(country,address), 'lang': 'ru'}],
		'lat': lat,
		'lon': lon,
		"url": [{"type": "MAIN", "value": url}],
		'actualization_date': int(time()),
		'working_time': {'lang': 'ru', 'value': wt},
		'phone': {'value': phone, 'type': 'phone'},
		'rubric_id': [{'value': _.strip()} for _ in rubrics]
	}
	print(json.dumps(item, ensure_ascii=False))
