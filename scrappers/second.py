import requests
from lxml.html import fromstring
from multiprocessing.pool import ThreadPool
import json

search_url = 'https://www.texasbar.com/AM/Template.cfm?Section=Find_A_Lawyer&Template=/CustomSource/MemberDirectory/Result_form_client.cfm'
blank_params = {'PPlCityName': '', 'County': '', 'State': '', 'Zip': '', 'FirstName': '', 'LastName': '', 'FormerLastName': '', 'CompanyName': '', 'BarCardNumber': '', 'Submitted': '1', 'ShowPrinter': '1', 'Find': '0'}


def get_texasbar_link(name):
    row = {'Avvo Name': name}
    split_name = name.split()
    if len(split_name) != 2:
        return row
    f_name, l_name = split_name
    params = blank_params.copy()
    params['FirstName'], params['LastName'] = f_name, l_name
    # Handling Request
    for i in range(3):
        try:
            res = requests.post(search_url, data=params, timeout=15)
            break
        except Exception as e:
            pass
    else:
        print(name)
        return row
    
    t = fromstring(res.text)
    link = t.xpath('//div[@class="avatar-column"]//h3/a/@href')
    if link:
        row['Link'] = 'https://www.texasbar.com' + link[0]
        return row
    return row

if __name__ == '__main__':
    with open('data/names.json', 'r') as f:
        names = json.load(f)
    names = list(set(names))

    data = []
    pool = ThreadPool(8)
    for r, chunk in enumerate(pool.imap_unordered(get_texasbar_link, names)):
        data.append(chunk)
        print(r)

    with open('data/texasbar links.json', 'w') as f:
        json.dump(data, f)
