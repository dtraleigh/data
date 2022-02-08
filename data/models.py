from django.db import models


class Water(models.Model):
    submit_date = models.DateField(auto_now_add=True)
    bill_date = models.DateField(blank=True, null=True)
    service_start_date = models.DateField()
    service_end_date = models.DateField()
    avg_gallons_per_day = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        verbose_name_plural = "Water"
        ordering = ["service_start_date"]

    def get_cname(self):
        return self.__class__.__name__

    def __str__(self):
        return f"Water {self.service_start_date}-{self.service_end_date} ({self.id})"


class Electricity(models.Model):
    submit_date = models.DateField(auto_now_add=True)
    bill_date = models.DateField(blank=True, null=True)
    service_start_date = models.DateField()
    service_end_date = models.DateField()
    kWh_usage = models.IntegerField()

    class Meta:
        verbose_name_plural = "Electricity"
        ordering = ["service_start_date"]

    def get_cname(self):
        return self.__class__.__name__

    def __str__(self):
        return f"Elec {self.service_start_date}-{self.service_end_date} ({self.id})"


class Gas(models.Model):
    submit_date = models.DateField(auto_now_add=True)
    bill_date = models.DateField(blank=True, null=True)
    service_start_date = models.DateField()
    service_end_date = models.DateField()
    therms_usage = models.IntegerField()

    class Meta:
        verbose_name_plural = "Gas"
        ordering = ["service_start_date"]

    def get_cname(self):
        return self.__class__.__name__

    def __str__(self):
        return f"Gas {self.service_start_date}-{self.service_end_date} ({self.id})"


class CarMiles(models.Model):
    submit_date = models.DateField(auto_now_add=True)
    reading_date = models.DateField()
    odometer_reading = models.IntegerField()

    class Meta:
        verbose_name_plural = "Car Miles"
        ordering = ["reading_date"]

    def get_cname(self):
        return self.__class__.__name__

    def __str__(self):
        return f"Car Miles {self.reading_date} ({self.id})"
