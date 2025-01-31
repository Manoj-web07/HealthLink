from django.db import models
from .doctor import Doctor
from .patient import Patient
from .hospital import Hospital

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
        ('Canceled', 'Canceled'),
        ('Rescheduled', 'Rescheduled'),
        ('No-Show', 'No-Show'),  # New status
    ]
    hospital = models.ForeignKey(
        Hospital, on_delete=models.SET_NULL, blank=True, null=True, related_name='appointments'
    )
    TREATMENT_CHOICES = [
        ('ayurveda', 'Ayurveda'),
        ('homeopathy', 'Homeopathy'),
    ]
    LOCATION_TYPE_CHOICES = [
        ('Hospital', 'Hospital'),
        ('Clinic', 'Clinic'),
    ]
    treatment_type = models.CharField(max_length=20, choices=TREATMENT_CHOICES)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateTimeField()  # Appointment date and time
    duration_minutes = models.PositiveIntegerField(default=30)  # Duration of the appointment
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Scheduled')
    reason = models.TextField(blank=True, null=True)  # Reason for the appointment
    notes = models.TextField(blank=True, null=True)  # Notes for the appointment
    location_type = models.CharField(
        max_length=10,
        choices=LOCATION_TYPE_CHOICES,
        default='Hospital',
    )  # Location of the appointment
    city = models.CharField(max_length=100)
    is_virtual = models.BooleanField(default=False)  # Virtual or in-person appointment
    created_at = models.DateTimeField(auto_now_add=True)  # Auto-generated creation time
    updated_at = models.DateTimeField(auto_now=True)  # Auto-generated update time

    # Additional Fields
    rescheduled_from = models.ForeignKey(
        'self', on_delete=models.SET_NULL, blank=True, null=True, related_name='rescheduled_appointments'
    )
    def __str__(self):
        return f"Appointment on {self.appointment_date} with Dr. {self.doctor.name} for {self.patient.name}"

    class Meta:
        ordering = ['-appointment_date']  # Latest appointments appear first
