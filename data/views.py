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
    years = get_years_list_from_data(all_water_data)
    water_line_data = create_line_data(years, all_water_data)
    all_water_data_sorted = all_water_data.order_by("-service_start_date")

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
    years = get_years_list_from_data(all_gas_data)
    gas_line_data = create_line_data(years, all_gas_data)
    all_gas_data_sorted = all_gas_data.order_by("-service_start_date")

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
    years = get_years_list_from_data(all_elec_data)
    elec_line_data = create_line_data(years, all_elec_data)
    all_elec_data_sorted = all_elec_data.order_by("-service_start_date")

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

    if all_CarMiles_data:
        years = []
        for datapoint in all_CarMiles_data:
            years.append(datapoint.reading_date.year)
        years = list(set(years))
        years.sort

        # To calculate VMT, we need monthA followed by monthB odometer reading
        # Trick is that if you want, ex: 2020 data, you need Jan 2021 datapoint to get Dec
        # First, get all points in a year. If there are 12 of them in the greatest year,
        # try to get the first month of the following year.
        VMT = []
        # If a single year
        if len(all_CarMiles_data) == 12:
            next_jan = CarMiles.objects.filter(reading_date__year=int(years_range) + 1, reading_date__month=1)
            VMT_calc_data = all_CarMiles_data.union(next_jan)
        VMT_calc_data_sorted = VMT_calc_data.order_by("reading_date")
        for count, datapoint in enumerate(VMT_calc_data_sorted):
            try:
                VMT.append(VMT_calc_data_sorted[count+1].odometer_reading - datapoint.odometer_reading)
            except IndexError:
                break

        car_miles_line_data = create_line_data(years, all_CarMiles_data)

        # Need to remove the last month
        logger.info("car_miles_line_data before pop\n")
        logger.info(car_miles_line_data)
        # car_miles_line_data[-1][2].pop()

        # At this point, we have [["2020", "rgba(0, 200, 0, 1)", [["0", 0], ["1", 0], ["2", 0], ["3", 0],
        # ["4", 0], ["5", 0], ["6", 0], ["7", 0], ["8", 0], ["9", 0], ["10", 0],
        # ["11", 0]]], ["2021", "rgba(200, 0, 0, 1)", [["0", 0], ["1", 0], ["2", 0], ["3", 0]]]]
        # Need to change odometer_reading to VMT for the month
        for year_count, year in enumerate(car_miles_line_data):
            for month_count, month in enumerate(year[2]):
                month[1] = VMT[year_count * 12 + month_count]

        # If we reverse the data, we need to reverse the VMT as well so they match
        table_data = zip(all_CarMiles_data.order_by("-reading_date"), VMT[::-1])
    else:
        car_miles_line_data = None
        table_data = None

    logger.info("car_miles_line_data:")
    logger.info(car_miles_line_data)
    logger.info("\nVMT")
    logger.info(VMT)
    # logger.info("\nall_CarMiles_data")
    # for datapoint in all_CarMiles_data.order_by("-reading_date"):
    #     logger.info(datapoint)

    return render(request, "miles.html", {"title": title,
                                          "measurement": measurement,
                                          "data": car_miles_line_data,
                                          "table_data": table_data,
                                          "years_range": years_range})
