from django.db import models
from .patient import Patient
from .doctor import Doctor  # Import your Doctor model
from django.core.exceptions import ValidationError


class Review(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="reviews")
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])  # Ratings from 1 to 5
    comment = models.TextField(blank=True, null=True)  # Optional comment
    created_at = models.DateTimeField(auto_now_add=True)  # When the review was created
    updated_at = models.DateTimeField(auto_now=True)  # When the review was last updated
    read = models.BooleanField(default=False)
    class Meta:
        unique_together = ('doctor', 'patient')  # Ensures a patient can review a doctor only once

    def __str__(self):
        return f"Review for Dr. {self.doctor.name} by {self.patient.name}"

    # Custom validation to ensure rating is between 1 and 5
    def clean(self):
        if not (1 <= self.rating <= 5):
            raise ValidationError("Rating must be between 1 and 5.")

    # Optionally, we can add a method to calculate the average rating for a doctor
    @staticmethod
    def get_average_rating(doctor):
        reviews = doctor.reviews.all()
        total_rating = sum(review.rating for review in reviews)
        return total_rating / len(reviews) if reviews else 0


