from django.db import models
from .department import Department
from .hospital import Hospital
from .doctor import Doctor

class Staff(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    ROLE_CHOICES = [
        ('Nurse', 'Nurse'),
        ('Technician', 'Technician'),
        ('Administrator', 'Administrator'),
        ('Lab Assistant', 'Lab Assistant'),
        ('Security', 'Security'),
        ('Other', 'Other'),
    ]

    role = models.CharField(max_length=100, choices=ROLE_CHOICES)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='staff_members', blank=True, null=True)
    hire_date = models.DateField(help_text="Date of hire")
    is_active = models.BooleanField(default=True, help_text="Is the staff member still active?")
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, blank=True, null=True,
                               related_name='staff_associated')
    def __str__(self):
        return f"{self.name} ({self.role})"

    class Meta:
        ordering = ['name']
