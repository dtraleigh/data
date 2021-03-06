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


def requested_years_to_use(years_range, data_class):
    """use the years from the request else, use this year and last. Also, account for some special keywords"""
    if not years_range:
        return str(datetime.now().year - 2) + "-" + str(datetime.now().year)
    elif years_range.lower() == "all":
        return f"{str(get_earliest_year_from_data(data_class))}-{str(get_most_recent_year_from_data(data_class))}"
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


def get_measurement_data_from_years(data_name, years_range):
    """Returns a list of datapoints per the years given in the range. Sorting is model default"""
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
    """Template ["label", "color", "borderWidth", [["9", 46.8], ...]]"""
    if all_data:
        data_type = type(all_data[0]).__name__

        line_data = []
        for count, year in enumerate(years):
            this_year_line_data = []
            this_year_line_data.append(str(year))
            this_year_line_data.append(colors[count])
            this_year_line_data.append(2)

            data = []
            for bill in all_data:
                midpoint_date = get_midpoint_of_dates(bill.service_start_date, bill.service_end_date)
                if midpoint_date.year == year:
                    data.append([str(midpoint_date.month - 1), getattr(bill, measurement_units[data_type])])

            this_year_line_data.append(data)

            line_data.append(this_year_line_data)

        return line_data
    else:
        return None


def get_most_recent_year_from_data(data_name):
    data_class = apps.get_model(app_label="data", model_name=data_name)
    if data_name != "CarMiles":
        return data_class.objects.latest("service_start_date").service_start_date.year
    else:
        return data_class.objects.latest("reading_date").reading_date.year


def get_earliest_year_from_data(data_name):
    data_class = apps.get_model(app_label="data", model_name=data_name)
    if data_name != "CarMiles":
        return data_class.objects.earliest("service_start_date").service_start_date.year
    else:
        return data_class.objects.earliest("reading_date").reading_date.year


def create_avg_line_data(class_name):
    """Template ["label", "color", "borderWidth", [["9", 46.8], ...]]"""
    data_class = apps.get_model(app_label="data", model_name=class_name)

    recent_year = get_most_recent_year_from_data(class_name)
    first_year = get_earliest_year_from_data(class_name)

    avg_line_data_complete = []
    avg_line_data_complete.append(f"Average ({str(first_year)}-{str(recent_year-1)})")
    avg_line_data_complete.append("rgba(22, 51, 73, 0.1)")
    avg_line_data_complete.append(5)

    if class_name != "CarMiles":
        # Data from first_year to recent_year - 1
        all_data_for_avg_line = data_class.objects.filter(service_start_date__year__gte=first_year,
                                                          service_start_date__year__lt=recent_year)
        all_month_data = []
        # Go through each month of each year
        for month in range(1, 13):
            month_data_objects = [x for x in all_data_for_avg_line if get_midpoint_of_dates(x.service_start_date, x.service_end_date).month == month]
            month_data = [getattr(y, measurement_units[class_name]) for y in month_data_objects]
            avg = get_average(month_data)
            all_month_data.append([f"{str(month - 1)}", avg])

        avg_line_data_complete.append(all_month_data)

        return avg_line_data_complete
    else:
        # Data from first_year to recent_year - 1
        all_data_for_avg_line = data_class.objects.filter(reading_date__year__gte=first_year,
                                                          reading_date__year__lt=recent_year)

        all_month_data = []
        # Go through each month of each year
        for month in range(1, 13):
            month_data_objects = [x for x in all_data_for_avg_line if x.reading_date.month == month]
            month_data = [get_VMT_calculation(y) for y in month_data_objects]
            avg = get_average(month_data)
            all_month_data.append([f"{str(month - 1)}", avg])

        avg_line_data_complete.append(all_month_data)

        return avg_line_data_complete


def get_VMT_calculation(datapoint):
    """With any datapoint from CarMiles, return the VMT for that month. If you pass the most recent datapoint, we
    can't calculate VMT. Ex: VMT for Feb = March Reading - Feb Reading. Readings are always taken on 1st of month"""
    try:
        if datapoint.reading_date.month == 12:
            next_months_datapoint = CarMiles.objects.get(reading_date__year=datapoint.reading_date.year + 1,
                                                         reading_date__month=1)
        else:
            next_months_datapoint = CarMiles.objects.get(reading_date__year=datapoint.reading_date.year,
                                                         reading_date__month=datapoint.reading_date.month + 1)
        return next_months_datapoint.odometer_reading - datapoint.odometer_reading
    except CarMiles.DoesNotExist:
        return None


def create_car_line_data(years, all_data, VMT):
    """ Example:
    [['2021', 'rgba(0, 200, 0, 1)', 2, [['0', 0], ['1', 0], ['2', 0], ['3', 0], ['4', 0], ['5', 0], ['6', 0], ['7', 0],
    ['8', 0], ['9', 0], ['10', 0], ['11', 0]]], ['2022', 'rgba(200, 0, 0, 1)', 2, [['0', 0], ['1', 0], ['2',
    0]]]] car_miles_line_data: [['2021', 'rgba(0, 200, 0, 1)', [['0', 550], ['1', 1203], ['2', 1722], ['3', 1864],
    ['4', 1808], ['5', 1302], ['6', 2499], ['7', 1461], ['8', 741], ['9', 1508], ['10', 785], ['11', 1592]]],
    ['2022', 'rgba(200, 0, 0, 1)', 2, [['0', 391], ['1', 896]]]]
    """
    if all_data:
        line_data = []
        for count, year in enumerate(years):
            this_year_line_data = []
            this_year_line_data.append(str(year))
            this_year_line_data.append(colors[count])
            this_year_line_data.append(2)

            data = []
            for reading in all_data:
                if reading.reading_date.year == year:
                    vmt_calculated_value = get_VMT_calculation(reading)
                    if vmt_calculated_value:
                        data.append([str(reading.reading_date.month - 1), vmt_calculated_value])

            this_year_line_data.append(data)
            line_data.append(this_year_line_data)

        return line_data
    else:
        return None
