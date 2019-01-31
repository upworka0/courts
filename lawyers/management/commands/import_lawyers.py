from lawyers.models import Lawyer
from django.core.management.base import BaseCommand
from courts.settings import BASE_DIR
import os, json

class Command(BaseCommand):
    def import_lawyers(self):
        json_path = os.path.join(BASE_DIR, 'scrappers', 'data', 'texasbar details.json')
        with open(json_path, 'r') as f:
            rows = json.load(f)
        seen = set()
        for row in rows:
            if not row.get('First Name', ''):
                    continue
            if row.get('Bar Card', '') in seen:
                continue
            obj = Lawyer()
            seen.add(row.get('Bar Card', ''))
            obj.bar_card = row.get('Bar Card', '')
            obj.first_name = row.get('First Name', '')
            obj.last_name  = row.get('Last Name', '')
            obj.full_name  = row.get('Full Name', '')
            obj.status = row.get('Status', '')
            obj.company = row.get('Company', '')
            obj.practice_areas = row.get('Practice Areas', '')
            obj.address = row.get('Address', '')
            obj.practice_location =row.get('Practice Location', '')
            obj.gmaps_img = row.get('Gmaps img', '')
            profile_img = row.get('Profile img', '').split('url(')[-1].strip(');')
            if profile_img:
                obj.profile_img = row.get('Bar Card', '')+'.jpg'
            else:
                obj.profile_img = 'no_avatar.jpg'
            obj.license_date = row.get('License Date', '')
            obj.statutory_profile_date = row.get('Statutory Profile Date', '')

            try:
                obj.save()
            except:
                pass

    def handle(self, *args, **options):
        """
        Call the function to import data
        """
        self.import_lawyers()
