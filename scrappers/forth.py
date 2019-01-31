import requests
from lxml.html import fromstring
from lxml import etree
from multiprocessing.pool import ThreadPool
import json
import re


def post_request(url, params):
    while True:
        try:
            res = requests.post(url, data=params)
            return res
        except:
            pass


def get_rows_of_table(table_elem, bar_card):
    data = []
    headers = [''.join(e.itertext()) for e in table_elem.xpath('thead/tr/th')]
    headers[0] = 'Case Number'
    table = [[''.join(map(strip_text, td.itertext())) for td in tr.xpath('td')] for tr in table_elem.xpath('tbody/tr')]

    for id, row in enumerate(table):
        new_row = {'Bar Card': bar_card}
        new_row.update({k: v for k, v in zip(headers, row)})
        data.append(new_row)
    return data


def get_all_pages_data(params, pages_num, t, bar_card):
    data = []
    params = params.copy()
    for i in range(pages_num):
        if i == 0:
            params['ctl00$ContentPlaceHolder1$grdCases$ctl00$ctl02$ctl00$ctl18'] = ' '
            del params['ctl00$ContentPlaceHolder1$btnSearch']
        else:
            params['__VIEWSTATE'] = t.xpath('//input[@name="__VIEWSTATE"]/@value')[0]
            params['__VIEWSTATEGENERATOR'] = t.xpath('//input[@name="__VIEWSTATEGENERATOR"]/@value')[0]

            res = post_request(search_url, params)
            t = fromstring(res.text)

        # check if the it returns the whole table
        table_elem = t.xpath('//table[@class=" rgClipCells"]')
        if table_elem:
            data = get_rows_of_table(table_elem[0], bar_card)
            return data

        table_elem = t.xpath('//table[@class="rgMasterTable rgClipCells"]')
        if table_elem:
            data += get_rows_of_table(table_elem[0], bar_card)
    return data


def strip_text(t):
    return t.strip()


def get_cases(bar_card):
    try:
        params = start_params.copy()
        params['ctl00$ContentPlaceHolder1$txtAttorneyNameOrBarNumber'] = bar_card
        res = post_request(search_url, params)
        t = fromstring(res.text)

        pages_num = t.xpath('//div[@class="rgWrap rgInfoPart"]/strong[2]/text()')
        pages_num = int(pages_num[0]) if pages_num else 0
        if pages_num == 0:
            if not res.text.__contains__('Print-Friendly'):
                print(bar_card, -1, end='\t')
                return bar_card, []

            def process_simple(content):
                content = str(content)
                content = content.replace('  ', '').replace('\n', '').replace('\r', '').replace('\t', '').replace(' ', '')
                return content

            case = {
                "Bar Card": bar_card,
                "Case Number": process_simple(t.xpath('//strong/text()')[1]),
                "Date Filed": process_simple(t.xpath('//div[@class="row-fluid"]/div[@class="span10"]/div/text()')[2]),
                "Style": process_simple(t.xpath('//div[@class="row-fluid"]/div[@class="span10"]/text()')[6]),
                "v.": process_simple(t.xpath('//div[@class="row-fluid"]/div[@class="span10"]/text()')[7]),
                "Case Type": process_simple(t.xpath('//div[@class="row-fluid"]/div[@class="span10"]/text()')[5]),
                "COA Case Number": "",
                "Trial Court Case Number": process_simple(t.xpath('//div[@class="row-fluid"]/div[@class="span4"]/text()')[3]),
                "Trial Court County": process_simple(t.xpath('//div[@class="row-fluid"]/div[@class="span4"]/text()')[1]),
                "Trial Court": process_simple(t.xpath('//div[@class="row-fluid"]/div[@class="span4"]/text()')[0]),
                "Appellate Court": "",

            }

            def process_details(content):
                content = etree.tostring(content, with_tail=False, method='html')
                content = content.decode('utf-8')
                content = content.replace('  ', '').replace('\n', '').replace('\r', '').replace('\t', '')
                return content

            main_content = t.xpath('//div[@id="main-content"]/div[@class="row-fluid"]')

            case['events'] = process_details(main_content[2])
            case['trial'] = process_details(main_content[6])
            case['parties'] = process_details(main_content[4])
            case['calendars'] = process_details(main_content[3])
            case['briefs'] = process_details(main_content[1])

            return bar_card, [case]

        elif pages_num == 1:
            table_elem = t.xpath('//table[@class="rgMasterTable rgClipCells"]')[0]
            data = get_rows_of_table(table_elem, bar_card)
        else:
            data = get_all_pages_data(params, pages_num, t, bar_card)

        return bar_card, data
    except Exception as e:
        print(bar_card, e)
        return bar_card, []


search_url = 'http://www.search.txcourts.gov/CaseSearch.aspx?coa=cossup'
try:
    blank_params = {t.split(':')[0]: ':'.join(t.split(':')[1:]) for t in open('formdata.txt', 'r').read().split('\n')}
except:
    blank_params = {t.split(':')[0]: ':'.join(t.split(':')[1:]) for t in open('scrappers/formdata.txt', 'r').read().split('\n')}
res = requests.get(search_url)
t = fromstring(res.text)
start_params = blank_params.copy()
start_params['__VIEWSTATE'] = t.xpath('//input[@name="__VIEWSTATE"]/@value')[0]
start_params['__VIEWSTATEGENERATOR'] = t.xpath('//input[@name="__VIEWSTATEGENERATOR"]/@value')[0]


if __name__ == '__main__':
    with open('data/texasbar details.json', 'r') as f:
        json_data = json.load(f)
        bar_cards = list(set([b['Bar Card'] for b in json_data if b.get('Bar Card', None)]))

    f = open('data/txcourts details.json', 'w')
    pool = ThreadPool(32)
    for c, chunk in enumerate(pool.imap_unordered(get_cases, bar_cards)):
        bar_card, cases = chunk
        for case in cases:
            f.write(json.dumps(case) + '\n')

        print(c)

    f.close()
