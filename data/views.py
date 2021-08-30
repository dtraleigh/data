from django.shortcuts import render
from data.models import *
import logging
from datetime import datetime

colors = ["rgba(0, 200, 0, 1)",  # Green
          "rgba(200, 0, 0, 1)",  # Red
          "rgba(191, 63, 148, 1)",  # Magenta
          "rgba(20, 23, 234, 1)",  # Blue
          "rgba(234, 173, 20, 1)",  # Orange
          "rgba(154, 101, 54, 1)",  # Brown
          "rgba(172, 243, 118, 1)",  # light green
          "rgba(101, 54, 154, 1)",  # Purple
          "rgba(172, 243, 118, 1)",  # dark green
          "rgba(246, 223, 141, 1)",  # Tan
          "rgba(246, 223, 141, 1)"  # pink
          ]

logger = logging.getLogger("django")


def get_years_list_from_data(object_data):
    # Returns a sorted list of years found across all service dates
    dataset_years = []

    for datapoint in object_data:
        dataset_years.append(datapoint.service_start_date.year)
        dataset_years.append(datapoint.service_end_date.year)

    dataset_years = list(set(dataset_years))
    dataset_years.sort()

    return dataset_years


def get_midpoint_of_dates(date1, date2):

    return date1 + (date2 - date1)/2


def requested_years_to_use(years_range):
    # use the years from the request else, use this year and last
    if not years_range:
        return str(datetime.now().year - 2) + "-" + str(datetime.now().year)
    return years_range


def home(request):

    return render(request, "home.html", {"colors": colors})


def water(request):
    title = "Water"
    measurement = "Average Gallons / Day"
    years_range = requested_years_to_use(request.GET.get("years"))
    year = request.GET.get("year")

    if year:
        all_water_data = Water.objects.filter(service_start_date__year=year)
    elif years_range:
        if "-" in years_range:
            all_water_data = Water.objects.filter(service_start_date__year__gte=years_range.split("-")[0],
                                                  service_start_date__year__lte=years_range.split("-")[1])
        elif "," in years_range:
            # Get all data then remove the ones that don't match these years
            all_data = Water.objects.all()
            all_water_data = []
            for y in years_range.split(","):
                for d in all_data:
                    if d.service_start_date.year == int(y):
                        all_water_data.append(d)

    years = get_years_list_from_data(all_water_data)

    # Template ["label", "color", [["2018, 9", 46.8], ...]]
    water_line_data = []
    for count, year in enumerate(years):
        this_year_water_line_data = []
        this_year_water_line_data.append(str(year))
        this_year_water_line_data.append(colors[count])

        water_data = []
        for water_bill in all_water_data:
            midpoint_date = get_midpoint_of_dates(water_bill.service_start_date, water_bill.service_end_date)
            if midpoint_date.year == year:
                water_data.append([str(midpoint_date.month - 1), water_bill.avg_gallons_per_day])

        this_year_water_line_data.append(water_data)

        water_line_data.append(this_year_water_line_data)
    # logger.info("water_line_data")
    # logger.info(water_line_data)

    return render(request, "page.html", {"title": title,
                                         "measurement": measurement,
                                         "data": water_line_data,
                                         "table_data": all_water_data})


def gas(request):
    title = "Natural Gas"
    measurement = "Therms per month"
    years_range = requested_years_to_use(request.GET.get("years"))
    year = request.GET.get("year")

    if year:
        all_gas_data = Gas.objects.filter(service_start_date__year=year)
    elif years_range:
        if "-" in years_range:
            all_gas_data = Gas.objects.filter(service_start_date__year__gte=years_range.split("-")[0],
                                                  service_start_date__year__lte=years_range.split("-")[1])
        elif "," in years_range:
            # Get all data then remove the ones that don't match these years
            all_data = Gas.objects.all()
            all_gas_data = []
            for y in years_range.split(","):
                for d in all_data:
                    if d.service_start_date.year == int(y):
                        all_gas_data.append(d)

    years = get_years_list_from_data(all_gas_data)

    # Template ["label", "color", [["2018, 9", 46.8], ...]]
    gas_line_data = []
    for count, year in enumerate(years):
        this_year_gas_line_data = []
        this_year_gas_line_data.append(str(year))
        this_year_gas_line_data.append(colors[count])

        gas_data = []
        for gas_bill in all_gas_data:
            midpoint_date = get_midpoint_of_dates(gas_bill.service_start_date, gas_bill.service_end_date)
            if midpoint_date.year == year:
                gas_data.append([str(midpoint_date.month - 1), gas_bill.therms_usage])

        this_year_gas_line_data.append(gas_data)

        gas_line_data.append(this_year_gas_line_data)

    return render(request, "page.html", {"title": title,
                                         "measurement": measurement,
                                         "data": gas_line_data,
                                         "table_data": all_gas_data})


