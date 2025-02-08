from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.utils import timezone
from django.contrib.auth import authenticate, login
from math import radians, sin, cos, sqrt, atan2
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from geopy.distance import geodesic
from django.contrib.auth.hashers import check_password, make_password
from .models import Patient, Doctor, Hospital,Appointment,City,Review, HospitalFeedback,Staff,Treatment,Disease
from django.utils.timezone import make_aware
from datetime import datetime,timedelta
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.utils.timezone import now
from django.db.models import Count
import requests
def base(request):
    return render(request, 'base.html')

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')

        # Initialize user as None
        user = None

        # Validate based on the role
        if role == 'patient':
            user = Patient.objects.filter(email=email, password=password).first()
        elif role == 'doctor':
            user = Doctor.objects.filter(email=email, password=password).first()
        elif role == 'hospital':
            user = Hospital.objects.filter(email=email, password=password).first()

        if user:
            # Save user role in session (or other relevant data)
            request.session['user_id'] = user.id
            request.session['user_role'] = role

            # Redirect based on role
            if role == 'patient':
                return redirect('Patient-Dashboard')
            elif role == 'doctor':
                return redirect('doctor_dashboard')
            elif role == 'hospital':
                return redirect('hospital_dashboard')
        else:
            messages.error(request, 'Invalid email, password, or role')

    return render(request, 'login.html')

def registration_view(request):
    if request.method == 'POST':
        # Collecting role-specific data
        role = request.POST.get('role')

        if role == 'patient':
            # Patient registration fields
            name = request.POST.get('name')
            gender = request.POST.get('gender')
            date_of_birth = request.POST.get('date_of_birth')
            blood_group = request.POST.get('blood_group')
            contact_number = request.POST.get('contact_number')
            email = request.POST.get('email')
            address = request.POST.get('address')
            password = request.POST.get('password')  # Password field for patient

            # Create a new patient
            patient = Patient(
                name=name,
                gender=gender,
                date_of_birth=date_of_birth,
                blood_group=blood_group,
                contact_number=contact_number,
                email=email,
                address=address,
                password=password
            )
            patient.save()

        elif role == 'doctor':
            # Doctor registration fields
            name = request.POST.get('name')
            gender = request.POST.get('gender')
            specialty = request.POST.get('specialty')
            qualification = request.POST.get('qualification')
            contact_number = request.POST.get('contact_number')
            email = request.POST.get('email')
            address = request.POST.get('address')
            password = request.POST.get('password')  # Password field for doctor

            # Create a new doctor
            doctor = Doctor(
                name=name,
                gender=gender,
                specialty=specialty,
                qualification=qualification,
                contact_number=contact_number,
                email=email,
                address=address,
                password=password
            )
            doctor.save()

        elif role == 'hospital':
            # Hospital registration fields
            hospital_name = request.POST.get('hospital_name')
            hospital_address = request.POST.get('hospital_address')
            contact_number = request.POST.get('contact_number')
            email = request.POST.get('email')
            password = request.POST.get('password')  # Password field for hospital

            # Create a new hospital
            hospital = Hospital(
                name=hospital_name,
                address=hospital_address,
                contact_number=contact_number,
                email=email,
                password=password
            )
            hospital.save()

        # Successful registration message
        messages.success(request, "Registration successful!")
        return redirect('login')  # Redirect to login page

    return render(request, 'registration.html')

def patient_dashboard(request):
    if 'user_id' not in request.session:
        return redirect('login')  # Redirect if the patient is not logged in

    # Fetch the patient object using session data
    try:
        patient = Patient.objects.get(id=request.session['user_id'])
    except Patient.DoesNotExist:
        return redirect('login')  # If patient doesn't exist, redirect to login

    now_time = make_aware(datetime.now())

    # Fetch appointments in the next 24 hours (today's appointments)
    appointments = Appointment.objects.filter(
        patient=patient,
        appointment_date__gte=now_time,
        appointment_date__lte=now_time + timedelta(hours=24)
    )

    # Get active treatments
    running_treatments = Treatment.objects.filter(patient=patient, status='Running')

    # Get daily health tip (assuming you have a model for it)
    # If you have a HealthTip model, fetch a random tip for the day
    # You could replace this with logic to fetch a random or daily tip
    daily_tip = "Drink 8 glasses of water for better hydration."

    # Get upcoming appointments for notifications
    upcoming_appointments = Appointment.objects.filter(
        patient=patient,
        appointment_date__gte=now_time,
    ).order_by('appointment_date')

    # Render the template with context
    context = {
        'patient': patient,
        'appointments': appointments,
        'running_treatments': running_treatments,
        'daily_tip': daily_tip,
        'upcoming_appointments': upcoming_appointments,
        'active_page': 'patient-dashboard',
    }

    return render(request, 'Patients/patient-dashboard.html', context)
