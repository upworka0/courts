from django.db import models
from datetime import datetime


class Lawyer(models.Model):
    bar_card = models.CharField(max_length=120, primary_key=True)
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    full_name = models.CharField(max_length=120)
    status = models.CharField(max_length=120, null=True, blank=True)
    company = models.CharField(max_length=120, null=True, blank=True)
    practice_areas = models.CharField(max_length=480, null=True, blank=True)

    address = models.CharField(max_length=120)
    practice_location = models.CharField(max_length=120, null=True, blank=True)

    gmaps_img = models.CharField(max_length=2000, null=True, blank=True)
    profile_img = models.CharField(max_length=2000, null=True, blank=True)

    license_date = models.CharField(max_length=60, null=True, blank=True)
    statutory_profile_date = models.CharField(max_length=60, null=True, blank=True)

    def __str__(self):
        return self.full_name


class Case(models.Model):
    lawyer = models.ForeignKey(Lawyer, on_delete=models.CASCADE)

    appellate_court = models.CharField(max_length=480, null=True, blank=True)
    coa_case_number = models.CharField(max_length=480, null=True, blank=True)
    case_number = models.CharField(max_length=480, null=True, blank=True)
    case_type = models.CharField(max_length=480, null=True, blank=True)
    date_filed = models.CharField(max_length=480, null=True, blank=True)
    style = models.CharField(max_length=480, null=True, blank=True)
    trial_court = models.CharField(max_length=480, null=True, blank=True)
    trial_court_case_number = models.CharField(max_length=480, null=True, blank=True)
    trial_court_county = models.CharField(max_length=480, null=True, blank=True)
    v = models.CharField(max_length=480, null=True, blank=True)

    case_events = models.TextField(null=True, blank=True)
    trial_court_information = models.TextField(null=True, blank=True)
    parties = models.TextField(null=True, blank=True)
    calendars = models.TextField(null=True, blank=True)
    appellate_briefs = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.case_number


class Status(models.Model):
    current_update = models.IntegerField(default=0)
