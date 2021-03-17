from django.shortcuts import render
from data.models import *
import logging, json

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


def get_years(object_data):
    # Returns a sorted list of years found across all service dates
    dataset_years = []

    for datapoint in object_data:
        dataset_years.append(datapoint.service_start_date.year)
        dataset_years.append(datapoint.service_end_date.year)

    dataset_years = list(set(dataset_years))
    dataset_years.sort()

    return dataset_years


def home(request):

    return render(request, "home.html", {"colors": colors})


def water(request):
    title = "Water"
    all_water_data = Water.objects.all()
    years = get_years(all_water_data)

    year_and_colors = zip(years, colors)

    return render(request, "page.html", {"title": title,
                                         "years": years,
                                         "colors": colors,
                                         "year_and_colors": year_and_colors
                                         })


def gas(request):

    return render(request, "base.html", {})


def electricity(request):

    return render(request, "base.html", {})


def car_gas(request):

    return render(request, "base.html", {})


def car_miles(request):

    return render(request, "base.html", {})