def patient_appointment(request):
    # Ensure the user is logged in
    patient_id = request.session.get('user_id')
    if not patient_id:
        return redirect('login')

    try:
        # Get the logged-in patient
        patient = Patient.objects.get(id=patient_id)
        current_time = datetime.now()

        upcoming_appointments = Appointment.objects.filter(
            patient=patient, appointment_date__gte=current_time
        ).order_by('appointment_date')

    except Patient.DoesNotExist:
        return redirect('login')

    context = {
        'patient': patient,
        'appointments': upcoming_appointments,
        'active_page': 'patient-appointment',
    }
    return render(request, 'patients/patient-appointment.html', context)
def past_appointments(request):
    # Ensure the user is logged in and the 'user_id' is in the session
    patient_id = request.session.get('user_id')
    if not patient_id:
        return redirect('login')  # Redirect to the login page if not logged in

    try:
        # Get the logged-in patient by ID
        patient = Patient.objects.get(id=patient_id)

        # Get the current time
        current_time = datetime.now()

        # Query for past appointments (appointments before the current time)
        past_appointments = Appointment.objects.filter(
            patient=patient,
            appointment_date__lt=current_time
        ).order_by('-appointment_date')

    except Patient.DoesNotExist:
        # If the patient does not exist, redirect to the login page
        return redirect('login')

    context = {
        'patient':patient,
        'past_appointments': past_appointments,
        'active_page': 'past-appointments',
    }

    return render(request, 'patients/past-appointment.html', context)


def past_treatments(request):
    # Ensure the user is logged in and the 'user_id' is in the session
    if 'user_id' not in request.session:
        return redirect('login')  # Redirect to login page if not logged in

    # Fetch the patient object using session data
    try:
        patient = Patient.objects.get(id=request.session['user_id'])
    except Patient.DoesNotExist:
        return redirect('login')  # Redirect if patient doesn't exist

    # Get the current time
    now_time = make_aware(datetime.now())

    # Fetch past treatments (treatments where the end_date is before the current time)
    past_treatments = Treatment.objects.filter(
        patient=patient,
        end_date__lt=now_time
    ).order_by('-end_date')

    context = {
        'patient': patient,
        'past_treatments': past_treatments,
        'active_page': 'past-treatments',  # Optional, if you have a navbar or active page indicator
    }

    return render(request, 'patients/past-treatments.html', context)

def patient_profile(request):
    patient_id = request.session.get('user_id')
    if not patient_id:
        return redirect('login')
    patient = Patient.objects.get(id=patient_id)

    context = {
        'patient': patient,
        'active_page': 'settings',
    }

    return render(request, 'patients/profile.html', context)


@login_required
def edit_profile(request):
    # Fetch patient using user_id stored in the session
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please log in to access this page.")
        return redirect('login')

    # Retrieve the Patient object or return 404 if not found
    patient = Patient.objects.get(id=user_id)

    if request.method == 'POST':
        # Update patient details from the form
        patient.name = request.POST.get('name', patient.name)
        patient.gender = request.POST.get('gender', patient.gender)
        patient.date_of_birth = request.POST.get('date_of_birth', patient.date_of_birth)
        patient.contact_number = request.POST.get('contact_number', patient.contact_number)
        patient.email = request.POST.get('email', patient.email)
        patient.address = request.POST.get('address', patient.address)
        patient.allergies = request.POST.get('allergies', patient.allergies)
        patient.weight = request.POST.get('weight', patient.weight)
        patient.height = request.POST.get('height', patient.height)
        patient.smoking_status = request.POST.get('smoking_status') == 'on'
        patient.drinking_status = request.POST.get('drinking_status') == 'on'
        patient.languages_spoken = request.POST.get('languages_spoken', patient.languages_spoken)

        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            patient.profile_picture = request.FILES['profile_picture']

        # Save changes to the database
        patient.save()
        messages.success(request, "Your profile has been updated successfully.")
        return redirect('patient_profile')

    # Render the edit profile template
    context = {
        'patient': patient,
        'active_page': 'settings',
    }
    return render(request, 'Patients/edit_profile.html', context)


