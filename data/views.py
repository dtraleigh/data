from django.shortcuts import render
from data.models import *
import logging
from datetime import datetime

from data.functions import *

logger = logging.getLogger("django")


def home(request):
    currentYear = datetime.now().year
    all_water_data = Water.objects.all()
    all_gas_data = Gas.objects.all()
    all_elec_data = Electricity.objects.all()
    all_vmt_data = CarMiles.objects.all()

    year_to_date_values = [get_YTD_values_for_any_year(currentYear, all_water_data),
                           get_YTD_values_for_any_year(currentYear, all_gas_data),
                           get_YTD_values_for_any_year(currentYear, all_elec_data),
                           get_YTD_values_for_any_year(currentYear, all_vmt_data)]
    prev_year_to_date_values = [get_YTD_values_for_any_year(currentYear - 1, all_water_data),
                                get_YTD_values_for_any_year(currentYear - 1, all_gas_data),
                                get_YTD_values_for_any_year(currentYear - 1, all_elec_data),
                                get_YTD_values_for_any_year(currentYear - 1, all_vmt_data)]
    avg_ytd_values = [get_YTD_values_for_all_years(all_water_data),
                      get_YTD_values_for_all_years(all_gas_data),
                      get_YTD_values_for_all_years(all_elec_data),
                      get_YTD_values_for_all_years(all_vmt_data)]

    return render(request, "home.html", {"year_to_date_values": year_to_date_values,
                                         "prev_year_to_date_values": prev_year_to_date_values,
                                         "avg_ytd_values": avg_ytd_values})


def water(request):
    title = "Water"
    measurement = "Average Gallons / Day"
    years_range = requested_years_to_use(request.GET.get("years"))

    all_water_data = get_measurement_data_from_years("Water", years_range)
    if all_water_data:
        all_water_data_sorted = all_water_data.order_by("-service_start_date")
    else:
        all_water_data_sorted = all_water_data

    years = get_years_list_from_data(all_water_data)
    water_line_data = create_line_data(years, all_water_data)

    return render(request, "page.html", {"title": title,
                                         "measurement": measurement,
                                         "data": water_line_data,
                                         "table_data": all_water_data_sorted,
                                         "years_range": years_range})


def gas(request):
    title = "Natural Gas"
    measurement = "Therms per month"
    years_range = requested_years_to_use(request.GET.get("years"))

    all_gas_data = get_measurement_data_from_years("Gas", years_range)
    if all_gas_data:
        all_gas_data_sorted = all_gas_data.order_by("-service_start_date")
    else:
        all_gas_data_sorted = all_gas_data

    years = get_years_list_from_data(all_gas_data)
    gas_line_data = create_line_data(years, all_gas_data)

    return render(request, "page.html", {"title": title,
                                         "measurement": measurement,
                                         "data": gas_line_data,
                                         "table_data": all_gas_data_sorted,
                                         "years_range": years_range})


def electricity(request):
    title = "Electricity"
    measurement = "Kilowatt hours used"
    years_range = requested_years_to_use(request.GET.get("years"))

    all_elec_data = get_measurement_data_from_years("Electricity", years_range)
    if all_elec_data:
        all_elec_data_sorted = all_elec_data.order_by("-service_start_date")
    else:
        all_elec_data_sorted = all_elec_data

    years = get_years_list_from_data(all_elec_data)
    elec_line_data = create_line_data(years, all_elec_data)

    return render(request, "page.html", {"title": title,
                                         "measurement": measurement,
                                         "data": elec_line_data,
                                         "table_data": all_elec_data_sorted,
                                         "years_range": years_range})


def car_miles(request):
    title = "Vehicle Miles Traveled"
    measurement = "Miles / Month"
    years_range = requested_years_to_use(request.GET.get("years"))
    all_CarMiles_data = get_measurement_data_from_years("CarMiles", years_range)
    car_miles_line_data = None
    table_data = None

    if all_CarMiles_data:
        VMT = []
        for datapoint in all_CarMiles_data.order_by("reading_date"):
            vmt_value = get_VMT_calculation(datapoint)
            if vmt_value:
                VMT.append(vmt_value)

        # Create sorted list of years, ex: [2020, 2021, 2022]
        years = []
        for datapoint in all_CarMiles_data:
            years.append(datapoint.reading_date.year)
        years = list(set(years))
        years.sort()
        car_miles_line_data = create_car_line_data(years, all_CarMiles_data.order_by("reading_date"), VMT)

        # If we reverse the data, we need to reverse the VMT as well so they match
        if len(all_CarMiles_data) % 12 != 0:
            table_data = zip(all_CarMiles_data.order_by("-reading_date")[1:], VMT[::-1])
        else:
            table_data = zip(all_CarMiles_data.order_by("-reading_date"), VMT[::-1])

        # logger.info("car_miles_line_data:")
        # logger.info(car_miles_line_data)
        # logger.info("\nVMT")
        # logger.info(VMT)
        # logger.info("\nall_CarMiles_data")
        # for datapoint in all_CarMiles_data.order_by("-reading_date"):
        #     logger.info(datapoint)

    return render(request, "miles.html", {"title": title,
                                          "measurement": measurement,
                                          "data": car_miles_line_data,
                                          "table_data": table_data,
                                          "years_range": years_range})