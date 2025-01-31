from django.db import models


class Facility(models.Model):
    name = models.CharField(max_length=255, help_text="Name of the facility (e.g., ICU, Radiology, Emergency Room)")
    description = models.TextField(blank=True, null=True, help_text="A brief description of the facility")
    available_from = models.TimeField(blank=True, null=True, help_text="Start time of facility availability")
    available_until = models.TimeField(blank=True, null=True, help_text="End time of facility availability")
    is_active = models.BooleanField(default=True, help_text="Is the facility currently operational?")


    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']