def doctor_listing(request):
    city_name = request.GET.get("city", "").strip()
    nearby = request.GET.get("nearby", "").strip()
    treatment = request.GET.get("treatment", "").strip()
    disease = request.GET.get("disease", "").strip()
    latitude = request.GET.get("latitude", None)
    longitude = request.GET.get("longitude", None)
    search_by = request.GET.get("search_by", "hospital")  # Default to 'hospital'

    patient = Patient.objects.get(id=request.session['user_id'])

    # Ensure treatment and disease are selected
    if not treatment or not disease:
        return render(request, 'Patients/doctor-listing.html', {
            'error': "Please select both treatment and disease.",
            'cities': City.objects.all(),
            'treatments': [choice[1] for choice in Doctor._meta.get_field('treatment_type').choices],
            'diseases': Disease.objects.all(),
            'patient': patient,
            'active_page': 'home',
        })

    available_treatments = [choice[1] for choice in Doctor._meta.get_field('treatment_type').choices]

    # Start filtering doctors directly and order by rating
    doctors = Doctor.objects.filter(
        treatment_type=treatment,
        diseases__name=disease
    ).order_by("-reviews")  # Highest-rated doctors first

    hospitals = Hospital.objects.all()
    selected_nearby = False

    # 🌍 Nearby Search
    if city_name == "nearby" or nearby == "1":
        if latitude and longitude:
            try:
                latitude, longitude = float(latitude), float(longitude)
                patient_location = (latitude, longitude)

                print("Fetching nearby hospitals for:", patient_location)  # Debugging Output
                nearby_hospitals = get_nearby_hospitals(patient_location)

                # Convert to QuerySet by using IDs
                hospitals = Hospital.objects.filter(id__in=[hospital.id for hospital in nearby_hospitals])

                # Apply additional filters only if hospitals exist
                if hospitals.exists():
                    hospitals = hospitals.filter(
                        doctors__treatment_type=treatment,
                        doctors__diseases__name=disease
                    ).distinct().order_by("-feedbacks")  # Order hospitals by rating

                    doctors = doctors.filter(hospital__in=hospitals).distinct().order_by("-reviews")

                selected_nearby = True
            except ValueError:
                print("Invalid latitude/longitude")  # Debugging Output
    else:
        # 🏙️ City-Based Search
        hospitals = Hospital.objects.filter(
            city__name=city_name,
            doctors__treatment_type=treatment,
            doctors__diseases__name=disease
        ).distinct().order_by("-feedbacks")  # Order hospitals by rating

        doctors = doctors.filter(hospital__city__name=city_name).distinct().order_by("-reviews")

    # 📜 Pagination
    doctor_paginator = Paginator(doctors, 10)
    hospital_paginator = Paginator(hospitals, 10)

    page_number = request.GET.get('page')
    page_obj = doctor_paginator.get_page(page_number)
    hospital_page_obj = hospital_paginator.get_page(page_number)

    # 📌 Context Data
    context = {
        'patient': patient,
        'doctors': page_obj,
        'hospitals': hospital_page_obj,
        'selected_city': city_name,
        'selected_nearby': selected_nearby,
        'cities': City.objects.all(),
        'treatments': available_treatments,
        'diseases': Disease.objects.all(),
        'search_by': search_by,
        'active_page': 'home',
    }

    return render(request, 'Patients/doctor-listing.html', context)

