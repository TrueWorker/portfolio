# -*- coding: utf-8 -*-
import requests
import json
import sys
import re
import phpserialize
from urllib.parse import quote


from lxml import html, etree
from time import sleep, time

requests.urllib3.disable_warnings()
session = requests.Session()


def req(url, ser_encoded, data=None, method='GET', decode='utf-8', headers=None, params=None, ser=None):
	loc = ser_encoded
	if not headers:

		headers = {
			'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 YaBrowser/20.9.3.189 (beta) Yowser/2.5 Safari/537.36',
			'Cookie': u'_fbp=fb.1.1680187393314.26853416; _ga=GA1.2.686361616.1680187389; _ga_9GF25Z7SC1=GS1.1.1680782707.8.1.1680784232.0.0.0; _ga_CJBDH6VKZ2=GS1.1.1680782707.8.1.1680784232.0.0.0; _ga_F5R3PNXHW0=GS1.1.1680782707.8.1.1680784232.0.0.0; _gid=GA1.2.1056641041.1680699480; _ym_d=1680187391; _ym_isad=2; _ym_uid=1680187391662766390; __buttonly_id=49722249; cart=%5B%5D; location={}; PHPSESSID=dlp4psvp9brpfarsast3ke63f4; _gat_UA-138163477-1=1'.format(loc)
		}
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
	rubrics = ['184105932']
	main_name = u'Садыхан'

	serialized_string = [
		u'a:2:{s:7:"city_id";i:3;s:4:"city";s:10:"Тараз";}',
		u'a:2:{s:7:"city_id";i:1;s:4:"city";s:12:"Алматы";}',
		u'a:2:{s:7:"city_id";i:4;s:4:"city";s:14:"Шымкент";}',
		u'a:2:{s:7:"city_id";i:13;s:4:"city";s:19:"Нур-Султан";}'
	]
	
	for ser in serialized_string:
		s = ser
		ser_encoded = quote(s, safe='')
		response = req(url,ser_encoded).text
		#tree = html.fromstring(response.text)
		data = re.findall("data-placemarks='(\[.*])'",response)
		if data:
			city = re.findall("<span class=\"value\">([а-яА-Я]+)</span>",response)[0]
			data = data[0]
			json_data = json.loads(data)

			for item in json_data:
				address = item['description'].split('<br>')[1]
				address = u'г.{}, {}'.format(city, address)

				coords = item['coord'].split(', ')
				lat = coords[0]
				lon = coords[1]

				wt = item['description'].split('<br>')[-1]



				item = {
					'name': [{'lang': 'ru', 'value': main_name, 'type': 'MAIN'}],
					'address': [{'one_line':address, 'lang': 'ru'}],
					'lat': lat,
					'lon': lon,
					'url': [{"type": "MAIN", "value":'https://sadykhan.kz'}],
					'actualization_date': int(time()),
					'working_time': {'lang': 'ru', 'value': wt},
					'phone': [{'value': '+7 727 349-49-49', 'type': 'phone'}],
					'rubric_id': [{'value': _.strip()} for _ in rubrics]
				}
				print(json.dumps(item, ensure_ascii=False))


if __name__ == '__main__':
	url_req = 'https://sadykhan.kz/kontakty/'
	parse(url_req)
