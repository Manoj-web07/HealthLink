from django.db import models
class Department(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True, help_text="Details about the department")
    head_of_department = models.CharField(max_length=255, blank=True, null=True, help_text="Name of the head of department")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Departments"
