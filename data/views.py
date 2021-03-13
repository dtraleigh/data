from django.shortcuts import render


def home(request):
    colors = ["rgba(0, 200, 0, 1)",         # Green
              "rgba(200, 0, 0, 1)",         # Red
              "rgba(191, 63, 148, 1)",      # Magenta
              "rgba(20, 23, 234, 1)",       # Blue
              "rgba(234, 173, 20, 1)",      # Orange
              "rgba(154, 101, 54, 1)",      # Brown
              "rgba(172, 243, 118, 1)",     # light green
              "rgba(101, 54, 154, 1)",      # Purple
              "rgba(172, 243, 118, 1)",     # dark green
              "rgba(246, 223, 141, 1)",     # Tan
              "rgba(246, 223, 141, 1)"      # pink
              ]

    return render(request, "home.html", {"colors": colors})


def water(request):

    return render(request, "base.html", {})


def gas(request):

    return render(request, "base.html", {})


def electricity(request):

    return render(request, "base.html", {})


def car_gas(request):

    return render(request, "base.html", {})


def car_miles(request):

    return render(request, "base.html", {})
