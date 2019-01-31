from django import template

register = template.Library()


@register.filter
def split_address(value):
    if ';' in value:
        return value.split(';')
    return value, ''


@register.filter
def index(value, arg):
    return value[arg]


@register.filter
def get_by_index(l, i):
    return l[i]


@register.filter
def get_avatar_url(url):
    if url:
        return "https://www.texasbar.com" + url[16:-2]
    else:
        return url


@register.filter
def get_case_type(case_type):
    return case_type.replace('&', '_')


@register.filter
def get_ocase_type(case_type):
    return case_type.replace('_', '&')
