import requests
from lxml.html import fromstring
from lxml import etree
from multiprocessing.pool import ThreadPool
import json


def process_details(content):
    content = etree.tostring(content, with_tail=False, method='html')
    content = content.decode('utf-8')
    content = content.replace('  ', '').replace('\n', '').replace('\r', '').replace('\t', '')
    return content


def get_case(case_info):
    if 'events' in case_info:
        return case_info

    url = "http://www.search.txcourts.gov/Case.aspx?cn=" + case_info['Case Number']
    res = requests.get(url)
    if res.status_code != 200:
        return case_info

    t = fromstring(res.text)
    try:
        main_content = t.xpath('//div[@id="main-content"]/div[@class="row-fluid"]')

        case_info['events'] = process_details(main_content[2])
        case_info['trial'] = process_details(main_content[len(main_content) - 1])
        case_info['parties'] = process_details(main_content[4])
        case_info['calendars'] = process_details(main_content[3])
        case_info['briefs'] = process_details(main_content[1])
    except:
        return case_info
    return case_info


def update_case(case_info):
    url = "http://www.search.txcourts.gov/Case.aspx?cn=" + case_info.case_number
    res = requests.get(url)
    if res.status_code != 200:
        return res.status_code

    t = fromstring(res.text)
    try:
        main_content = t.xpath('//div[@id="main-content"]/div[@class="row-fluid"]')
        case_events = process_details(main_content[2])
        if case_info.case_events == case_events:
            return 'same'
        case_info.case_events = process_details(main_content[2])
        case_info.trial_court_information = process_details(main_content[len(main_content) - 1])
        case_info.parties = process_details(main_content[4])
        case_info.calendars = process_details(main_content[3])
        case_info.appellate_briefs = process_details(main_content[1])
        case_info.save()
        return 'updated'
    except:
        return 'error while updating'


def get_court(court_info):
    get_court.progress += 1

    if 'events' in court_info:
        return

    print(get_court.progress)

    url = "http://www.search.txcourts.gov/Case.aspx?cn=" + court_info['Case Number']
    res = requests.get(url)
    if res.status_code != 200:
        print('error occurred at', get_court.progress, 'with', res.status_code)
        return

    t = fromstring(res.text)
    try:
        main_content = t.xpath('//div[@id="main-content"]/div[@class="row-fluid"]')

        court_info['events'] = process_details(main_content[2])
        court_info['trial'] = process_details(main_content[len(main_content) - 1])
        court_info['parties'] = process_details(main_content[4])
        court_info['calendars'] = process_details(main_content[3])
        court_info['briefs'] = process_details(main_content[1])
        print(len(main_content), url, court_info['trial'])
    except Exception as e:
        print('error occurred at', get_court.progress, 'with', e)


if __name__ == '__main__':
    court_file = open('data/div1.json')
    court_infos = []
    for court in court_file.readlines():
        court_infos.append(json.loads(court))
    court_file.close()

    get_court.progress = 0

    pool = ThreadPool(32)
    for id, _ in enumerate(pool.imap_unordered(get_court, court_infos)):
        if get_court.progress % 200 == 0:
            print(len(court_infos))
            court_file = open('data/div1.json', 'w')
            for case in court_infos:
                court_file.write(json.dumps(case) + '\n')
            court_file.close()

    court_file = open('data/div1.json', 'w')
    for case in court_infos:
        court_file.write(json.dumps(case) + '\n')
    court_file.close()
