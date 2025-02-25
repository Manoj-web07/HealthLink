"""
URL configuration for HealthLink project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Health import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('Base/',views.base,name='base'),
    path('',views.intro, name='intro'),
    path('Login/', views.user_login, name='login'),
    path('register/', views.registration_view, name='registration'),
    path('patient/dashboard/', views.patient_dashboard, name='Patient-Dashboard'),
    path('appointments/', views.patient_appointment, name='patient_appointments'),
    path('past-appointments/', views.past_appointments, name='past_appointments'),
    path('past-treatments/', views.past_treatments, name='past_treatments'),
    path('profile/', views.patient_profile, name='patient_profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('doctor-listing/', views.doctor_listing, name='doctor_listing'),
    path('hospital/<int:hospital_id>/', views.hospital_detail, name='hospital_detail'),
    path('doctors/<int:doctor_id>/', views.doctor_detail, name='doctor_detail'),
    path('patient/change-password/', views.patient_password, name='patient_change_password'),
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/<int:doctor_id>/comments/', views.doctor_comments, name='doctor_comments'),
    path('appointment/', views.appointments_view, name='appointments_view'),
    path('rescheduled-appointments/', views.rescheduled_appointments_view, name='rescheduled_appointments_view'),
    path('completed-appointments/', views.completed_appointments, name='completed_appointments'),
    path('my-patients/', views.my_patients_view, name='my_patients'),
    path('running-treatments/', views.running_treatments_view, name='running_treatments'),
    path('end-treatment/<int:treatment_id>/', views.end_treatment, name='end_treatment'),
    path('past_treatments/', views.past_treatments_view, name='past_treatment'),
    path('doctor/<int:doctor_id>/', views.doctor_profile, name='doctor_profile'),
    path('doctor/edit-profile/', views.edit_doctor_profile, name='edit_doctor_profile'),
    path('search_hospitals/', views.search_hospitals, name='search_hospitals'),
    path('search_cities/', views.search_cities, name='search_cities'),
    path('add_city/', views.add_city, name='add_city'),
    path('add_disease/', views.add_disease, name='add_disease'),
    path('change-passwords/', views.change_password, name='change_password'),
    path('hospital-dashboard/', views.hospital_dashboard, name='hospital_dashboard'),
    path('submit-appointment/', views.submit_appointment_request, name='submit_appointment_request'),
    path('appointments/upcoming/', views.upcoming_appointments, name='upcoming_appointments'),
    path('attend/<int:appointment_id>/', views.attend, name='attend'),
    path('appointments/approve/<int:appointment_id>/', views.approve_appointment, name='approve_appointment'),
    path('appointments/requests/', views.appointment_requests, name='appointments-request'),
    path('cancel-appointment/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('appointments/reschedule/<int:appointment_id>/', views.reschedule_appointment, name='reschedule_appointment'),
    path('doctor/appointments/reschedule/<int:appointment_id>/', views.doctor_reschedule_appointment, name='doctor_reschedule_appointment'),
    path('appointments/cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointments'),
    path('doctor/appointments/cancel/<int:appointment_id>/', views.doctor_cancel_appointment, name='doctor_cancel_appointment'),
    path('reschedule-requests/', views.rescheduled_requests, name='reschedule_request'),
    path('appointments/reschedules/<int:appointment_id>/', views.rescheduled_appointments, name='rescheduled_appointments'),
    path('doctors_page/', views.doctors_page, name='doctors_page'),
    path('doctor_page/<int:doctor_id>/', views.view_doctor, name='view_doctors'),
    path('doctor/toggle-status/<int:doctor_id>/', views.toggle_doctor_status, name='toggle_doctor_status'),
    path('staff/', views.staff_list, name='staff_list'),
    path('staff/add/', views.add_staff, name='add_staff'),
    path('staff/edit/<int:staff_id>/', views.edit_staff, name='edit_staff'),
    path('staff/toggle_status/<int:staff_id>/', views.toggle_staff_status, name='toggle_staff_status'),
    path('delete_staff/<int:staff_id>/', views.delete_staff, name='delete_staff'),
    path('departments/', views.department_list, name='department_list'),
    path('facilities/', views.facility_list, name='facility_list'),
    path('completed-appointment/', views.completed_appointment, name='completed_appointment'),
    path('running-treatment/', views.running_treatments, name='running_treatment'),
    path('treatment/records/', views.treatments_record, name='treatment_records'),
    path('hospitals/<int:hospital_id>/', views.hospital_profile, name='hospital-profile'),
    path('hospital/edit/', views.edit_hospital_profile, name='edit_hospital_profile'),
    path('hospital/passwords/', views.change_hospital_password, name='change_hospital_password'),
    path('logout/', views.logout, name='logout'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact_us, name='contact_us'),
    path('submit_review_or_feedback/', views.submit_review_or_feedback, name='submit_review_or_feedback'),

    path('reviews/', views.reviews, name='reviews')
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT)
