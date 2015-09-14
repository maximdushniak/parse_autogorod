#!/usr/bin/env python

import csv
import sys
import time

import requests
import lxml.html


def get_proxies():
    return {'http': '108.162.197.97:80'}

def get_params(art):
    params = dict(article=art, time='false', ajax='true', sort='article')

    return params


def get_headers():
    headers = {'Host': 'avtogorod.by',
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0',
               'Accept': '*/*', 'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
               'Accept-Encoding': 'gzip, deflate', 'DNT': '1', 'X-Requested-With': 'XMLHttpRequest',
               'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Connection': 'keep-alive'}

    return headers


def parse_result_table(doc, searchart='', searchmark=''):
    d = []

    for row in doc.xpath(
            './/div/div/div[@id="ajax_analogs"]/table[@class="details-list filterResultTable xsmalls"]//tr[@class]'):  # Строки таблицы с результами
        try:
            place = row.xpath(
                'td[normalize-space(@class)="th-td-result-place cell td-color2"]|td[normalize-space(@class)="th-td-result-place td-color"]')[
                0].text_content().strip()

            if place.upper() == 'ПОД ЗАКАЗ': continue

            brend = row.xpath(
                'td[normalize-space(@class)="th-td-result-brand cell td-color2"]/span|td[normalize-space(@class)="th-td-result-brand td-color"]/span')[
                0].text_content().strip()
            art = row.xpath(
                'td[normalize-space(@class)="th-td-result-article td-color"]/span/span/b|td[normalize-space(@class)="th-td-result-article cell td-color2"]/span/span/b')[
                0].text_content().strip()
            descr = row.xpath(
                'td[normalize-space(@class)="th-td-result-descr cell td-color2"]/span[@class="artlook-descr"]/span[@class="descr-hide-overflow"]|td[normalize-space(@class)="th-td-result-descr td-color"]/span[@class="artlook-descr"]/span[@class="descr-hide-overflow"]')[
                0].text_content().strip()

            price = row.xpath(
                'td[normalize-space(@class)="th-td-result-price box-price-view cell td-color2"]|td[normalize-space(@class)="th-td-result-price box-price-view td-color"]')[
                0]
            price_value = price.xpath('span[@itemprop="offers"]')[0].text_content().strip()

            # price_curency = price.xpath('meta')

            d.append([searchmark, searchart, brend, art, descr, place, price_value])
        except:
            pass

    return d


def search_article(art, mark=''):
    url = 'http://avtogorod.by'
    search_url = url + '/search/artlookup/'

    headers = get_headers()
    params = get_params(art)
    proxies = get_proxies()

    r = requests.get(search_url, headers=headers, params=params, proxies = proxies)

    # Парсим, если есть аналоги
    doc = lxml.html.document_fromstring(r.text)

    d = []
    aaa = doc.xpath('.//div/div/table/tr/td/h1[@class="uppercase"]')

    if len(aaa) == 1:
        if aaa[0].text_content().strip().upper() == 'Производители'.upper():
            for table in doc.find_class('details-list filterResultTable set-search-grid xsmalls'):
                for tr in table.find_class('cursor'):
                    if mark.upper() in tr[1].text_content().strip().upper():
                        search_url = url + tr[3][0].get('href')
                        r = requests.get(search_url, headers=headers, params=params, proxies = proxies)
                        doc = lxml.html.document_fromstring(r.text)

                    d += parse_result_table(doc, art, mark)

        else:
            d += parse_result_table(doc, art, mark)

    return d


start_datetime = time.time()

print('Start:', time.ctime(start_datetime))
print('-------------------------------------')

res_list = []

filename = 'search.txt'
if len(sys.argv) > 1:
    filename = sys.argv[1]

with open(filename, newline='') as csvfile:
    print('Read file: ' + filename)
    reader = csv.reader(csvfile, dialect='excel', delimiter='\t')
    # n = 0
    for row in reader:
        # n += 1
        print('Parse:', row)
        art = row[0].strip()
        mark = ''
        if len(row) == 2:
            mark = row[1].strip()

        res_list += search_article(art, mark)

if len(res_list) > 0:
    res_list = [['Искомый бренд', 'Искомый артикул', 'Бренд', 'Артикул', 'Наименование', 'Направление',
                 'Цена']] + res_list

    result_file = open("result_file.csv", 'w', newline='')
    wr = csv.writer(result_file, quoting=csv.QUOTE_ALL, delimiter=';')

    wr.writerows(res_list)

    print('File safe in: ', result_file.name)

end_datetime = time.time()

print('-------------------------------------')
print('Finish:', time.ctime(end_datetime))
print('Time:', (end_datetime-start_datetime), '(sec)')
print('')
input('Press any key..')
