from django.db import models
from .patient import Patient
from .doctor import Doctor
from django.utils import timezone


class Treatment(models.Model):
    STATUS_CHOICES = [
        ('Running', 'Running'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='treatments')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name='treatments')
    name = models.CharField(max_length=255)  # Treatment name (e.g., "Chemotherapy", "Physical Therapy")
    description = models.TextField(blank=True, null=True)  # Detailed description of the treatment
    start_date = models.DateField(default=timezone.now)  # Start date of the treatment
    end_date = models.DateField(blank=True, null=True)  # End date of the treatment (optional)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Running')  # Status of the treatment
    created_at = models.DateTimeField(auto_now_add=True)  # Date when the treatment record was created
    updated_at = models.DateTimeField(auto_now=True)  # Date when the treatment record was last updated

    def __str__(self):
        return f"Treatment: {self.name} for {self.patient.name} by Dr. {self.doctor.name if self.doctor else 'N/A'}"

    # Optional: Define a method to check if the treatment is currently ongoing
    def is_ongoing(self):
        return self.status == 'Running' and (self.end_date is None or self.end_date >= timezone.now().date())
