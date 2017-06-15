from django.conf.urls import url

from api import views

urlpatterns = [
    url(r'^$', views.test),
    url(r'^get_children_polyclinic_timetable$', views.get_children_polyclinic_timetable),
    url(r'^get_adult_polyclinic_timetable$', views.get_adult_polyclinic_timetable)
]