from django.db import models


class DayOfWeek(models.Model):
    name = models.CharField(max_length=9, choices=[
        ('Mon', 'Monday'),
        ('Tue', 'Tuesday'),
        ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'),
        ('Fri', 'Friday'),
        ('Sat', 'Saturday'),
        ('Sun', 'Sunday'),
    ])

    def __str__(self):
        return self.name