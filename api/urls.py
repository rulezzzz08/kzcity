from django.conf.urls import url

from api import views

urlpatterns = [
    url(r'^$', views.test),
    url(r'^get_children_polyclinic_timetable$', views.get_children_polyclinic_timetable),
    url(r'^get_adult_polyclinic_timetable$', views.get_adult_polyclinic_timetable),
    url(r'^transport/get_all_routes$', views.get_all_routes),
    url(r'^transport/get_timetable_daily$', views.get_timetable_daily),
    url(r'^transport/get_timetable$', views.get_timetable)
]