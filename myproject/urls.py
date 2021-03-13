from django.contrib import admin
from django.urls import path

from data import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.home, name="home"),
    path("water/", views.water, name="water"),
    path("gas/", views.gas, name="gas"),
    path("electricity/", views.electricity, name="electricity"),
    path("car_gas/", views.car_gas, name="car_gas"),
    path("car_miles/", views.car_miles, name="car_miles"),
]
