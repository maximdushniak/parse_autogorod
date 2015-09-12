import requests
import lxml.html
import csv


def get_params(art):
    params = {'article': art, 'time': 'false', 'ajax': 'true', 'sort': 'article'}

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

        brend = row.xpath(
            'td[normalize-space(@class)="th-td-result-brand cell td-color2"]/span|td[normalize-space(@class)="th-td-result-brand td-color"]/span')[
            0].text_content().strip()
        art = row.xpath(
            'td[normalize-space(@class)="th-td-result-article td-color"]/span/span/b|td[normalize-space(@class)="th-td-result-article cell td-color2"]/span/span/b')[
            0].text_content().strip()
        descr = row.xpath(
            'td[normalize-space(@class)="th-td-result-descr cell td-color2"]/span[@class="artlook-descr"]/span[@class="descr-hide-overflow"]|td[normalize-space(@class)="th-td-result-descr td-color"]/span[@class="artlook-descr"]/span[@class="descr-hide-overflow"]')[
            0].text_content().strip()
        place = row.xpath(
            'td[normalize-space(@class)="th-td-result-place cell td-color2"]|td[normalize-space(@class)="th-td-result-place td-color"]')[
            0].text_content().strip()

        if place.upper() == 'ПОД ЗАКАЗ': continue

        price = row.xpath(
            'td[normalize-space(@class)="th-td-result-price box-price-view cell td-color2"]|td[normalize-space(@class)="th-td-result-price box-price-view td-color"]')[0]
        price_value = price.xpath('span[@itemprop="offers"]')[0].text_content().strip()

        # price_curency = price.xpath('meta')

        d.append([searchmark, searchart, brend, art, descr, place, price_value])

    return d


def search_article(art, mark):
    url = 'http://avtogorod.by'
    search_url = url + '/search/artlookup/'

    headers = get_headers()
    params = get_params(art)

    r = requests.get(search_url, headers=headers, params=params)

    # Парсим, если есть аналоги
    doc = lxml.html.document_fromstring(r.text)

    d = []
    aaa = doc.xpath('.//div/div/table/tr/td/h1[@class="uppercase"]')

    b = []

    if len(aaa) == 1:
        if aaa[0].text_content().strip().upper() == 'Производители'.upper():
            for table in doc.find_class('details-list filterResultTable set-search-grid xsmalls'):
                for tr in table.find_class('cursor'):
                     if mark.upper() in tr[1].text_content().upper():
                         search_url = url + tr[3][0].get('href')
                         r = requests.get(search_url, headers=headers, params=params)
                         doc = lxml.html.document_fromstring(r.text)

                     d += parse_result_table(doc, art, mark)

        else:
           d += parse_result_table(doc, art, mark)

    return d

res_list = []

with open('search.txt', newline='') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        l = row[0].split()
        print(l)
        res_list += search_article(l[0], l[1])

if len(res_list) > 0:
    result_file = open("result_file.csv", 'w', newline='')
    wr = csv.writer(result_file, quoting=csv.QUOTE_ALL)

    wr.writerows(res_list)
    print('-------------------------------------')
    print('End!!!')

input('Press any key..')
