from django.contrib import admin
from .models import Appointment
from .models import Hospital, Department, Staff, Patient, DayOfWeek, Doctor, HospitalFeedback, Language, Shift, Review, Facility, Disease, Treatment,City

# Register your models here.

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('appointment_date', 'doctor', 'patient', 'status', 'is_virtual', 'hospital')
    list_filter = ('status', 'doctor', 'patient', 'is_virtual', 'hospital')
    search_fields = ('doctor__name', 'patient__name', 'hospital__name', 'reason')
    date_hierarchy = 'appointment_date'
    ordering = ['-appointment_date']  # Ensure the most recent appointments are listed first
    raw_id_fields = ('doctor', 'patient', 'hospital')  # To make foreign keys more manageable
    readonly_fields = ('created_at', 'updated_at')  # Make sure these fields are not editable in the admin panel

    # Optionally, you could add custom actions for rescheduling or changing statuses
    def mark_completed(self, request, queryset):
        queryset.update(status='Completed')

    def mark_canceled(self, request, queryset):
        queryset.update(status='Canceled')

    actions = [mark_completed, mark_canceled]

admin.site.register(Appointment, AppointmentAdmin)

class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialty', 'hospital', 'city', 'experience_years', 'consultation_type', 'is_active')
    list_filter = ('treatment_type', 'hospital', 'is_active')
    search_fields = ('name', 'specialty', 'hospital__name', 'email', 'city',)
    ordering = ('name',)
    filter_horizontal = ('diseases', 'languages_spoken', 'days_available')

    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'gender', 'specialty', 'qualification', 'experience_years', 'contact_number', 'email', 'address', 'city', 'profile_picture')
        }),
        ('Professional Details', {
            'fields': ('hospital', 'treatment_type', 'consultation_type', 'languages_spoken', 'diseases')
        }),
        ('Consultation Details', {
            'fields': ('availability_start_time', 'availability_end_time', 'days_available')
        }),
        ('System Information', {
            'fields': ('password', 'is_active', 'created_at', 'updated_at')
        }),
    )

    readonly_fields = ('created_at', 'updated_at')  # Makes the timestamps read-only

    def get_queryset(self, request):
        """Optimize queries by prefetching related fields."""
        return super().get_queryset(request).select_related('hospital').prefetch_related('languages_spoken', 'diseases', 'days_available')

    def password(self, obj):
        """Display password as a secure field (hashed version)."""
        return obj.password if obj.password else "Not Set"

# Register the models with the Django admin
admin.site.register(Doctor, DoctorAdmin)
admin.site.register(Disease)
admin.site.register(Language)
admin.site.register(DayOfWeek)

class DepartmentInline(admin.TabularInline):
    model = Hospital.departments.through
    extra = 1

class FacilityInline(admin.TabularInline):
    model = Hospital.hospital_facilities.through
    extra = 1
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'contact_number', 'city','email', 'is_active', 'established_date')
    list_filter = ('is_active', 'established_date')
    search_fields = ('name', 'address', 'email')
    filter_horizontal = ('departments', 'hospital_facilities')  # Only for Many-to-Many fields
    ordering = ['name']

admin.site.register(Hospital, HospitalAdmin)


class HospitalFeedbackAdmin(admin.ModelAdmin):
    list_display = ('hospital', 'patient', 'rating', 'date')
    list_filter = ('hospital', 'rating')
    search_fields = ('hospital__name', 'patient__name', 'feedback')
    ordering = ['-date']

admin.site.register(HospitalFeedback, HospitalFeedbackAdmin)

class PatientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'contact_number', 'date_of_birth', 'blood_group')
    search_fields = ('name', 'email', 'contact_number')
    list_filter = ('blood_group', 'gender')

admin.site.register(Patient, PatientAdmin)

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'patient', 'rating', 'created_at')  # Display key fields in the list view
    list_filter = ('rating', 'created_at')  # Allow filtering by rating and creation date
    search_fields = ('doctor__name', 'patient__name')  # Allow searching by doctor and patient names
    ordering = ['-created_at']  # Order reviews by most recent first

    # Optionally, make 'comment' field editable in the admin list
    list_editable = ('rating',)

    # Optionally, add inline editing for reviews (if necessary)
    fieldsets = (
        (None, {
            'fields': ('doctor', 'patient', 'rating', 'comment')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')  # Make created_at and updated_at readonly

admin.site.register(Review, ReviewAdmin)


class ShiftAdmin(admin.ModelAdmin):
    # Display fields in the list view
    list_display = ('staff', 'shift_type', 'shift_start', 'shift_end', 'is_active')

    # Filters to narrow down the data
    list_filter = ('shift_type', 'is_active')

    # Add search functionality for staff name
    search_fields = ('staff__name',)

    # Add filtering by active status
    list_editable = ('is_active',)

    # Adding ordering to display shifts in the correct order
    ordering = ('shift_start',)

    # Add inline editing options (optional)
    fieldsets = (
        (None, {
            'fields': ('staff', 'shift_type', 'shift_start', 'shift_end', 'is_active')
        }),
    )


admin.site.register(Shift, ShiftAdmin)


class StaffAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'hospital', 'department', 'doctor', 'hire_date', 'is_active')
    list_filter = ('hospital', 'department', 'is_active')
    search_fields = ('name',)  # Correct the indentation here

admin.site.register(Staff, StaffAdmin)

class TreatmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'patient', 'doctor', 'start_date', 'status', 'created_at')
    list_filter = ('status', 'doctor')
    search_fields = ('patient__name', 'doctor__name', 'name')

admin.site.register(Treatment, TreatmentAdmin)

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)