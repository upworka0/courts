from lawyers.models import Case, Lawyer
from django.core.management.base import BaseCommand
from courts.settings import BASE_DIR
import os, json

class Command(BaseCommand):
    def import_cases(self):
        json_path = os.path.join(BASE_DIR, 'scrappers', 'data', 'txcourts details.json')
        with open(json_path, 'r') as f:
            rows = json.load(f)

        for r, row in enumerate(rows):
            if r%1000==0:
                print('{} out of {}'.format(r, len(rows)))
                
            if not row.get('Bar Card', None):
                continue
            if not row.get('Case Number', None):
                continue
            if 'Your search found no results. Try broadening your search criteria.' == row.get('Case Number', ''):
                continue
            
            obj = Case()
            bar_card = row.get('Bar Card', '')
            lawyer = Lawyer.objects.get(bar_card=bar_card)
            
            obj.lawyer = lawyer
            obj.appellate_court = row.get('Appellate Court', '')
            obj.coa_case_number  = row.get('COA Case Number', '')
            obj.case_number  = row.get('Case Number', '')
            obj.case_type = row.get('Case Type', '').replace('&', 'and').upper().strip()
            obj.date_filed = row.get('Date Filed', '')
            obj.style = row.get('Style', '')
            obj.trial_court = row.get('Trial Court', '')
            obj.trial_court_case_number = row.get('Trial Court Case Number', '')
            obj.trial_court_county = row.get('Trial Court County', '')
            obj.v = row.get('v.', '')

            try:
                obj.save()
            except:
                pass
        
    def handle(self, *args, **options):
        """
        Call the function to import data
        """
        self.import_cases()
