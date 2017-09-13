import json
from django.db import connection
from django.http import HttpResponse
from lxml import html
from django.http import HttpResponseBadRequest


def get_polyclinic_timetable(url):
    properties_daily = ['speciality', 'name', 'room', 'region', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday']
    properties_remarks = ['speciality', 'name', 'room', 'region', 'remarks']
    doctors = []
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
    return json.dumps(doctors, ensure_ascii=False)  # ensure-ascii???


def test(request):
    return HttpResponse('test')


def get_children_polyclinic_timetable(request):
    url = 'http://uslugivkz.ru/index.php/uslugi-chastnykh-lits/raspisanie-detskoj-polikliniki'
    timetable = get_polyclinic_timetable(url)
    return HttpResponse(timetable)


def get_adult_polyclinic_timetable(request):
    url = 'http://uslugivkz.ru/index.php/uslugi-chastnykh-lits/rasp-vz-pol'
    timetable = get_polyclinic_timetable(url)
    return HttpResponse(timetable)


def get_all_routes(request):
    cursor = connection.cursor()
    sql_query = """
        SELECT r.route_num r_num, r.id r_id, c_fr.id c_fr_id, c_fr.name c_fr_name, s_fr.id s_fr_id,
        s_fr.name s_fr_name, c_to.id c_to_id, c_to.name c_to_name, s_to.id s_to_id, s_to.name s_to_name
        FROM routes r
        JOIN cities c_fr ON r.city_from_id = c_fr.id
        JOIN stations s_fr ON r.city_from_id = s_fr.city_id AND r.station_from_id = s_fr.id
        JOIN cities c_to ON r.city_to_id = c_to.id
        JOIN stations s_to ON r.city_to_id = s_to.city_id AND r.station_to_id = s_to.id
        ORDER BY r_num;
    """
    cursor.execute(sql_query)
    sql_result = cursor.fetchall()
    all_routes = []
    for row in sql_result:
        route = dict(
            route_num=row[0],
            route_id=row[1],
            city_from_id=row[2],
            city_from_name=row[3],
            station_from_id=row[4],
            station_from_name=row[5],
            city_to_id=row[6],
            city_to_name=row[7],
            station_to_id=row[8],
            station_to_name=row[9]
        )
        all_routes.append(route)
    return HttpResponse(json.dumps(all_routes, ensure_ascii=False))


def get_timetable_daily(request):
    x = request.GET.get('route_num')
    y = request.GET.get('route_id')
    z = request.GET.get('day_id')
    if request.GET.get('route_num') and request.GET.get('route_id') and request.GET.get('day_id'):
        cursor = connection.cursor()
        params = dict(
            route_num=request.GET['route_num'],
            route_id=request.GET['route_id'],
            day_id=request.GET['day_id']
        )
        sql_query = """
            SELECT r.route_num r_num, r.id r_id, t.line_id l_id, dd.id d_id, dd.short_name day, t.id t_id, t.time, 
            c_fr.id c_fr_id, c_fr.name c_fr_name, s_fr.id s_fr_id, s_fr.name s_fr_name, c_to.id c_to_id, 
            c_to.name c_to_name, s_to.id s_to_id, s_to.name s_to_name, l.remark rem
            FROM
            (
                SELECT route_num, route_id, line_id, day_id, id, hour, minutes, CONCAT_WS(':', hour, minutes) time 
                FROM timetables
                WHERE route_num = %(route_num)s # param
                AND route_id = %(route_id)s # param
                AND day_id = %(day_id)s # param
            ) t
            JOIN routes r ON t.route_num = r.route_num AND t.route_id = r.id
            JOIN kzcity.lines l ON t.route_num = l.route_num AND t.route_id = l.route_id AND t.line_id = l.id
            JOIN cities c_fr ON r.city_from_id = c_fr.id
            JOIN stations s_fr ON r.city_from_id = s_fr.city_id AND r.station_from_id = s_fr.id
            JOIN cities c_to ON r.city_to_id = c_to.id
            JOIN stations s_to ON r.city_to_id = s_to.city_id AND r.station_to_id = s_to.id
            JOIN days_dict dd ON t.day_id = dd.id
            ORDER BY r_num, r_id, l_id, t_id;
        """
        cursor.execute(sql_query, params)
        sql_result = cursor.fetchall()
        timetable = []
        for row in sql_result:
            timetable_element = dict(
                route_num=row[0],
                route_id=row[1],
                line_id=row[2],
                day_id=row[3],
                day_short_name=row[4],
                timetable_id=row[5],
                time=row[6],
                city_from_id=row[7],
                city_from_name=row[8],
                station_from_id=row[9],
                station_from_name=row[10],
                city_to_id=row[11],
                city_to_name=row[12],
                station_to_id=row[13],
                station_to_name=row[14],
                remark=row[15]
            )
            timetable.append(timetable_element)
        return HttpResponse(json.dumps(timetable, ensure_ascii=False))
    return HttpResponseBadRequest
