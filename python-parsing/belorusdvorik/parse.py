# coding=utf-8
import requests
import json
import re
from lxml import html, etree
from time import sleep, time

requests.urllib3.disable_warnings()
session = requests.Session()



def req(url, decode='utf-8', method='GET', headers=None, data=None, params=None):
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
		inf = re.sub(r'\d{5},?', '', inf)
		inf = re.sub(r'["«»]', '', inf)
		inf = re.sub(r'&nbsp;', ' ', inf)
		inf = re.sub(r'(?:, ?)+', ', ', inf)
		inf = inf.replace('–', '-')
		inf = re.sub(r'\s+', ' ', inf)
	return inf.strip()



##Забераем адреса

def parse(url):

	rubrics = ['184108031']
	main_name = u'Белорусский Дворик'
	phone = {'value': u"+7 (812) 516-58-48", 'type': "phone"}
	country = u'Россия'
	city = u'Санкт-Петербург'

	response = req(url)
	tree = html.fromstring(response.content)

	list = tree.xpath('//div[@class="item-page"]')[0]
	for part in list.xpath('./p'):
		for address in part.xpath('./span/br/following-sibling::text()'):
			address = re.sub(u'( \(.*\)?)', '',address)
			if city not in address:
				address = u'{}, {}'.format(city, address)

##Пишем в json
			item = {
				'name': [{'lang': 'ru', 'value': main_name, 'type': 'MAIN'}],
				'address': [{'one_line':u'{}, {}'.format(country,address), 'lang': 'ru'}],
				'phone': phone,
				'url': [{"type": "MAIN", "value": u'https://belorusdvorik.ru/'}],
				'actualization_date': int(time()),
				'rubric_id': [{'value': _.strip()} for _ in rubrics]
			}
			print(json.dumps(item, ensure_ascii=False))


if __name__ == '__main__':
	url_req = 'https://belorusdvorik.ru/adresa-magazinov.html'
	parse(url_req)