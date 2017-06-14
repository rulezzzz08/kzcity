import json

from django.http import HttpResponse
from lxml import html


def test(request):
    properties_daily = ['speciality', 'name', 'room', 'region', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday']
    properties_remarks = ['speciality', 'name', 'room', 'region', 'remarks']
    doctors = []
    # url = 'http://uslugivkz.ru/index.php/uslugi-chastnykh-lits/raspisanie-detskoj-polikliniki'
    url = 'http://uslugivkz.ru/index.php/uslugi-chastnykh-lits/rasp-vz-pol'
    # print(datetime.datetime.now())
    html_tree = html.parse(url)
    root = html_tree.getroot()
    tbody = root.xpath(r'.//tbody[@class="fabrik_groupdata"]')[0]
    for tr in tbody:
        doctor = {}
        if len(tr) == 5:
            properties = properties_remarks
        else:
            properties = properties_daily
        for i, td in enumerate(tr):
            value = td.xpath(r'descendant::text()')
            if len(value) > 0:
                doctor[properties[i]] = value[0]
        doctors.append(doctor)
    print({'value': doctors})
    # print(datetime.datetime.now())
    return HttpResponse(json.dumps(doctors, ensure_ascii=False))  # ensure-ascii???
