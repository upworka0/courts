"""courts URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from lawyers.views import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', home_page),

    url(r'^cases_types/$', cases_types, name='cases-types'),
    url(r'^lawyers_list/', lawyers_by_case, name='lawyers-list'),

    url(r'^search_lawyers/$', search_lawyers),

    url(r'^lawyer/(?P<pk>\d+)/$', LawyerView.as_view()),
    url(r'^cases/(?P<bar_card>\d+)/$', cases_table_view),

    url(r'^add/$', add_lawyer),

    url(r'^cases_data/(?P<case_id>\d+)/$', cases_datas),
    url(r'^ajax_case/', ajax_case),

    url(r'^update_all_data/', update_all_data),

    url(r'^django-rq/', include('django_rq.urls')),
]

urlpatterns += staticfiles_urlpatterns()