def get_nearby_hospitals(patient_location):
    """
    Function to return nearby hospitals within a 10 km radius.
    """
    all_hospitals = Hospital.objects.all()
    nearby_hospitals = []

    for hospital in all_hospitals:
        if hospital.latitude and hospital.longitude:
            hospital_location = (hospital.latitude, hospital.longitude)
            # Calculate distance between patient and hospital using geopy
            distance = geodesic(patient_location, hospital_location).km
            if distance <= 30:  # Limit to 10 km radius (can be adjusted)
                nearby_hospitals.append(hospital)

    # Convert list to QuerySet by using the `id__in` filter
    nearby_hospitals_queryset = Hospital.objects.filter(id__in=[hospital.id for hospital in nearby_hospitals])
    return nearby_hospitals

def hospital_detail(request, hospital_id):
    """Displays details of a hospital."""
    hospital = Hospital.objects.get(id=hospital_id)
    doctors = Doctor.objects.filter(hospital=hospital)  # Fetch doctors of this hospital

    context = {
        'hospital': hospital,
        'doctors': doctors,
        'active_page': 'home',
    }

    return render(request, 'Patients/hospital_detail.html', context)


def doctor_detail(request, doctor_id):
    """Displays details of a doctor."""
    doctor = Doctor.objects.get(id=doctor_id)

    context = {
        'doctor': doctor,
        'active_page': 'home',
    }

    return render(request, 'Patients/doctor_detail.html', context)

