import requests
from lxml.html import fromstring
from multiprocessing.pool import ThreadPool
import json
import os

# rows = pd.read_excel('data/texasbar links.xlsx').fillna('').to_dict('records')


def get_first(t):
    if t:
        return t[0].strip()
    return ''


def download_image(profile_img, bar_card):
    img_path = '../static/images/{}.jpg'.format(bar_card)
    if os.path.exists(img_path):
        return
    img_url = 'https://www.texasbar.com' + profile_img.split('url(')[-1].strip(');')
    res = requests.get(img_url)    
    with open(img_path, 'wb') as f:
        f.write(res.content)


def get_texasbar_details(r):
    row = r.copy()
    if not row.get('Link', ''):
        return row       

    for i in range(3):
        try:
            res = requests.get(row['Link'], timeout=20)
            break
        except:
            pass
    else:
        print(row['Link'])
        return row
    
    t = fromstring(res.text)
    elem = t.xpath('//article[@class="lawyer"]')
    if elem:
        elem = elem[0]
    else:
        return row

    full_name = ' '.join(elem.xpath('.//h3/span/text()'))
    first_name = get_first(elem.xpath('.//span[@class="given-name"]/text()'))
    last_name = get_first(elem.xpath('.//span[@class="family-name"]/text()'))
    profile_img = get_first(elem.xpath('./div/img/@style'))
  
    status = get_first(elem.xpath('.//span[@id="member_status_detail_ui_dialog_anchor"]/text()'))
    company = get_first(elem.xpath('.//h5/text()'))
    
    bar_date = elem.xpath('.//strong[text()="Bar Card Number:"]/../text()')
    bar_card = bar_date[1].strip() if len(bar_date) > 1 else ''
    license_date = bar_date[3].strip() if len(bar_date) > 3 else ''
    
    practice_location = elem.xpath('.//strong[text()="Primary Practice Location:"]/../text()')
    practice_location = practice_location[1].strip() if len(practice_location) > 1 else ''

    address = ';'.join([t.strip() for t in elem.xpath('.//p[@class="address"]/span/text()') if t.strip()])    
    practice_areas = ''.join([t.strip() for t in elem.xpath('.//p[@class="areas"]/text()')])
    sat_prof_date = ''.join([t.strip() for t in elem.xpath('.//span[text()="Statutory Profile Last Certified On: "]/../../text()')])

    gmaps_image = get_first(elem.xpath('.//img[@class="show-desktop"]/@src'))

    # if profile_img and bar_card:
    #     try:
    #         download_image(profile_img, bar_card)
    #     except:
    #         pass
        
    row['Full Name'] = full_name
    row['First Name'] = first_name
    row['Last Name'] = last_name
    row['Bar Card'] = bar_card
    
    row['Status'] = status
    row['Company'] = company
      
    row['Practice Location'] = practice_location
    row['Address'] = address
    row['Practice Areas'] = practice_areas
    
    row['License Date'] = license_date
    row['Statutory Profile Date'] = sat_prof_date

    row['Profile img'] = profile_img
    row['Gmaps img'] = gmaps_image
    
    return row


if __name__ == '__main__':
    with open('data/texasbar links.json', 'r') as f:
        rows = json.load(f)
        
    data = []
    pool = ThreadPool(16)
    for r, chunk in enumerate(pool.imap_unordered(get_texasbar_details, rows)):
        data.append(chunk)
        # if r % 100 == 0:
        print(r)

    with open('data/texasbar details.json', 'w') as f:
        json.dump(data, f)
