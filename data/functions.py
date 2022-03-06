from datetime import datetime
import operator
from django.db.models import Q
from functools import reduce

from django.apps import apps
from data.models import *

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

measurement_units = {
    "Water": "avg_gallons_per_day",
    "Electricity": "kWh_usage",
    "Gas": "therms_usage"
}


def get_years_list_from_data(object_data):
    """Returns a sorted list of years found across all service dates"""
    dataset_years = []
    if object_data:
        for datapoint in object_data:
            dataset_years.append(datapoint.service_start_date.year)
            dataset_years.append(datapoint.service_end_date.year)

        dataset_years = list(set(dataset_years))
        dataset_years.sort()

        return dataset_years
    else:
        return None


def get_midpoint_of_dates(date1, date2):
    return date1 + (date2 - date1) / 2


def requested_years_to_use(years_range):
    """use the years from the request else, use this year and last"""
    if not years_range:
        return str(datetime.now().year - 2) + "-" + str(datetime.now().year)
    return years_range


def get_measurements_in_year(all_data, year):
    """Returns a list of all the measurements within a given year"""
    this_years_values = []

    # To account for possible service start dates and end dates in different years, use the midpoint
    for measurement in all_data:
        if get_midpoint_of_dates(measurement.service_start_date, measurement.service_end_date).year == year:
            this_years_values.append(measurement)

    return this_years_values


def get_YTD_values_for_any_year(year, data):
    """Get the sum of measurements that have a service date in the year given"""
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


def get_YTD_values_for_all_years(data):
    """Get the sum of measurements that have a service date across all past years
    Does not include current year"""
    data_type = type(data[0]).__name__

    if data_type != "CarMiles":
        years = list(set([x.service_start_date.year for x in data]))
        years.sort()
        del years[-1]
        prev_years_values = [get_YTD_values_for_any_year(year, data) for year in years]
        return round(get_average(prev_years_values))
    elif data_type == "CarMiles":
        years = list(set([a.reading_date.year for a in data]))
        years.sort()
        del years[-1]
        prev_years_values = [get_YTD_values_for_any_year(year, data) for year in years]
        return round(get_average(prev_years_values))
    else:
        return None


def get_average(lst):
    return sum(lst) / len(lst)


def get_measurement_data(data_name, years_range):
    data_class = apps.get_model(app_label="data", model_name=data_name)
    years_range = years_range.replace(" ", "")

    if data_name != "CarMiles":
        if "-" in years_range:
            return data_class.objects.filter(service_start_date__year__gte=years_range.split("-")[0],
                                             service_start_date__year__lte=years_range.split("-")[1])
        elif "," in years_range:
            years = years_range.split(",")
            return data_class.objects.filter(reduce(operator.or_,
                                                    (Q(service_start_date__year__contains=y) for y in years)))
        elif "-" not in years_range and "," not in years_range:
            try:
                return data_class.objects.filter(service_start_date__year=years_range)
            except ValueError:
                return None

    else:
        if "-" in years_range:
            return CarMiles.objects.filter(reading_date__year__gte=years_range.split("-")[0],
                                           reading_date__year__lte=years_range.split("-")[1])
        elif "," in years_range:
            years = years_range.split(",")
            return data_class.objects.filter(reduce(operator.or_,
                                                    (Q(reading_date__year__contains=y) for y in years)))
        elif "-" not in years_range and "," not in years_range:
            try:
                return data_class.objects.filter(reading_date__year=years_range)
            except ValueError:
                return None


def create_line_data(years, all_data):
    """Template ["label", "color", [["2018, 9", 46.8], ...]]"""
    if all_data:
        data_type = type(all_data[0]).__name__

        line_data = []
        for count, year in enumerate(years):
            this_year_line_data = []
            this_year_line_data.append(str(year))
            this_year_line_data.append(colors[count])

            data = []
            if data_type != "CarMiles":
                for bill in all_data:
                    midpoint_date = get_midpoint_of_dates(bill.service_start_date, bill.service_end_date)
                    if midpoint_date.year == year:
                        data.append([str(midpoint_date.month - 1), getattr(bill, measurement_units[data_type])])

                this_year_line_data.append(data)

                line_data.append(this_year_line_data)
            elif data_type == "CarMiles":
                for reading in all_data:
                    if reading.reading_date.year == year:
                        # Will replace the 0 with the VMT value in the next for loop
                        data.append([str(reading.reading_date.month - 1), 0])

                this_year_line_data.append(data)

                line_data.append(this_year_line_data)

        return line_data
    else:
        return None
