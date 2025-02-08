from django.db import models
from .doctor import Doctor
from .patient import Patient
from .hospital import Hospital
from django.utils import timezone
from django.core.exceptions import ValidationError


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
        ('Canceled', 'Canceled'),
        ('Rescheduled', 'Rescheduled'),
        ('No-Show', 'No-Show'),
    ]

    TREATMENT_CHOICES = [
        ('ayurveda', 'Ayurveda'),
        ('homeopathy', 'Homeopathy'),
        ('allopathy', 'Allopathy'),
    ]

    LOCATION_TYPE_CHOICES = [
        ('Hospital', 'Hospital'),
        ('Clinic', 'Clinic'),
    ]

    hospital = models.ForeignKey(
        Hospital, on_delete=models.SET_NULL, blank=True, null=True, related_name='appointments'
    )
    treatment_type = models.CharField(max_length=20, choices=TREATMENT_CHOICES)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments', db_index=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments', db_index=True)
    appointment_date = models.DateTimeField(db_index=True)
    duration_minutes = models.PositiveIntegerField(default=30)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Scheduled', db_index=True)
    reason = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    location_type = models.CharField(max_length=10, choices=LOCATION_TYPE_CHOICES, default='Hospital')
    city = models.CharField(max_length=100)
    is_virtual = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rescheduled_from = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True,
                                         related_name='rescheduled_appointments')

    class Meta:
        ordering = ['-appointment_date']
        unique_together = ('doctor', 'patient', 'appointment_date')  # Ensure no double-booking

    def __str__(self):
        return f"Appointment on {self.appointment_date} with Dr. {self.doctor.name} for {self.patient.name} ({self.status})"

    def clean(self):
        if self.appointment_date <= timezone.now():
            raise ValidationError("Appointment date must be in the future.")
