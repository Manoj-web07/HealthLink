from django.db import models
from .hospital import Hospital
from .patient import Patient
class HospitalFeedback(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="hospital_feedbacks")
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name="feedbacks")
    rating = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    feedback = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.hospital.name} by {self.patient.name}"

    class Meta:
        ordering = ['-date']