def patient_password(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please log in first.")
        return redirect('login')

    try:
        patient = Patient.objects.get(id=user_id)
    except Patient.DoesNotExist:
        messages.error(request, "Patient not found.")
        return redirect('login')

    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Check if the current password is correct
        if check_password(current_password, patient.password):
            if new_password == confirm_password:
                patient.password = make_password(new_password)  # Hash the new password
                patient.save()

                # Optionally log the patient out after password change
                request.session.flush()  # Clears session
                messages.success(request, "Your password has been changed successfully. Please log in again.")
                return redirect('login')
            else:
                messages.error(request, "New password and confirmation do not match.")
        else:
            messages.error(request, "Current password is incorrect.")

    return render(request, 'Patients/patient_password.html', {'patient': patient, 'active_page': 'settings'})

def doctor_dashboard(request):
    # Ensure the user is logged in
    if 'user_id' not in request.session:
        return redirect('login')  # Redirect to login page if the doctor is not logged in

    # Fetch the doctor object from session data using the 'user_id' stored in session
    try:
        doctor = Doctor.objects.get(id=request.session['user_id'])
    except Doctor.DoesNotExist:
        return redirect('login')  # If doctor does not exist, redirect to login

    # Get the current time and make it timezone-aware
    now_time = make_aware(datetime.now())

    # Fetch dashboard data for the doctor
    # Get the count of upcoming appointments for the doctor (appointments with date >= now)
    upcoming_appointments = Appointment.objects.filter(doctor=doctor, appointment_date__gte=now_time).count()

    # Get the count of new patients in the last 30 days
    new_patients = Patient.objects.filter(created_at__gte=now_time - timedelta(days=30)).count()

    # Get the count of all appointments attended by the doctor (total patients attendance)
    total_patients_attendance = Appointment.objects.filter(doctor=doctor).count()

    # Get the count of distinct patients who have attended appointments with the doctor
    total_distinct_patients = Appointment.objects.filter(doctor=doctor).values('patient').distinct().count()

    # Fetch the reviews given to the doctor
    reviews = Review.objects.filter(doctor=doctor)
    review_count = reviews.count()  # Total number of reviews

    # Calculate the average rating for the doctor, ensuring it's 0 if no reviews
    average_rating = round(sum([r.rating for r in reviews]) / review_count, 2) if review_count > 0 else 0

    # Prepare the distribution of ratings (1-5 stars) for Chart.js visualization
    rating_distribution = {
        "5 Stars": reviews.filter(rating=5).count(),
        "4 Stars": reviews.filter(rating=4).count(),
        "3 Stars": reviews.filter(rating=3).count(),
        "2 Stars": reviews.filter(rating=2).count(),
        "1 Star": reviews.filter(rating=1).count(),
    }
    patient_comments = reviews.values('patient__name', 'comment','created_at')

    # Convert the rating distribution to JSON format to pass to Chart.js
    rating_distribution_json = json.dumps(rating_distribution)

    # Prepare the context to pass to the template
    context = {
        "doctor": doctor,  # The doctor object
        "upcoming_appointments": upcoming_appointments,  # Count of upcoming appointments
        "new_patients": new_patients,  # Count of new patients in the last 30 days
        "total_patients_attendance": total_patients_attendance,  # Total number of appointments attended
        "total_distinct_patients": total_distinct_patients,  # Total distinct patients
        "average_rating": average_rating,  # Average rating of the doctor
        "review_count": review_count,  # Number of reviews
        "rating_distribution": rating_distribution,  # Rating distribution for Chart.js
        "patient_comments": patient_comments,
        "rating_distribution_json": rating_distribution_json,  # Rating distribution in JSON format
        "active_page": "doctor-dashboard",  # To highlight the active page in the navigation bar
    }

    # Render the template with the context data
    return render(request, "Doctors/doctor-dashboard.html", context)

def appointments_view(request):
    # Ensure the doctor is logged in
    if 'user_id' not in request.session:
        return redirect('login')  # Redirect to login if not authenticated

    try:
        doctor = Doctor.objects.get(id=request.session['user_id'])  # Fetch doctor
    except Doctor.DoesNotExist:
        return redirect('login')  # Handle invalid doctor cases

    now_time = make_aware(datetime.now())  # Get current timezone-aware time

    # Fetch upcoming appointments sorted by appointment date
    upcoming_appointments = Appointment.objects.filter(
        doctor=doctor, status='Scheduled'
    ).order_by('appointment_date')

    context = {
        "doctor": doctor,
        "upcoming_appointments": upcoming_appointments,
        "now_time": now_time,  # Pass current time for template logic
        "active_page": "appointments",  # Highlight 'Appointments' in navigation
    }

    return render(request, "Doctors/appointments.html", context)

def rescheduled_appointments_view(request):
    # Ensure the doctor is logged in
    if 'user_id' not in request.session:
        return redirect('login')  # Redirect to login if not authenticated

    try:
        doctor = Doctor.objects.get(id=request.session['user_id'])  # Fetch doctor
    except Doctor.DoesNotExist:
        return redirect('login')  # Handle invalid doctor cases

    now_time = make_aware(datetime.now())  # Get current timezone-aware time

    # Fetch rescheduled appointments sorted by appointment date
    rescheduled_appointments = Appointment.objects.filter(
        doctor=doctor, status="rescheduled"
    ).order_by('appointment_date')

    context = {
        "doctor": doctor,
        "rescheduled_appointments": rescheduled_appointments,
        "now_time": now_time,
        "active_page": "rescheduled_appointments",  # Highlight 'Rescheduled Appointments' menu
    }

    return render(request, "Doctors/rescheduled_appointments.html", context)

def completed_appointments(request):
    if 'user_id' not in request.session:
        return redirect('login')  # Redirect if the doctor is not logged in

    doctor = Doctor.objects.get(id=request.session['user_id'])  # Get doctor object
    now_time = make_aware(datetime.now())  # Current timezone-aware time

    # Fetch only completed appointments
    completed_appointments = Appointment.objects.filter(doctor=doctor, status='Completed').order_by('-appointment_date')

    context = {
        "doctor": doctor,
        "completed_appointments": completed_appointments,
        'active_page': "appointment-records",
    }

    return render(request, 'Doctors/completed_appointments.html', context)
def my_patients_view(request):
    if 'user_id' not in request.session:
        return redirect('login')  # Redirect if not logged in

    doctor = Doctor.objects.get(id=request.session['user_id'])  # Get doctor

    # Get all patients who have had an appointment with this doctor
    patients = Patient.objects.filter(appointments__doctor=doctor).distinct()

    context = {
        "doctor": doctor,
        "my_patients": patients,
        'active_page': "my-patients",
    }

    return render(request, 'Doctors/my_patients.html', context)
def running_treatments_view(request):
    if 'user_id' not in request.session:
        return redirect('login')  # Redirect if the doctor is not logged in

    doctor = Doctor.objects.get(id=request.session['user_id'])  # Get doctor by session ID
    now_time = timezone.now().date()  # Get current date (timezone-aware)

    # Fetch treatments that are running (status = 'Running' and end date is either null or in the future)
    running_treatments = Treatment.objects.filter(
        doctor=doctor,
        status='Running',
        end_date__gte=now_time  # Treatment still running (either no end date or in the future)
    ).order_by('start_date')

    context = {
        'doctor': doctor,
        'running_treatments': running_treatments,
        'active_page': "running_treatments",
    }

    return render(request, 'Doctors/running_treatments.html', context)
def end_treatment(request, treatment_id):
    # Ensure the user is logged in and a doctor (optional check based on your logic)
    if 'user_id' not in request.session:
        return redirect('login')  # Redirect to login page if the doctor is not logged in

    # Fetch the treatment object by ID
    treatment = Treatment.objects.get(id=treatment_id)

    # Update the treatment's end_date to the current date and status to 'Completed'
    treatment.end_date = timezone.now().date()
    treatment.status = 'Completed'
    treatment.save()  # Save the updated treatment

    # Redirect back to the running treatments page
    return redirect('running_treatments')
def past_treatments_view(request):
    if 'user_id' not in request.session:
        return redirect('login')  # Redirect to login page if the doctor is not logged in

    doctor = Doctor.objects.get(id=request.session['user_id'])  # Get doctor by session ID
    now_time = timezone.now().date()  # Get current date (timezone-aware)

    # Fetch treatments that are completed
    past_treatments = Treatment.objects.filter(
        doctor=doctor,
        status='Completed',
        end_date__lte=now_time  # Completed treatments with end date in the past
    ).order_by('-end_date')  # Order by most recent completed treatment

    context = {
        'doctor': doctor,
        'past_treatments': past_treatments,
        'active_page': "treatments-records",

    }

    return render(request, 'Doctors/past_treatments.html', context)


def doctor_profile(request, doctor_id):
    if 'user_id' not in request.session:
        return redirect('login')

    # Fetch the doctor object
    doctor = Doctor.objects.get(id=doctor_id)
    diseases = doctor.diseases.all()
    context = {
        'doctor': doctor,
        'diseases': diseases,
        'active_page': "settings"
    }

    return render(request, 'Doctors/doctor_profile.html', context)
def edit_doctor_profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please log in to access this page.")
        return redirect('login')

    # Retrieve the doctor object
    doctor = Doctor.objects.get(id=user_id)
    diseases = Disease.objects.all()

    if request.method == 'POST':
        doctor.name = request.POST.get('name', doctor.name)
        doctor.gender = request.POST.get('gender', doctor.gender)
        doctor.contact_number = request.POST.get('contact_number', doctor.contact_number)
        doctor.email = request.POST.get('email', doctor.email)
        doctor.address = request.POST.get('address', doctor.address)
        doctor.city = request.POST.get('city', doctor.city)
        doctor.specialty = request.POST.get('specialty', doctor.specialty)
        doctor.qualification = request.POST.get('qualification', doctor.qualification)
        doctor.experience_years = request.POST.get('experience_years', doctor.experience_years)
        doctor.about = request.POST.get('about', doctor.about)

        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            doctor.profile_picture = request.FILES['profile_picture']
        selected_disease_ids = request.POST.getlist('diseases')
        doctor.diseases.set(selected_disease_ids)

        doctor.save()
        messages.success(request, "Your profile has been updated successfully.")
        return redirect('doctor_profile', doctor_id=doctor.id)

    context = {
        'doctor': doctor,
        'diseases': diseases,
        'active_page': 'settings',
    }
    return render(request, 'Doctors/edit_profile.html', context)
def change_password(request):
    if 'user_id' not in request.session:
        messages.error(request, "Please log in first.")
        return redirect('login')

    doctor = Doctor.objects.filter(id=request.session['user_id']).first()
    if not doctor:
        messages.error(request, "Doctor not found.")
        return redirect('login')

    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Directly compare stored password (NOT RECOMMENDED if hashed)
        if current_password != doctor.password:
            messages.error(request, "Current password is incorrect.")
        elif new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
        else:
            doctor.password = new_password  # ⚠️ Plain text storage (Not Secure)
            doctor.save()
            request.session.flush()  # Log out user after changing password
            messages.success(request, "Password changed successfully. Please log in again.")
            return redirect('login')

    return render(request, 'Doctors/change_password.html', {'doctor': doctor, 'active_page': 'settings'})