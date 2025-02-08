from django.db import models
from .hospital import Hospital
from .disease import Disease


class Doctor(models.Model):
    TREATMENT_CHOICES = [
        ('ayurveda', 'Ayurveda'),
        ('homeopathy', 'Homeopathy'),
        ('allopathy', 'Allopathy'),
    ]
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    CONSULTATION_TYPES = [
        ('In-person', 'In-person'),
        ('Virtual', 'Virtual'),
        ('Both', 'Both'),
    ]

    DAYS_OF_WEEK = [
        ('Mon', 'Monday'),
        ('Tue', 'Tuesday'),
        ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'),
        ('Fri', 'Friday'),
        ('Sat', 'Saturday'),
        ('Sun', 'Sunday'),
    ]

    name = models.CharField(max_length=255)  # Full name of the doctor
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    specialty = models.CharField(max_length=255)  # Doctor's specialty (e.g., Cardiologist, Dentist)
    qualification = models.CharField(max_length=255, blank=True, null=True)  # Qualifications (e.g., MBBS, MD)
    experience_years = models.PositiveIntegerField(default=0)  # Years of experience
    contact_number = models.CharField(max_length=15, blank=True, null=True)  # Contact number
    email = models.EmailField(unique=True)  # Email address
    address = models.CharField(max_length=500, blank=True, null=True, help_text="Clinic or personal address")  # Clinic or hospital address
    treatment_type = models.CharField(max_length=20, choices=TREATMENT_CHOICES)
    password = models.CharField(max_length=128)
    city = models.CharField(max_length=100, blank=True, null=True)
    consultation_type = models.CharField(max_length=10, choices=CONSULTATION_TYPES, default='Both')  # Consultation type
    availability_start_time = models.TimeField(blank=True, null=True)  # Start time of daily availability
    availability_end_time = models.TimeField(blank=True, null=True)  # End time of daily availability
    days_available = models.ManyToManyField('DayOfWeek', blank=True)  # Days available (using a separate model for flexibility)
    is_active = models.BooleanField(default=True)  # Active status of the doctor
    profile_picture = models.ImageField(upload_to='doctors/profile_pictures/', blank=True, null=True)  # Profile picture
    languages_spoken = models.ManyToManyField('Language', blank=True)  # Languages the doctor speaks (using a ManyToManyField for languages)
    about = models.TextField(blank=True, null=True)  # A brief bio or description
    social_links = models.JSONField(blank=True, null=True)  # Links to social profiles (e.g., LinkedIn)
    created_at = models.DateTimeField(auto_now_add=True)  # Record creation time
    updated_at = models.DateTimeField(auto_now=True)  # Record last updated time
    hospital = models.ForeignKey(Hospital, on_delete=models.SET_NULL, blank=True, null=True, related_name='doctors')
    diseases = models.ManyToManyField(Disease, related_name='doctors')

    def __str__(self):
        return f"Dr. {self.name} - {self.specialty}"