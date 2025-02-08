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
    path('',views.base),
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
    path('change-password/', views.patient_password, name='change_password'),
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('appointment/', views.appointments_view, name='appointments_view'),
    path('rescheduled-appointments/', views.rescheduled_appointments_view, name='rescheduled_appointments_view'),
    path('completed-appointments/', views.completed_appointments, name='completed_appointments'),
    path('my-patients/', views.my_patients_view, name='my_patients'),
    path('running-treatments/', views.running_treatments_view, name='running_treatments'),
    path('end-treatment/<int:treatment_id>/', views.end_treatment, name='end_treatment'),
    path('past_treatments/', views.past_treatments_view, name='past_treatments'),
    path('doctor/<int:doctor_id>/', views.doctor_profile, name='doctor_profile'),
    path('doctor/edit-profile/', views.edit_doctor_profile, name='edit_doctor_profile'),
    path('change-passwords/', views.change_password, name='change_password'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT)
