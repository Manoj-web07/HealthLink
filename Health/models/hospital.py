import requests
from django.db import models
from django.core.exceptions import ValidationError
from .facility import Facility


class Hospital(models.Model):
    HOSPITAL_TYPES = [
        ('hospital', 'Hospital'),
        ('clinic', 'Clinic'),
    ]
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=500, help_text="Full address of the hospital")
    hospital_type = models.CharField(max_length=10, choices=HOSPITAL_TYPES, default='hospital')
    contact_number = models.CharField(max_length=15, blank=True, null=True, help_text="Contact number")
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='patients/profile_pictures/', blank=True, null=True)
    established_date = models.DateField(null=True, blank=True, help_text="Date of establishment")
    is_active = models.BooleanField(default=True, help_text="Is the hospital currently operational?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    password = models.CharField(max_length=128)
    # Relationship with Departments
    departments = models.ManyToManyField('Department', blank=True, related_name='hospitals')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    # Facilities offered by the hospital
    hospital_facilities = models.ManyToManyField(Facility, blank=True, related_name='hospitals')

    def save(self, *args, **kwargs):
        if self.address and (not self.latitude or not self.longitude):
            self._get_coordinates_from_address()
        super().save(*args, **kwargs)

    def _get_coordinates_from_address(self):
        """Fetch latitude & longitude using OpenStreetMap (Nominatim)."""
        url = f"https://nominatim.openstreetmap.org/search?q={self.address}&format=json"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})

        if response.status_code == 200:
            data = response.json()
            if data:
                self.latitude = float(data[0]['lat'])
                self.longitude = float(data[0]['lon'])
            else:
                raise ValidationError(f"Could not find coordinates for: {self.address}")
        else:
            raise ValidationError(f"Error fetching location: {response.status_code}")

    def __str__(self):
        return self.name
