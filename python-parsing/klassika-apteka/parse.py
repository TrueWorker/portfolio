# coding=utf-8
import requests
import json
import sys
import re

from bs4 import BeautifulSoup
from lxml import html, etree
from time import sleep, time

requests.urllib3.disable_warnings()
session = requests.Session()



def req(url, data, decode='utf-8', method='POST', headers=None, params=None):
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

def parse(url, reg, phone):
	data = {'region': reg, 'city': 'all'}
	response = req(url, data).text
	#soup = BeautifulSoup(response, "lxml")
	#print(soup)
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

if __name__ == '__main__':
	url_req = 'https://klassika-apteka.ru/ajax/filter_apteka.php'
	region = ["8374", "8375"]
	for reg in region:
		if reg == "8374":
			phone = '+7 (343) 287-77-77'
		else:
			phone = '+7 (351) 232-33-13'
		parse(url_req, reg, phone)
