import random
from time import sleep

import requests
from lxml.html import fromstring
from multiprocessing.pool import ThreadPool
import json

search_url = 'https://www.avvo.com/search/lawyer_search?loc=tx&page={}&q=appeals-lawyer&sort=relevancy'.format
pages = range(1, 239)


def get_names(page):
    url = search_url(page)
    res = requests.get(
        url=url,
        headers={
            'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US, en; q=0.8, ko; q=0.5, ru; q=0.3',
            'Host': 'www.avvo.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299'
        },
    )
    print(res.status_code)
    t = fromstring(res.text)
    names = t.xpath('//h3[@itemprop="name"]/text()')
    return names

names = []
for page in pages:
    names += get_names(page)
    print(len(names))
    sleep(random.randint(7, 10))

# pool = ThreadPool(8)
# for r, chunk in enumerate(pool.imap_unordered(get_names, pages)):
#     names += chunk
#     if r % 20 == 0:
#         print(r)


with open('data/names.json', 'w') as f:
    json.dump(names, f)

with open('data/names.json') as f:
    names = json.load(f)
    print(len(names))
    print(len(set(names)))
