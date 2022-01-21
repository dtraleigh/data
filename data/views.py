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

measurement_units = {
    "Water": "avg_gallons_per_day",
    "Electricity": "kWh_usage",
    "Gas": "therms_usage"
}


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


def get_measurements_in_year(all_data, year):
    # Returns a list of all the measurements within a given year
    this_years_values = []

    # To account for possible service start dates and end dates in different years, use the midpoint
    for measurement in all_data:
        if get_midpoint_of_dates(measurement.service_start_date, measurement.service_end_date).year == year:
            this_years_values.append(measurement)

    return this_years_values


def get_YTD_values(data, typeM):
    # YTD is the sum of measurements that have a service date in the current year
    currentYear = datetime.now().year
    currentMonth = datetime.now().month

    if typeM == "water":
        water_sum = 0
        for measurement in get_measurements_in_year(data, currentYear):
            water_sum += measurement.avg_gallons_per_day
        return water_sum
    elif typeM == "gas":
        gas_sum = 0
        for measurement in get_measurements_in_year(data, currentYear):
            gas_sum += measurement.therms_usage
        return gas_sum
    elif typeM == "elec":
        elec_sum = 0
        for measurement in get_measurements_in_year(data, currentYear):
            elec_sum += measurement.kWh_usage
        return elec_sum
    elif typeM == "VMT":
        # VMT is the difference between the most recent reading this year and the one from Jan of this year
        return CarMiles.objects.get(reading_date__year=currentYear, reading_date__month=currentMonth).odometer_reading \
                  - CarMiles.objects.get(reading_date__year=currentYear, reading_date__month=1).odometer_reading
    else:
        return None


def get_YTD_values_for_any_year(year, data):
    # Get the sum of measurements that have a service date in the year given
    currentMonth = datetime.now().month
    data_type = type(data[0]).__name__

    if data_type != "CarMiles":
        measurement_sum = 0
        all_measurements_in_year = get_measurements_in_year(data, year)
        for measurement in all_measurements_in_year[:currentMonth - 1]:
            measurement_sum += getattr(measurement, measurement_units[data_type])
        return measurement_sum
    elif data_type == "CarMiles":
        # VMT is the difference between the most recent reading this year and the one from Jan of this year
        return CarMiles.objects.get(reading_date__year=year, reading_date__month=currentMonth).odometer_reading \
                  - CarMiles.objects.get(reading_date__year=year, reading_date__month=1).odometer_reading
    else:
        return None


def get_average(lst):
    return sum(lst) / len(lst)


def home(request):
    currentYear = datetime.now().year
    all_water_data = Water.objects.all()
    all_gas_data = Gas.objects.all()
    all_elec_data = Electricity.objects.all()
    all_vmt_data = CarMiles.objects.all()

    year_to_date_values = [get_YTD_values(all_water_data, "water"),
                           get_YTD_values(all_gas_data, "gas"),
                           get_YTD_values(all_elec_data, "elec"),
                           get_YTD_values(all_water_data, "VMT")]
    prev_year_to_date_values = [get_YTD_values_for_any_year(currentYear - 1, all_water_data),
                                get_YTD_values_for_any_year(currentYear - 1, all_gas_data),
                                get_YTD_values_for_any_year(currentYear - 1, all_elec_data),
                                get_YTD_values_for_any_year(currentYear - 1, all_water_data)]

    avg_ytd_values = []

    water_years = list(set([x.service_start_date.year for x in all_water_data]))
    water_years.sort()
    del water_years[-1]
    prev_years_water_values = [get_YTD_values(all_water_data, "water") for year in water_years]
    avg_ytd_values.append(round(get_average(prev_years_water_values)))

    gas_years = list(set([y.service_start_date.year for y in all_gas_data]))
    gas_years.sort()
    del gas_years[-1]
    prev_years_gas_values = [get_YTD_values(all_gas_data, "gas") for year in gas_years]
    avg_ytd_values.append(round(get_average(prev_years_gas_values)))

    elec_years = list(set([z.service_start_date.year for z in all_elec_data]))
    elec_years.sort()
    del elec_years[-1]
    prev_years_elec_values = [get_YTD_values(all_elec_data, "elec") for year in elec_years]
    avg_ytd_values.append(round(get_average(prev_years_elec_values)))

    vmt_years = list(set([a.reading_date.year for a in all_vmt_data]))
    vmt_years.sort()
    del vmt_years[-1]
    prev_years_vmt_values = [get_YTD_values(all_vmt_data, "VMT") for year in vmt_years]
    avg_ytd_values.append(round(get_average(prev_years_vmt_values)))

    return render(request, "home.html", {"year_to_date_values": year_to_date_values,
                                         "prev_year_to_date_values": prev_year_to_date_values,
                                         "avg_ytd_values": avg_ytd_values})


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

    table_data = zip(all_CarMiles_data, VMT)

    return render(request, "miles.html", {"title": title,
                                          "measurement": measurement,
                                          "data": car_miles_line_data,
                                          "table_data": table_data})
