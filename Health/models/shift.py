from django.db import models
from .staff import Staff
class Shift(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    shift_type = models.CharField(max_length=20, choices=[
        ('Morning', 'Morning'),
        ('Afternoon', 'Afternoon'),
        ('Night', 'Night')
    ])
    shift_start =  models.IntegerField(choices=[
    (9, '9:00 AM'),
    (12, '12:00 PM'),
    (15, '3:00 PM'),
    (18, '6:00 PM'),
    (21, '9:00 PM'),
])
    shift_end = models.IntegerField(choices=[
    (9, '9:00 AM'),
    (12, '12:00 PM'),
    (15, '3:00 PM'),
    (18, '6:00 PM'),
    (21, '9:00 PM'),
])
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.staff.name} - {self.shift_type} Shift"

    class Meta:
        ordering = ['shift_start']

