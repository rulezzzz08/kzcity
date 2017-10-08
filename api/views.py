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
    if request.GET.get('route_num') and request.GET.get('route_id') and request.GET.get('day_id'):
        cursor = connection.cursor()
        params = dict(
            route_num=request.GET['route_num'],
            route_id=request.GET['route_id'],
            day_id=request.GET['day_id']
        )
        sql_query = """
            SELECT r.route_num r_num, r.id r_id, t.line_id l_id, dd.id d_id, dd.short_name day, t.id t_id, t.hour, 
            t.minutes, c_fr.id c_fr_id, c_fr.name c_fr_name, s_fr.id s_fr_id, s_fr.name s_fr_name, c_to.id c_to_id, 
            c_to.name c_to_name, s_to.id s_to_id, s_to.name s_to_name, l.remark rem
            FROM
            (
                SELECT route_num, route_id, line_id, day_id, id, hour, minutes 
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
            ORDER BY r_num, r_id, t_id;
        """
        cursor.execute(sql_query, params)
        sql_result = cursor.fetchall()
        timetables = []
        for row in sql_result:
            timetable = dict(
                route_num=row[0],
                route_id=row[1],
                line_id=row[2],
                day_id=row[3],
                day_short_name=row[4],
                timetable_id=row[5],
                hour=row[6],
                minutes=row[7],
                city_from_id=row[8],
                city_from_name=row[9],
                station_from_id=row[10],
                station_from_name=row[11],
                city_to_id=row[12],
                city_to_name=row[13],
                station_to_id=row[14],
                station_to_name=row[15],
                remark=row[16]
            )
            timetables.append(timetable)
        return HttpResponse(json.dumps(timetables, ensure_ascii=False))
    return HttpResponseBadRequest


def get_timetable(request):
    if request.GET.get('route_num') and request.GET.get('route_id'):
        cursor = connection.cursor()
        params = dict(
            route_num=request.GET['route_num'],
            route_id=request.GET['route_id']
        )
        sql_query = """
            SELECT r.route_num r_num, r.id r_id, t.line_id l_id, dd.id d_id, dd.short_name day, t.id t_id, t.hour, 
            t.minutes, c_fr.id c_fr_id, c_fr.name c_fr_name, s_fr.id s_fr_id, s_fr.name s_fr_name, c_to.id c_to_id, 
            c_to.name c_to_name, s_to.id s_to_id, s_to.name s_to_name, l.remark rem
            FROM
            (
                SELECT route_num, route_id, line_id, day_id, id, hour, minutes
                FROM timetables
                WHERE route_num = %(route_num)s # param
                AND route_id = %(route_id)s # param
            ) t
            JOIN routes r ON t.route_num = r.route_num AND t.route_id = r.id
            JOIN kzcity.lines l ON t.route_num = l.route_num AND t.route_id = l.route_id AND t.line_id = l.id
            JOIN cities c_fr ON r.city_from_id = c_fr.id
            JOIN stations s_fr ON r.city_from_id = s_fr.city_id AND r.station_from_id = s_fr.id
            JOIN cities c_to ON r.city_to_id = c_to.id
            JOIN stations s_to ON r.city_to_id = s_to.city_id AND r.station_to_id = s_to.id
            JOIN days_dict dd ON t.day_id = dd.id
            ORDER BY r_num, r_id, d_id, t_id;
        """
        cursor.execute(sql_query, params)
        sql_result = cursor.fetchall()
        timetables = []
        for row in sql_result:
            timetable = dict(
                route_num=row[0],
                route_id=row[1],
                line_id=row[2],
                day_id=row[3],
                day_short_name=row[4],
                timetable_id=row[5],
                hour=row[6],
                minutes=row[7],
                city_from_id=row[8],
                city_from_name=row[9],
                station_from_id=row[10],
                station_from_name=row[11],
                city_to_id=row[12],
                city_to_name=row[13],
                station_to_id=row[14],
                station_to_name=row[15],
                remark=row[16]
            )
            timetables.append(timetable)
        return HttpResponse(json.dumps(timetables, ensure_ascii=False))
    return HttpResponseBadRequest


def get_cats(request):
    cursor = connection.cursor()
    sql_query = """
            select c.id cat_id, c.name cat, s.id sub_id, s.name sub
            from org_categories c
            left join org_subcategories s
            on c.id = s.cat_id
            order by cat, sub;
        """
    cursor.execute(sql_query)
    sql_result = cursor.fetchall()
    categories = [dict(id=sql_result[0][0], name=sql_result[0][1])]
    if sql_result[0][3] is not None:
        categories[0]['subcategories'] = [dict(id=sql_result[0][2], name=sql_result[0][3])]
    for i, row in enumerate(sql_result[1:]):
        if row[0] != sql_result[i][0]:
            categories.append(dict(id=row[0], name=row[1]))
            if row[2] is not None:
                categories[-1]['subcategories'] = [dict(id=row[2], name=row[3])]
        else:
            categories[-1].get('subcategories', []).append(dict(id=row[2], name=row[3]))
    return HttpResponse(json.dumps(categories, ensure_ascii=False))


def get_orgs(request):
    cursor = connection.cursor()
    if request.GET.get('subcat_id') and request.GET.get('cat_id'):
        params = dict(
            cat=request.GET['cat_id'],
            subcat=request.GET['subcat_id']
        )
        sql_query = """
            select card.city_id, c.name city, card.street_id, s.name street, building_num, 
            card.id, card.name name, cat_id, subcat_id, lon, lat, phone, url, description
            from
            (
                select *
                from org_cards
                where cat_id = %(cat)s # param
                and subcat_id = %(subcat)s # param
            ) as card
            join cities c on card.city_id = c.id
            join streets s on card.street_id = s.id
            order by name
        """
    elif request.GET.get('cat_id'):
        params = dict(
            cat=request.GET['cat_id'],
        )
        sql_query = """
                    select card.city_id, c.name city, card.street_id, s.name street, building_num, 
                    card.id, card.name name, cat_id, subcat_id, lon, lat, phone, url, description
                    from
                    (
                        select *
                        from org_cards
                        where cat_id = %(cat)s # param
                    ) as card
                    join cities c on card.city_id = c.id
                    join streets s on card.street_id = s.id
                    order by name
                """
    else:
        return HttpResponseBadRequest
    cursor.execute(sql_query, params)
    sql_result = cursor.fetchall()
    orgs = []
    for row in sql_result:
        org = dict(
            city_id=row[0],
            city=row[1],
            street_id=row[2],
            street=row[3],
            building_num=row[4],
            id=row[5],
            name=row[6],
            cat_id=row[7],
            subcat_id=row[8],
            lon=row[9],
            lat=row[10],
            phone=row[11],
            url=row[12],
            description=row[13]
        )
        orgs.append(org)
    return HttpResponse(json.dumps(orgs, ensure_ascii=False))
