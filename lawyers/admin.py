from django.contrib import admin
from .models import Lawyer, Case

# Register your models here.
admin.site.register(Lawyer)
admin.site.register(Case)