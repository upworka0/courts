from lawyers.models import Case, Lawyer
from django.core.management.base import BaseCommand
from django.db.models import Count
from courts.settings import BASE_DIR
from multiprocessing.pool import ThreadPool
import os

from courts import settings
from scrappers.forth import get_cases
from scrappers.fifth import get_case

import requests
from lxml.html import fromstring


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('texasbar_link', type=str)

    def import_lawyer(self, row):
        obj = Lawyer()
        obj.bar_card = row.get('Bar Card', '')
        obj.first_name = row.get('First Name', '')
        obj.last_name = row.get('Last Name', '')
        obj.full_name = row.get('Full Name', '')
        obj.status = row.get('Status', '')
        obj.company = row.get('Company', '')
        obj.practice_areas = row.get('Practice Areas', '')
        obj.address = row.get('Address', '')
        obj.practice_location = row.get('Practice Location', '')
        obj.gmaps_img = row.get('Gmaps img', '')
        obj.profile_img = row.get('Profile img', '')
        # profile_img = row.get('Profile img', '').split('url(')[-1].strip(');')
        # if profile_img:
        #     obj.profile_img = row.get('Bar Card', '')+'.jpg'
        # else:
        #     obj.profile_img = 'no_avatar.jpg'
        obj.license_date = row.get('License Date', '')
        obj.statutory_profile_date = row.get('Statutory Profile Date', '')

        try:
            obj.save()
        except:
            pass

    def save_case(self, row):
        obj = Case()
        bar_card = row.get('Bar Card', '')
        lawyer = Lawyer.objects.get(bar_card=bar_card)

        obj.lawyer = lawyer
        obj.appellate_court = row.get('Appellate Court', '')
        obj.coa_case_number = row.get('COA Case Number', '')
        obj.case_number = row.get('Case Number', '')
        obj.case_type = row.get('Case Type', '').replace('&', 'and').upper().strip()
        if obj.case_type not in ['11.07', '11.07 HC', '11.071', '1107-HC']:
            obj.case_type = ' '.join([word[0].upper() + word[1:] for word in obj.case_type.split() if
                                      word not in ['to', 'or', 'for', 'of', 'with', 'under']])
        obj.date_filed = row.get('Date Filed', '')
        obj.style = row.get('Style', '')
        obj.trial_court = row.get('Trial Court', '')
        obj.trial_court_case_number = row.get('Trial Court Case Number', '')
        obj.trial_court_county = row.get('Trial Court County', '')
        obj.v = row.get('v.', '')
        obj.appellate_briefs = row.get('briefs', '')
        obj.calendars = row.get('calendars', '')
        obj.case_events = row.get('events', '')
        obj.parties = row.get('parties', '')
        obj.trial_court_information = row.get('trial', '')

        try:
            obj.save()
        except:
            pass

    def import_cases(self, rows):
        db_values = list(Case.objects.values('case_number', 'lawyer_id'))
        if type(rows) == dict:
            if not rows.get('Bar Card', None) or not rows.get('Case Number', None):
                return
            if 'Your search found no results. Try broadening your search criteria.' == rows.get('Case Number', ''):
                return
            self.save_case(rows)
        else:
            rows = [case for case in rows if case['Bar Card'] and case['Case Number']
                    and case['Case Number'] != 'Your search found no results. Try broadening your search criteria.'
                    and not db_values.__contains__({'case_number': case['Case Number'], 'lawyer_id': case['Bar Card']})]

            pool = ThreadPool(32)
            for _, c in enumerate(pool.imap_unordered(get_case, rows)):
                print(c)
                self.save_case(c)
            
    def handle(self, *args, **options):
        """
        Call the function to import data
        """
        # try:
        texasbar_link = options['texasbar_link']
        if not texasbar_link:
            return ''
        row = {'Link': texasbar_link}
        lawyer_row = get_texasbar_details(row)
        print(lawyer_row)
        self.import_lawyer(lawyer_row)

        bar_card = lawyer_row.get('Bar Card', '')
        if not bar_card:
            return ''

        bar_card, cases_rows = get_cases(bar_card)
        self.import_cases(cases_rows)

        lawyers_list = Lawyer.objects.annotate(cases_count=Count('case')).order_by('-cases_count')
        file = open(settings.MEDIA_ROOT + '/lawyers.txt', 'w')
        for lawyer in lawyers_list:
            file.write(','.join([lawyer.bar_card, lawyer.full_name, str(lawyer.cases_count)]) + '\n')
        file.close()

        cases_list = Case.objects.values('case_type').exclude(case_type='').order_by('case_type')
        file = open(settings.MEDIA_ROOT + '/case_types.txt', 'w')
        file.write(str(','.join(sorted(set(list([case['case_type'] for case in cases_list]))))))
        file.close()

        return bar_card


def get_first(t):
    if t:
        return t[0].strip()
    return ''


def download_image(profile_img, bar_card):
    img_path = os.path.join(BASE_DIR, '..', 'staticfiles', 'images', '{}.jpg'.format(bar_card))
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
    sat_prof_date = ''.join(
        [t.strip() for t in elem.xpath('.//span[text()="Statutory Profile Last Certified On: "]/../../text()')])

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
