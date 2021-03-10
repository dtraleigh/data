from django.contrib import admin
from data.models import *


class WaterAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Water._meta.get_fields()]


class ElectricityAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Electricity._meta.get_fields()]


class GasAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Gas._meta.get_fields()]


admin.site.register(Water, WaterAdmin)
admin.site.register(Electricity, ElectricityAdmin)
admin.site.register(Gas, GasAdmin)