def electricity(request):
    title = "Electricity"
    measurement = "Kilowatt hours used"
    years_range = requested_years_to_use(request.GET.get("years"))
    year = request.GET.get("year")

    if year:
        all_elec_data = Electricity.objects.filter(service_start_date__year=year)
    elif years_range:
        if "-" in years_range:
            all_elec_data = Electricity.objects.filter(service_start_date__year__gte=years_range.split("-")[0],
                                                       service_start_date__year__lte=years_range.split("-")[1])
        elif "," in years_range:
            # Get all data then remove the ones that don't match these years
            all_data = Electricity.objects.all()
            all_elec_data = []
            for y in years_range.split(","):
                for d in all_data:
                    if d.service_start_date.year == int(y):
                        all_elec_data.append(d)

    years = get_years_list_from_data(all_elec_data)

    # Template ["label", "color", [["2018, 9", 46.8], ...]]
    elec_line_data = []
    for count, year in enumerate(years):
        this_year_elec_line_data = []
        this_year_elec_line_data.append(str(year))
        this_year_elec_line_data.append(colors[count])

        elec_data = []
        for elec_bill in all_elec_data:
            midpoint_date = get_midpoint_of_dates(elec_bill.service_start_date, elec_bill.service_end_date)
            if midpoint_date.year == year:
                elec_data.append([str(midpoint_date.month - 1), elec_bill.kWh_usage])

        this_year_elec_line_data.append(elec_data)

        elec_line_data.append(this_year_elec_line_data)

    return render(request, "page.html", {"title": title,
                                         "measurement": measurement,
                                         "data": elec_line_data,
                                         "table_data": all_elec_data})


def car_miles(request):
    title = "Vehicle Miles Traveled"
    measurement = "Miles / Month"
    years_range = requested_years_to_use(request.GET.get("years"))
    year = request.GET.get("year")

    if year:
        all_CarMiles_data = CarMiles.objects.filter(reading_date__year=year)
    elif years_range:
        if "-" in years_range:
            all_CarMiles_data = CarMiles.objects.filter(reading_date__year__gte=years_range.split("-")[0],
                                                        reading_date__year__lte=years_range.split("-")[1])
        elif "," in years_range:
            # Get all data then remove the ones that don't match these years
            all_data = CarMiles.objects.all()
            all_CarMiles_data = []
            for y in years_range.split(","):
                for d in all_data:
                    if d.reading_date.year == int(y):
                        all_CarMiles_data.append(d)

    years = []
    for datapoint in all_CarMiles_data:
        years.append(datapoint.reading_date.year)
    years = list(set(years))
    years.sort

    k = [j.odometer_reading for j in all_CarMiles_data]
    l = [j.odometer_reading for j in all_CarMiles_data[1:]]
    VMT = []

    for count, o in enumerate(l):
        VMT.append(o-k[count])
    # logger.info("VMT")
    # logger.info(VMT)

    # Create a year, here we add the year and color, not the VMT value just yet
    # Template ["label", "color", [["2018, 9", 46.8], ...]]
    car_miles_line_data = []
    for count, year in enumerate(years):
        this_year_car_miles_line_data = []
        this_year_car_miles_line_data.append(str(year))
        this_year_car_miles_line_data.append(colors[count])

        car_miles_data = []
        for reading in all_CarMiles_data:
            if reading.reading_date.year == year:
                # Will replace the 0 with the VMT value in the next for loop
                car_miles_data.append([str(reading.reading_date.month - 1), 0])

        this_year_car_miles_line_data.append(car_miles_data)

        car_miles_line_data.append(this_year_car_miles_line_data)

    # Need to remove the last month
    car_miles_line_data[-1][2].pop()

    # logger.info("car_miles_line_data")
    # logger.info(car_miles_line_data)

    # At this point, we have [['2020', 'rgba(0, 200, 0, 1)', [['0', 0], ['1', 0], ['2', 0], ['3', 0],
    # ['4', 0], ['5', 0], ['6', 0], ['7', 0], ['8', 0], ['9', 0], ['10', 0],
    # ['11', 0]]], ['2021', 'rgba(200, 0, 0, 1)', [['0', 0], ['1', 0], ['2', 0], ['3', 0]]]]
    # Need to change odometer_reading to VMT for the month
    for year_count, year in enumerate(car_miles_line_data):
        for month_count, month in enumerate(year[2]):
            month[1] = VMT[year_count * 12 + month_count]

    # Zipping a list of all readings, all_CarMiles_data, with a new list of just the VMTs from VMT_car_miles_line_data
    just_VMTs = []
    for year in car_miles_line_data:
        for month in year[2]:
            just_VMTs.append(month[1])
    # logger.info(car_miles_line_data)

    table_data = zip(all_CarMiles_data, just_VMTs)

    return render(request, "miles.html", {"title": title,
                                          "measurement": measurement,
                                          "data": car_miles_line_data,
                                          "table_data": table_data})
