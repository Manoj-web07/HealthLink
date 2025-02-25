from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.urls import reverse
from django.db import IntegrityError
from django.db.models import Q
from urllib.parse import urlencode
from django.templatetags.static import static
import os
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponseBadRequest
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth import authenticate, login
from math import radians, sin, cos, sqrt, atan2
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from geopy.distance import geodesic
from django.contrib.auth.hashers import check_password, make_password
from .models import Patient, Doctor, Hospital,Facility,Appointment,City,Review,Language,DayOfWeek ,HospitalFeedback,Staff,Treatment,Disease,Department
from django.utils.timezone import make_aware
from datetime import datetime,timedelta
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.utils.timezone import now
from django.db.models import Count
import requests

def intro(request):
    return render(request, 'intro.html')
def about(request):
    return render(request, 'about.html')
def services(request):
    return render(request, 'service.html')


def contact_us(request):
    if request.method == 'POST':
        # Retrieve data from the form
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Send the email (you can also log this data or store it in the database)
        try:
            send_mail(
                f"Message from {name} ({email})",  # Subject
                message,  # Message content
                email,  # From email
                [settings.CONTACT_EMAIL],  # To email (configure in settings.py)
                fail_silently=False,
            )
            return HttpResponse("<h2>Thank you for contacting us! We will get back to you soon.</h2>")
        except Exception as e:
            return HttpResponse(f"<h2>Error sending message: {str(e)}</h2>")

    return render(request, 'contact_us.html')
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
            patient=patient, status='Scheduled', appointment_date__gte=current_time
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
            patient=patient, status='Completed'
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
        patient=patient, status='Completed',
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

    # Calculate the average rating for each doctor
    reviews = Review.objects.filter(doctor__in=doctors)
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] if reviews.exists() else None

    context = {
        'hospital': hospital,
        'doctors': doctors,
        'average_rating': average_rating,
        'active_page': 'home',
    }

    return render(request, 'Patients/hospital_detail.html', context)


def doctor_detail(request, doctor_id):
    """Displays details of a doctor."""
    doctor = Doctor.objects.get(id=doctor_id)
    reviews = Review.objects.filter(doctor=doctor)
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] if reviews.exists() else None
    context = {
        'doctor': doctor,
        'reviews': reviews,
        'average_rating': average_rating,
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
    if not doctor.name or not doctor.diseases or not doctor.hospital or not doctor.city or not doctor.specialty or not doctor.contact_number or not doctor.email or not doctor.qualification:
        messages.warning(request, "Some profile details are missing. Please update your profile.")
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

    # Fetch all reviews for the doctor
    reviews = Review.objects.filter(doctor=doctor).order_by('-created_at')[:3]  # Latest 3 reviews
    review_count = Review.objects.filter(doctor=doctor).count()

    # Calculate the average rating for the doctor, ensuring it's 0 if no reviews
    average_rating = round(sum([r.rating for r in reviews]) / review_count, 2) if review_count > 0 else 0

    # Prepare the distribution of ratings (1-5 stars) for Chart.js visualization
    rating_distribution = {
        "5 Stars": Review.objects.filter(doctor=doctor, rating=5).count(),
        "4 Stars": Review.objects.filter(doctor=doctor, rating=4).count(),
        "3 Stars": Review.objects.filter(doctor=doctor, rating=3).count(),
        "2 Stars": Review.objects.filter(doctor=doctor, rating=2).count(),
        "1 Star": Review.objects.filter(doctor=doctor, rating=1).count(),
    }

    # Convert the rating distribution to JSON format for Chart.js
    rating_distribution_json = json.dumps(rating_distribution)

    # Prepare patient comments to pass to the template (show patient's name and comment)
    patient_comments = reviews.values('patient__name', 'comment', 'created_at')

    # Prepare the context to pass to the template
    context = {
        "doctor": doctor,
        "upcoming_appointments": upcoming_appointments,
        "new_patients": new_patients,
        "total_patients_attendance": total_patients_attendance,
        "total_distinct_patients": total_distinct_patients,
        "average_rating": average_rating,
        "review_count": review_count,
        "rating_distribution": rating_distribution,
        "patient_comments": patient_comments,
        "rating_distribution_json": rating_distribution_json,
        "active_page": "doctor-dashboard",
    }

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

    search_query = request.GET.get('search', '')
    appointment_date = request.GET.get('appointment_date', '')
    if search_query:
        upcoming_appointments = upcoming_appointments.filter(patient__name__icontains=search_query)

    if appointment_date:
        upcoming_appointments = upcoming_appointments.filter(appointment_date__date=appointment_date)
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

    # If search query is provided, filter based on the patient name or appointment date
    search_query = request.GET.get('search', '')
    appointment_date = request.GET.get('appointment_date', '')

    if search_query:
        completed_appointments = completed_appointments.filter(patient__name__icontains=search_query)

    if appointment_date:
        completed_appointments = completed_appointments.filter(appointment_date__date=appointment_date)

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

    search_query = request.GET.get('search', '')  # Get the search query from the GET request

    # If there is a search query, filter patients based on their name
    if search_query:
        patients = patients.filter(name__icontains=search_query)  # Search by patient name

    context = {
        "doctor": doctor,
        "my_patients": patients,
        'active_page': "my-patients",  # Make sure "my-patients" is highlighted in navigation
    }

    return render(request, 'Doctors/my_patients.html', context)
def doctor_comments(request, doctor_id):
    doctor = Doctor.objects.get(id=doctor_id)
    comments = Review.objects.filter(doctor=doctor).order_by('-created_at')  # Ordering by date, most recent first
    search_query = request.GET.get('search', '')

    if search_query:
        comments = comments.filter(patient__name__icontains=search_query)

    context = {
        'doctor': doctor,
        'comments': comments,
        'search_query': search_query,
        'star_range': range(1, 6),
        'active_page': "doctor_comments",
    }

    return render(request, 'Doctors/comments.html', context)

def running_treatments_view(request):
    if 'user_id' not in request.session:
        return redirect('login')  # Redirect if the doctor is not logged in

    doctor = Doctor.objects.get(id=request.session['user_id'])  # Get doctor by session ID
    now_time = timezone.now().date()  # Get current date (timezone-aware)
    patients = Patient.objects.filter(appointments__doctor=doctor).distinct()


    # Fetch treatments that are running (status = 'Running')
    running_treatments = Treatment.objects.filter(
        doctor=doctor,
        status='Running',
    ).order_by('start_date')
    # Handle the search query (from GET request)
    search_query = request.GET.get('search', '')  # Get the search query from the GET request

    # If there is a search query, filter patients based on their name
    if search_query:
        running_treatments = running_treatments.filter(patient__name__icontains=search_query)  # Corrected: keep 'patients' as a queryset

    if request.method == "POST":
        # Add Treatment
        if 'add_treatment' in request.POST:
            patient_id = request.POST.get('patient_name')
            treatment_name = request.POST.get('treatment_name')
            start_date = request.POST.get('start_date')

            patient = Patient.objects.filter(id=patient_id).first()
            if not patient:
                messages.error(request, "Patient not found.")
            else:
                Treatment.objects.create(
                    patient=patient,
                    name=treatment_name,
                    start_date=start_date,
                    status='Running',
                    doctor=doctor
                )
                messages.success(request, "Treatment added successfully.")
                return redirect('running_treatments')

        # Edit Treatment
        if 'edit_treatment' in request.POST:
            treatment_id = request.POST.get('treatment_id')
            treatment_name = request.POST.get('treatment_name')
            start_date = request.POST.get('start_date')

            treatment = Treatment.objects.get(id=treatment_id)
            treatment.name = treatment_name
            treatment.start_date = start_date
            treatment.save()

            messages.success(request, "Treatment updated successfully.")
            return redirect('running_treatments')

    context = {
        'doctor': doctor,  # Use 'patients' here, not 'patient'
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
    search_query = request.GET.get('search', '')  # Get the search query from the GET request

    # If there is a search query, filter patients based on their name
    if search_query:
        past_treatments = past_treatments.filter(patient__name__icontains=search_query)
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
        'active_page':"settings"
    }

    return render(request, 'Doctors/doctor_profile.html', context)


# View (edit_doctor_profile)
def edit_doctor_profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please log in to access this page.")
        return redirect('login')

    try:
        doctor = Doctor.objects.get(id=user_id)
    except Doctor.DoesNotExist:
        messages.error(request, "Doctor not found.")
        return redirect('login')
        # Handle the profile update on POST request
    if request.method == 'POST':
        # Process the incoming data and update the doctor profile
        doctor.name = request.POST.get('name', doctor.name)
        doctor.gender = request.POST.get('gender', doctor.gender)
        doctor.email = request.POST.get('email', doctor.email)
        doctor.contact_number = request.POST.get('contact_number', doctor.contact_number)
        doctor.address = request.POST.get('address', doctor.address)
        doctor.qualification = request.POST.get('qualification', doctor.qualification)
        doctor.experience_years = request.POST.get('experience_years', doctor.experience_years)
        doctor.specialty = request.POST.get('specialty', doctor.specialty)
        doctor.treatment_type = request.POST.get('treatment_type', doctor.treatment_type)
        doctor.consultation_type = request.POST.get('consultation_type', doctor.consultation_type)

        # If there's a new profile picture, handle the upload
        if request.FILES.get('profile_picture'):
            doctor.profile_picture = request.FILES.get('profile_picture')

        # If the hospital was updated, handle it
        hospital_id = request.POST.get('hospital')
        if hospital_id:
            doctor.hospital = Hospital.objects.get(id=hospital_id)

        # Save the updated doctor profile
        doctor.save()

        # Handle days available (multi-select)
        days_available_ids = request.POST.getlist('days_available')
        doctor.days_available.clear()
        doctor.days_available.add(*DayOfWeek.objects.filter(id__in=days_available_ids))

        # Handle diseases (multi-select)
        diseases_ids = request.POST.getlist('diseases')
        doctor.diseases.clear()
        doctor.diseases.add(*Disease.objects.filter(id__in=diseases_ids))

        # Handle languages spoken (multi-select)
        languages_ids = request.POST.getlist('languages_spoken')
        doctor.languages_spoken.clear()
        doctor.languages_spoken.add(*Language.objects.filter(id__in=languages_ids))

        # Success message and redirect
        messages.success(request, 'Profile updated successfully.')
        # In views.py
        return redirect('doctor_profile', doctor_id=doctor.id)
    # Or wherever you want to redirect after update

        # If GET request, just render the profile page with the current data
    else:
        all_days = DayOfWeek.objects.all()
        all_languages = Language.objects.all()
        all_diseases = Disease.objects.all()
        all_hospitals = Hospital.objects.all()
    # Handling GET request: pre-populating the profile form with existing data
    return render(request, 'Doctors/edit_profile.html', {
        'doctor': doctor,
        'diseases': all_diseases,
        'all_days': all_days,
        'all_languages': all_languages,
        'hospitals': all_hospitals
    })

def add_disease(request):
    if request.method == 'POST':
        disease_name = request.POST.get('name')

        # Check if disease name is provided
        if disease_name:
            # Check if disease already exists
            if Disease.objects.filter(name=disease_name).exists():
                messages.error(request, f'Disease "{disease_name}" already exists.')
            else:
                # Create the new disease
                Disease.objects.create(name=disease_name)
                messages.success(request, f'Disease "{disease_name}" added successfully.')
        else:
            messages.error(request, 'Please provide a valid disease name.')

        # Redirect to the profile edit page (or wherever appropriate)
        return redirect('edit_doctor_profile')

    # If not POST request, just redirect to the profile edit page
    return redirect('edit_doctor_profile')
def add_city(request):
    if request.method == "POST":
        # Get the city name from the POST data
        data = json.loads(request.body)
        city_name = data.get('name')

        # Validate the city name
        if not city_name:
            return JsonResponse({'success': False, 'error': 'City name cannot be empty'})

        # Create and save the new city
        city = City.objects.create(name=city_name)

        # Return the success response with the city ID
        return JsonResponse({'success': True, 'city_id': city.id, 'city_name': city.name})

def search_hospitals(request):
    query = request.GET.get('query', '')
    hospitals = Hospital.objects.filter(name__icontains=query)
    return JsonResponse({'hospitals': [{'id': hospital.id, 'name': hospital.name} for hospital in hospitals]})
def search_cities(request):
    query = request.GET.get('query', '')
    cities = City.objects.filter(name__icontains=query)[:10]  # Get cities matching the query, limit to 10 results
    city_data = [{'id': city.id, 'name': city.name} for city in cities]
    return JsonResponse({'cities': city_data})
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

    return render(request, 'Doctors/change_password.html', {'doctor': doctor,'active_page': 'settings'})


def hospital_dashboard(request):
    # Ensure the hospital ID is stored in the session (use a more descriptive session key)
    if 'user_id' not in request.session:
        messages.error(request, "Please log in first.")
        return redirect('login')

    hospital_id = request.session['user_id']  # Use 'hospital_id' for clarity

    try:
        hospital = Hospital.objects.annotate(num_staff=Count('staff')).get(id=hospital_id)
    except Hospital.DoesNotExist:
        messages.error(request, "Hospital not found.")
        return redirect('login')
    if not hospital.name or not hospital.address or not hospital.contact_number:
        messages.warning(request, "Your hospital profile is incomplete. Please update it.")
    # Add more hospital-specific information here
    num_doctors = hospital.doctors.count()  # Assuming you have a related Doctor model
    num_staff =  hospital.num_staff  # Assuming you have a related Staff model
    num_departments = hospital.departments.count()  # Count the number of departments in this hospital

    # For today's appointments, assuming Appointment model has an `appointment_date` field
    today_appointments = Appointment.objects.filter(hospital=hospital, appointment_date__date=datetime.today()).count()

    # For total appointment requests
    total_appointment_requests = Appointment.objects.filter(hospital=hospital, status="Requested").count()

    # For total reschedule requests
    total_reschedule_requests = Appointment.objects.filter(hospital=hospital, status="Rescheduled").count()

    # Average doctor rating
    avg_doctor_rating = Review.objects.filter(doctor__hospital=hospital).aggregate(Avg('rating'))['rating__avg'] or 0
    running_treatments = Treatment.objects.filter(doctor__hospital=hospital, status="Running").count()
    context = {
        'hospital': hospital,
        'num_doctors': num_doctors,
        'num_staff': num_staff,
        'num_departments': num_departments,
        'today_appointments': today_appointments,
        'running_treatments': running_treatments,
        'total_appointment_requests': total_appointment_requests,
        'total_reschedule_requests': total_reschedule_requests,
        'avg_doctor_rating': round(avg_doctor_rating, 1),  # rounding to 1 decimal place
        'active_page': 'hospital-dashboard',
    }
    return render(request, 'Hospital/hospital-dashboard.html', context)


def submit_appointment_request(request):
    if 'user_id' not in request.session:
        return redirect('login')  # Redirect if the patient is not logged in

    # Fetch the patient object using session data
    try:
        patient = Patient.objects.get(id=request.session['user_id'])
    except Patient.DoesNotExist:
        return redirect('login')  # If patient doesn't exist, redirect to login

    if request.method == 'POST':
        # Get the data from the form
        doctor_id = request.POST.get('doctor_id')
        treatment = request.POST.get('treatment_type')  # Get the treatment type from the form
        reason = request.POST.get('reason')
        appointment_date = request.POST.get('appointment_date')

        # Ensure treatment_type is not empty
        if not treatment:
            messages.error(request, "Treatment type cannot be empty.")
            return redirect('doctor_listing')

        try:
            doctor = Doctor.objects.get(id=doctor_id)
            hospital = doctor.hospital
            hospital_city = hospital.city
        except Doctor.DoesNotExist:
            messages.error(request, "The selected doctor does not exist.")
            return redirect('doctor_listing')

        try:
            requested_date = timezone.datetime.strptime(appointment_date, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
            return redirect('doctor_listing')

        # Check if the appointment already exists for this doctor, patient, and date
        if Appointment.objects.filter(doctor_id=doctor_id, patient_id=patient.id, appointment_date=appointment_date).exists():
            messages.error(request, "This appointment is already booked.")
            return redirect('doctor_listing')

        # Create the appointment
        appointment = Appointment(
            doctor=doctor,
            patient=patient,
            hospital=hospital,
            city=hospital_city,
            appointment_date=requested_date,  # Only the date, no time yet
            treatment_type=treatment,
            reason=reason,
            status='Requested'  # Status is 'Requested' until the hospital assigns a time
        )
        appointment.save()

        # Notify the patient that the appointment request was successful
        messages.success(request,
                         "Your appointment request has been successfully sent. The hospital will assign a time shortly.")
        return redirect('doctor_listing')  # Or any other redirect path after submission

    # Redirect in case the method is not POST (or any other error)
    return redirect('doctor_listing')

def upcoming_appointments(request):
    # Ensure the hospital ID is stored in the session (use a more descriptive session key)
    if 'user_id' not in request.session:
        messages.error(request, "Please log in first.")
        return redirect('login')

    hospital_id = request.session['user_id']  # Use 'hospital_id' for clarity

    try:
        hospital = Hospital.objects.get(id=hospital_id)
    except Hospital.DoesNotExist:
        messages.error(request, "Hospital not found.")
        return redirect('login')
    # Fetch all upcoming appointments
    appointments = Appointment.objects.filter(hospital=hospital, status='Scheduled').order_by('appointment_date')
    context = {
        'hospital': hospital,
        'appointments':appointments,
        'active_page':"appointments"
    }
    # Render the page with the upcoming appointments
    return render(request, 'Hospital/today-appointments.html', context)

def appointment_requests(request):
    # Check if the user is logged in (using session)
    if 'user_id' not in request.session:
        messages.error(request, "Please log in first.")
        return redirect('login')

    hospital_id = request.session['user_id']  # Use 'hospital_id' for clarity

    try:
        # Fetch hospital object based on hospital_id from session
        hospital = Hospital.objects.get(id=hospital_id)
    except Hospital.DoesNotExist:
        # If hospital not found, redirect to login page with error message
        messages.error(request, "Hospital not found.")
        return redirect('login')

    # Fetch all appointment requests that have 'Requested' status
    appointments = Appointment.objects.filter(hospital=hospital, status='Requested').order_by('appointment_date')

    context = {
        'hospital': hospital,
        'appointments': appointments,
        'active_page': 'appointment-requests',  # To highlight the active page in the navbar
    }

    return render(request, 'Hospital/appointments-request.html', context)

def send_approval_email(appointment, hospital):
    # Get doctor and hospital information
    doctor_name = appointment.doctor.name  # Assuming doctor has a 'name' field
    hospital_name = hospital.name  # Access hospital name from the passed hospital object

    subject = "Your Appointment has been Approved"

    # HTML email content without logo or image
    html_content = f"""
    <html>
    <body>
        <p>Dear {appointment.patient.name},</p>

        <p>We are pleased to inform you that your appointment has been approved.</p>
        <p><b>Appointment Details:</b><br>
        <b>Doctor:</b> {doctor_name}<br>
        <b>Hospital:</b> {hospital_name}<br>
        <b>Date:</b> {appointment.appointment_date.strftime('%Y-%m-%d')}<br>
        <b>Time:</b> {appointment.appointment_date.strftime('%H:%M')}<br>
        <b>Status:</b> {appointment.status}<br>
        </p>

        <p>Please be on time for your appointment. We look forward to seeing you soon.</p>

        <p>Best regards,<br>{hospital_name}</p>

    </body>
    </html>
    """

    # Plain text version (fallback if HTML is not supported by the client)
    text_content = strip_tags(html_content)  # Strips HTML tags to create plain text

    # Create the email
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [appointment.patient.email]  # Ensure `patient_email` is a field in your Appointment model

    email = EmailMultiAlternatives(
        subject, text_content, from_email, recipient_list
    )

    # Set the HTML content without logo or image
    email.content_subtype = "html"  # Ensure content is HTML
    email.attach_alternative(html_content, "text/html")  # Attach the HTML content

    # Send the email
    try:
        email.send()
        print("Approval email sent successfully without logo or image!")
    except Exception as e:
        print(f"Error sending email: {e}")
def approve_appointment(request, appointment_id):
    # Check if the user is logged in (using session)
    if 'user_id' not in request.session:
        messages.error(request, "Please log in first.")
        return redirect('login')
    hospital_id = request.session['user_id']  # Use 'hospital_id' for clarity

    try:
        # Fetch hospital object based on hospital_id from session
        hospital = Hospital.objects.get(id=hospital_id)
    except Hospital.DoesNotExist:
        # If hospital not found, redirect to login page with error message
        messages.error(request, "Hospital not found.")
        return redirect('login')
    # Fetch the appointment request from the database
    appointment = Appointment.objects.get(id=appointment_id)
    if request.method == 'POST':
        # Get the time provided by the hospital
        appointment_time = request.POST.get('appointment_time')

        if not appointment_time:
            return HttpResponseBadRequest("No appointment time provided.")  # In case no time is entered

        # Combine the requested date with the assigned time to create the full appointment datetime
        requested_date = appointment.appointment_date
        time_parts = appointment_time.split(":")  # Split the time input (HH:MM)

        # Update the appointment datetime with the provided time
        assigned_datetime = requested_date.replace(hour=int(time_parts[0]), minute=int(time_parts[1]), second=0,
                                                   microsecond=0)

        # Update the appointment time and status
        appointment.appointment_date = assigned_datetime
        appointment.status = 'Scheduled'  # Mark appointment as scheduled
        appointment.save()
        # Send email with appointment details and hospital information
        send_approval_email(appointment, hospital)

        # Redirect to appointment request list after approval
        return redirect('appointments-request')  # Or to another page showing approved appointments

    return redirect('appointments-request')
def cancel_appointment(request, appointment_id):
    # Check if the user is logged in (using session)
    if 'user_id' not in request.session:
        messages.error(request, "Please log in first.")
        return redirect('login')

    # Fetch the appointment instance
    appointment = Appointment.objects.get(id=appointment_id)

    # Ensure the logged-in user is associated with this appointment
    if appointment.patient.id != request.session['user_id']:
        messages.error(request, "You are not authorized to cancel this appointment.")
        return redirect('appointments-request')

    # Update the status of the appointment to "Canceled"
    appointment.status = 'Canceled'
    appointment.save()

    # Show a success message
    messages.success(request, f"Appointment for {appointment.patient.name} has been canceled.")

    # Send email notification to the patient
    send_mail(
        subject='Appointment Cancellation Confirmation',
        message=f"Dear {appointment.patient.name},\n\n"
                f"Your appointment with Dr. {appointment.doctor.name} on {appointment.date} has been canceled.\n"
                f"Please contact us if you wish to reschedule or have any further questions.\n\n"
                f"Best regards,\nThe HealthCare Team",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[appointment.patient.email],
    )

    # Optionally, send a notification to the doctor
    send_mail(
        subject='Appointment Cancellation Notification',
        message=f"Dear Dr. {appointment.doctor.name},\n\n"
                f"An appointment with {appointment.patient.name} on {appointment.date} has been canceled.\n"
                f"Please check your schedule for updates.\n\n"
                f"Best regards,\nThe HealthCare Team",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[appointment.doctor.email],
    )

    # Redirect to the appointment request list after cancellation
    return redirect('appointments-request')

def reschedule_appointment(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id)

    if request.method == 'POST':
        new_appointment_date = request.POST.get('appointment_date')

        if new_appointment_date:
            # Convert the new appointment date to a datetime object
            new_appointment_date_obj = datetime.strptime(new_appointment_date, '%Y-%m-%d')

            # Check if an appointment already exists for the same doctor and patient on the new date
            conflicting_appointment = Appointment.objects.filter(
                doctor=appointment.doctor,
                patient=appointment.patient,
                appointment_date=new_appointment_date_obj
            ).exists()

            if conflicting_appointment:
                messages.error(request,
                               "An appointment already exists for this doctor and patient on the selected date.")
                return redirect('patient_appointments')

            # If no conflict, update the appointment date and status
            appointment.appointment_date = new_appointment_date_obj
            appointment.status = "Rescheduled"  # Update status to Rescheduled
            try:
                appointment.save()  # Save the updated appointment
                messages.success(request, "Your appointment has been rescheduled successfully.")
                return redirect('patient_appointments')  # Redirect back to the appointments page
            except IntegrityError:
                messages.error(request, "There was an error while saving the rescheduled appointment.")
                return redirect('patient_appointments')  # Redirect back in case of error

    # If something goes wrong, return to the appointments page with an error message
    messages.error(request, "Something went wrong while rescheduling your appointment.")
    return redirect('patient_appointments')
def doctor_reschedule_appointment(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id)

    if request.method == 'POST':
        new_appointment_date = request.POST.get('appointment_date')

        if new_appointment_date:
            # Convert the new appointment date to a datetime object
            new_appointment_date_obj = datetime.strptime(new_appointment_date, '%Y-%m-%d')

            # Check if an appointment already exists for the same doctor and patient on the new date
            conflicting_appointment = Appointment.objects.filter(
                doctor=appointment.doctor,
                patient=appointment.patient,
                appointment_date=new_appointment_date_obj
            ).exists()

            if conflicting_appointment:
                messages.error(request,
                               "An appointment already exists for this doctor and patient on the selected date.")
                return redirect('appointments_view')

            # If no conflict, update the appointment date and status
            appointment.appointment_date = new_appointment_date_obj
            appointment.status = "Rescheduled"  # Update status to Rescheduled
            try:
                appointment.save()  # Save the updated appointment
                messages.success(request, "Your appointment has been rescheduled successfully.")
                return redirect('appointments_view')  # Redirect back to the appointments page
            except IntegrityError:
                messages.error(request, "There was an error while saving the rescheduled appointment.")
                return redirect('appointments_view')  # Redirect back in case of error

    # If something goes wrong, return to the appointments page with an error message
    messages.error(request, "Something went wrong while rescheduling your appointment.")
    return redirect('appointments_view')
def cancel_appointment(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id)

    if request.method == 'POST':
        appointment.status = "Canceled"  # Update status to Canceled
        appointment.save()

        messages.success(request, "Your appointment has been canceled.")
        return redirect('patient_appointments')  # Redirect to the appointments page

    messages.error(request, "Something went wrong while canceling your appointment.")
    return redirect('patient_appointments')
def doctor_cancel_appointment(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id)

    if request.method == 'POST':
        appointment.status = "Canceled"  # Update status to Canceled
        appointment.save()

        messages.success(request, "Your appointment has been canceled.")
        return redirect('appointments_view')  # Redirect to the appointments page

    messages.error(request, "Something went wrong while canceling your appointment.")
    return redirect('appointments_view')
def rescheduled_requests(request):
    # Check if the user is logged in (using session)
    if 'user_id' not in request.session:
        messages.error(request, "Please log in first.")
        return redirect('login')

    hospital_id = request.session['user_id']  # Use 'hospital_id' for clarity

    try:
        # Fetch hospital object based on hospital_id from session
        hospital = Hospital.objects.get(id=hospital_id)
    except Hospital.DoesNotExist:
        # If hospital not found, redirect to login page with error message
        messages.error(request, "Hospital not found.")
        return redirect('login')

    # Fetch all appointment requests that have 'Reschedule' status
    appointments = Appointment.objects.filter(hospital=hospital, status='Rescheduled').order_by('appointment_date')

    # Check if there are no reschedule requests
    if not appointments:
        messages.info(request, "No reschedule requests found.")

    context = {
        'hospital': hospital,
        'appointments': appointments,
        'active_page': 'reschedule-requests',  # To highlight the active page in the navbar
    }

    return render(request, 'Hospital/reschedule-request.html', context)

def send_reschedule_email(appointment, hospital):
    # Get doctor and hospital information
    doctor_name = appointment.doctor.name  # Assuming doctor has a 'name' field
    hospital_name = hospital.name  # Access hospital name from the passed hospital object

    subject = "Your Appointment has been Rescheduled"

    # HTML email content
    html_content = f"""
    <html>
    <body>
        <p>Dear {appointment.patient.name},</p>

        <p>Your appointment has been rescheduled.</p>
        <p><b>Appointment Details:</b><br>
        <b>Doctor:</b> {doctor_name}<br>
        <b>Hospital:</b> {hospital_name}<br>
        <b>New Date:</b> {appointment.appointment_date.strftime('%Y-%m-%d')} at {appointment.appointment_date.strftime('%I:%M %p')
}<br>
        <b>Status:</b> {appointment.status}<br>
        </p>

        <p>Please be on time for your rescheduled appointment. We look forward to seeing you soon.</p>

        <p>Best regards,<br>{hospital_name}</p>
    </body>
    </html>
    """

    # Plain text version (fallback if HTML is not supported by the client)
    text_content = strip_tags(html_content)  # Strips HTML tags to create plain text

    # Create the email
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [appointment.patient.email]  # Ensure `patient_email` is a field in your Appointment model

    email = EmailMultiAlternatives(
        subject, text_content, from_email, recipient_list
    )

    # Set the HTML content
    email.content_subtype = "html"  # Ensure content is HTML
    email.attach_alternative(html_content, "text/html")  # Attach the HTML content

    # Send the email
    try:
        email.send()
        print("Reschedule email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")


def rescheduled_appointments(request, appointment_id):
    # Check if the user is logged in (using session)
    if 'user_id' not in request.session:
        messages.error(request, "Please log in first.")
        return redirect('login')

    # Fetch the appointment request from the database
    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        messages.error(request, "Appointment not found.")
        return redirect('reschedule_request')

    if request.method == 'POST':
        # Get the time provided by the hospital
        appointment_time = request.POST.get('appointment_time')

        if not appointment_time:
            return HttpResponseBadRequest("No appointment time provided.")  # In case no time is entered
        # Combine the requested date with the assigned time to create the full appointment datetime
        requested_date = appointment.appointment_date
        try:
            time_parts = appointment_time.split(":")  # Split the time input (HH:MM)

            # Validate time input to ensure correct format
            if len(time_parts) != 2 or not all(part.isdigit() for part in time_parts):
                return HttpResponseBadRequest("Invalid time format. Please use HH:MM.")

            # Update the appointment datetime with the provided time
            assigned_datetime = requested_date.replace(
                hour=int(time_parts[0]),
                minute=int(time_parts[1]),
                second=0,
                microsecond=0
            )

            # Update the appointment time and status
            appointment.appointment_date = assigned_datetime
            appointment.status = 'Scheduled'  # Mark appointment as rescheduled
            appointment.save()

            # Send the reschedule confirmation email with both original and new dates
            hospital = appointment.hospital  # Assuming appointment has a hospital field
            send_reschedule_email(appointment, hospital)

            # Redirect to appointment request list after rescheduling
            messages.success(request, "Appointment rescheduled successfully.")
            return redirect('reschedule_request')  # Or to another page showing rescheduled appointments

        except ValueError:
            return HttpResponseBadRequest("Invalid date or time input. Please try again.")

    return redirect('reschedule_request')
def doctors_page(request):
    # Ensure the hospital ID is stored in the session
    if 'user_id' not in request.session:
        messages.error(request, "Please log in first.")
        return redirect('login')

    hospital_id = request.session['user_id']

    try:
        hospital = Hospital.objects.get(id=hospital_id)
    except Hospital.DoesNotExist:
        messages.error(request, "Hospital not found.")
        return redirect('login')

    # Get the search query from GET parameters
    search_query = request.GET.get('search', '')

    # Fetch all doctors associated with the hospital
    doctors = hospital.doctors.all()

    if search_query:
        # Use Q objects to combine multiple conditions
        doctors = doctors.filter(
            Q(name__icontains=search_query) |
            Q(specialty__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    # Prepare context to pass to the template
    context = {
        'doctors': doctors,
        'hospital': hospital,
        'search_query': search_query,
        'active_page': 'doctors'
    }

    return render(request, 'Hospital/doctors-list.html', context)
def view_doctor(request, doctor_id):
    # Ensure the hospital ID is stored in the session
    if 'user_id' not in request.session:
        messages.error(request, "Please log in first.")
        return redirect('login')

    hospital_id = request.session['user_id']

    try:
        hospital = Hospital.objects.get(id=hospital_id)
    except Hospital.DoesNotExist:
        messages.error(request, "Hospital not found.")
        return redirect('login')

    try:
        doctor = Doctor.objects.get(id=doctor_id)
    except Doctor.DoesNotExist:
        messages.error(request, "Doctor not found.")
        return redirect('doctors_page')

    # Calculate the average rating for the specific doctor
    avg_doctor_rating = Review.objects.filter(doctor=doctor).aggregate(Avg('rating'))['rating__avg']

    # If no ratings, set to a default value
    if avg_doctor_rating is None:
        avg_doctor_rating = 0.0

    # Prepare context to pass to the template
    context = {
        'hospital': hospital,
        'doctor': doctor,
        'average_rating': avg_doctor_rating,  # Pass the average rating to the template
        'active_page': 'doctors'
    }

    return render(request, 'Hospital/view_doctor.html', context)
def toggle_doctor_status(request, doctor_id):
    try:
        doctor = Doctor.objects.get(id=doctor_id)
    except Doctor.DoesNotExist:
        messages.error(request, "Doctor not found.")
        return redirect('doctors_page')

    # Toggle the doctor's status
    doctor.is_active = not doctor.is_active
    doctor.save()

    # Success message
    messages.success(request, f"Doctor status changed to {'Active' if doctor.is_active else 'Inactive'}.")

    return redirect('doctors_page')

def staff_list(request):
    if 'user_id' not in request.session:
        messages.error(request, "Please log in first.")
        return redirect('login')

    hospital_id = request.session['user_id']

    try:
        hospital = Hospital.objects.get(id=hospital_id)
    except Hospital.DoesNotExist:
        messages.error(request, "Hospital not found.")
        return redirect('login')

    # Fetch filter options
    search_query = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')
    department_filter = request.GET.get('department', '')

    # Fetch staff members based on filters
    staff_members = Staff.objects.filter(hospital=hospital)

    if search_query:
        staff_members = staff_members.filter(name__icontains=search_query)

    if role_filter:
        staff_members = staff_members.filter(role=role_filter)

    if department_filter:
        staff_members = staff_members.filter(department__name=department_filter)

    # Get all departments and roles for filter options
    departments = Department.objects.filter(hospitals=hospital)
    roles = Staff.ROLE_CHOICES

    context = {
        'hospital': hospital,
        'staff_members': staff_members,
        'departments': departments,
        'roles': roles,
        'search_query': search_query,
        'role_filter': role_filter,
        'department_filter': department_filter,
        'active_page': 'staff'
    }

    return render(request, 'Hospital/staff_list.html', context)
def toggle_staff_status(request, staff_id):
    if 'user_id' not in request.session:
        messages.error(request, "Please log in first.")
        return redirect('login')

    hospital_id = request.session['user_id']

    try:
        staff = Staff.objects.get(id=staff_id)
    except Staff.DoesNotExist:
        messages.error(request, "Staff member not found.")
        return redirect('staff_list')

    # Toggle staff status between Active and Inactive
    staff.is_active = not staff.is_active
    staff.save()

    messages.success(request, f"Staff status changed to {'Active' if staff.is_active else 'Inactive'}.")
    return redirect('staff_list')

    # Toggle staff status
    staff.is_active = not staff.is_active
    staff.save()

    messages.success(request, f"Staff status changed to {'Active' if staff.is_active else 'Inactive'}.")
    return redirect('staff_list')
def add_staff(request):
    if 'user_id' not in request.session:
        messages.error(request, "Please log in first.")
        return redirect('login')

    hospital_id = request.session['user_id']

    try:
        hospital = Hospital.objects.get(id=hospital_id)
    except Hospital.DoesNotExist:
        messages.error(request, "Hospital not found.")
        return redirect('login')

    if request.method == 'POST':
        # Retrieve form data
        name = request.POST['name']
        role = request.POST['role']
        contact_number = request.POST['contact_number']
        email = request.POST['email']
        department_id = request.POST.get('department')
        department = Department.objects.get(id=department_id) if department_id else None
        hire_date = request.POST['hire_date']
        is_active = request.POST.get('is_active') == 'on'

        # Create staff member
        staff_member = Staff.objects.create(
            hospital=hospital,
            name=name,
            role=role,
            contact_number=contact_number,
            email=email,
            department=department,
            hire_date=hire_date,
            is_active=is_active
        )

        # Show success message
        messages.success(request, f'New staff member {staff_member.name} added successfully.')

        # Redirect to staff list page
        return redirect('staff_list')

    else:
        # GET request - Provide departments and roles for the form
        roles = Staff.ROLE_CHOICES
        departments = Department.objects.filter(hospital=hospital)
        return render(request, 'staff/add_staff_modal.html', {'roles': roles, 'departments': departments})


def edit_staff(request, staff_id):
    if 'user_id' not in request.session:
        messages.error(request, "Please log in first.")
        return redirect('login')

    hospital_id = request.session['user_id']

    try:
        hospital = Hospital.objects.get(id=hospital_id)
    except Hospital.DoesNotExist:
        messages.error(request, "Hospital not found.")
        return redirect('login')

    # Fetch the staff member to edit
    staff_member = Staff.objects.get(id=staff_id, hospital=hospital)

    if request.method == 'POST':
        # Update the staff member's details
        staff_member.name = request.POST['name']
        staff_member.role = request.POST['role']
        staff_member.contact_number = request.POST['contact_number']
        staff_member.email = request.POST['email']
        department_id = request.POST.get('department')
        staff_member.department = Department.objects.get(id=department_id) if department_id else None
        staff_member.hire_date = request.POST['hire_date']
        staff_member.is_active = request.POST.get('is_active') == 'on'

        # Save the updated staff member
        staff_member.save()

        # Show success message
        messages.success(request, f'Staff member {staff_member.name} updated successfully.')

        # Redirect to staff list page
        return redirect('staff_list')

    else:
        # GET request - Pre-populate the form with current staff member's details
        roles = Staff.ROLE_CHOICES
        departments = Department.objects.filter(hospital=hospital)
        return render(request, 'staff/edit_staff.html', {
            'staff_member': staff_member,
            'roles': roles,
            'departments': departments
        })


def delete_staff(request, staff_id):
    staff =Staff.objects.get(id=staff_id)

    # Delete the staff member
    staff.delete()

    return redirect('staff_list')

def department_list(request):
    # Ensure the user is logged in by checking the session
    if 'user_id' not in request.session:
        messages.error(request, "Please log in first.")
        return redirect('login')

    hospital_id = request.session['user_id']

    try:
        hospital = Hospital.objects.get(id=hospital_id)
    except Hospital.DoesNotExist:
        messages.error(request, "Hospital not found.")
        return redirect('login')

    # Get departments for the logged-in hospital
    departments = Department.objects.filter(hospitals=hospital)

    if request.method == 'POST':
        action = request.POST.get('action')  # Identify add, edit, or delete action

        # Add department
        if action == 'add':
            # Get the department information from the form
            name = request.POST.get('name')
            description = request.POST.get('description')
            head_of_department = request.POST.get('head_of_department')
            is_active = 'is_active' in request.POST  # Checkbox handling

            # Create and save a new department instance
            department = Department(
                name=name,
                description=description,
                head_of_department=head_of_department,
                is_active=is_active,
            )
            department.save()  # Save the new department to the database

            # Now associate the newly created department with the hospital
            hospital = Hospital.objects.get(id=hospital_id)  # Fetch the hospital based on hospital_id
            hospital.departments.add(department)  # Add the newly created department to the hospital's departments

            messages.success(request, 'Department added successfully to the hospital!')

        # Edit department
        elif action == 'edit':
            department_id = request.POST.get('department_id')
            department =Department.objects.get(id=department_id, hospitals=hospital)  # Ensure the department belongs to the hospital

            department.name = request.POST.get('name')
            department.description = request.POST.get('description')
            department.head_of_department = request.POST.get('head_of_department')
            department.is_active = 'is_active' in request.POST  # Checkbox handling
            department.save()  # Save the updated department
            messages.success(request, 'Department updated successfully!')

        # Delete department
        elif action == 'delete':
            department_id = request.POST.get('department_id')
            department = Department.objects.get(id=department_id, hospitals=hospital)  # Ensure the department belongs to the hospital
            department.delete()  # Delete the department
            messages.success(request, 'Department deleted successfully!')

        return redirect('department_list')  # Redirect to the department list after action

    context = {
        'hospital': hospital,
        'departments': departments,
        'active_page': 'departments',  # Highlight the 'departments' section
    }

    return render(request, 'Hospital/department_list.html', context)
def facility_list(request):
    # Check if user is logged in
    if 'user_id' not in request.session:
        messages.error(request, "Please log in first.")
        return redirect('login')

    hospital_id = request.session['user_id']

    try:
        # Fetch the hospital based on the hospital ID from the session
        hospital = Hospital.objects.get(id=hospital_id)
    except Hospital.DoesNotExist:
        messages.error(request, "Hospital not found.")
        return redirect('login')

    # Retrieve all facilities related to the hospital
    facilities = Facility.objects.filter(hospitals=hospital)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            # Add a new facility to the hospital
            name = request.POST.get('name')
            description = request.POST.get('description')
            available_from = request.POST.get('available_from')
            available_until = request.POST.get('available_until')
            is_active = 'is_active' in request.POST  # Checkbox handling

            # Create and save new facility
            facility = Facility(
                name=name,
                description=description,
                available_from=available_from,
                available_until=available_until,
                is_active=is_active
            )
            facility.save()

            hospital = Hospital.objects.get(id=hospital_id)
            hospital.hospital_facilities.add(facility)

            messages.success(request, 'Facility added successfully to the hospital!')

        elif action == 'edit':
            # Edit an existing facility
            facility_id = request.POST.get('facility_id')
            facility = Facility.objects.get(id=facility_id)

            facility.name = request.POST.get('name')
            facility.description = request.POST.get('description')
            facility.available_from = request.POST.get('available_from')
            facility.available_until = request.POST.get('available_until')
            facility.is_active = 'is_active' in request.POST  # Checkbox handling

            facility.save()
            messages.success(request, 'Facility updated successfully!')

        elif action == 'delete':
            # Delete facility
            facility_id = request.POST.get('facility_id')
            facility = Facility.objects.get(id=facility_id)
            hospital = Hospital.objects.get(id=hospital_id)
            # Remove the facility from the hospital's facilities first
            hospital.hospital_facilities.remove(facility)
            facility.delete()

            messages.success(request, 'Facility deleted successfully!')

        return redirect('facility_list')  # Redirect back to the facility list

    context = {
        'hospital': hospital,
        'facilities': facilities,
        'active_page':"facilities"
    }

    return render(request, 'Hospital/facility_list.html', context)
def completed_appointment(request):
    # Check if user is logged in
    if 'user_id' not in request.session:
        messages.error(request, "Please log in first.")
        return redirect('login')

    hospital_id = request.session['user_id']

    try:
        # Fetch the hospital based on the hospital ID from the session
        hospital = Hospital.objects.get(id=hospital_id)
    except Hospital.DoesNotExist:
        messages.error(request, "Hospital not found.")
        return redirect('login')
    search_query = request.GET.get('search', '')
    if search_query:
        # Filter appointments by patient name if search is applied
        completed_appointments = Appointment.objects.filter(hospital=hospital,
            status='Completed',
            patient__name__icontains=search_query
        )
    else:
        completed_appointments = Appointment.objects.filter(hospital=hospital,status='completed')

    context = {
        'hospital':hospital,
        'completed_appointments': completed_appointments,
        'active_page': "appointment-records"
    }

    return render(request, 'hospital/appointment-record.html', context)
def running_treatments(request):
    # Check if the user is logged in
    if 'user_id' not in request.session:
        messages.error(request, "Please log in first.")
        return redirect('login')

    # Get hospital id from session
    hospital_id = request.session['user_id']

    try:
        # Fetch the hospital based on the hospital ID from the session
        hospital = Hospital.objects.get(id=hospital_id)
    except Hospital.DoesNotExist:
        # If hospital is not found, redirect to login
        messages.error(request, "Hospital not found.")
        return redirect('login')

    # Get search query from GET request (if any)
    search_query = request.GET.get('search', '')

    # Filter treatments based on hospital and status 'running'
    if search_query:
        treatments = Treatment.objects.filter(
            doctor__hospital=hospital,
            status='Running',
            patient__name__icontains=search_query
        )
    else:
        treatments = Treatment.objects.filter(doctor__hospital=hospital, status="Running")

    # Prepare context to render
    context = {
        'hospital': hospital,
        'treatments': treatments,
        'active_page': 'running-treatments',  # Set the active page for the navbar
    }

    # Render the template with the context data
    return render(request, 'Hospital/running_treatments.html', context)
def treatments_record(request):
    # Check if the user is logged in
    if 'user_id' not in request.session:
        messages.error(request, "Please log in first.")
        return redirect('login')

    # Get hospital id from session
    hospital_id = request.session['user_id']

    try:
        # Fetch the hospital based on the hospital ID from the session
        hospital = Hospital.objects.get(id=hospital_id)
    except Hospital.DoesNotExist:
        # If hospital is not found, redirect to login
        messages.error(request, "Hospital not found.")
        return redirect('login')

    # Get search query from GET request (if any)
    search_query = request.GET.get('search', '')

    # Filter treatments based on hospital and status 'running'
    if search_query:
        treatments = Treatment.objects.filter(
            doctor__hospital=hospital,
            status='Completed',
            patient__name__icontains=search_query
        )
    else:
        treatments = Treatment.objects.filter(doctor__hospital=hospital, status="Completed")

    # Prepare context to render
    context = {
        'hospital': hospital,
        'treatments': treatments,
        'active_page': 'treatments-records',  # Set the active page for the navbar
    }

    # Render the template with the context data
    return render(request, 'Hospital/treatment-records.html', context)
def hospital_profile(request, hospital_id):
    # Fetch the hospital using the ID passed in the URL
    hospital = Hospital.objects.get(id=hospital_id)

    # Create context to pass data to the template
    context = {
        'hospital': hospital,
        'active_page': 'settings',
    }

    return render(request, 'Hospital/hospital_profile.html', context)


def edit_hospital_profile(request):
    # Assuming the user is logged in and the hospital is associated with the logged-in user
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please log in to access this page.")
        return redirect('login')

    # Retrieve the hospital object
    hospital = Hospital.objects.get(id=user_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        contact_number = request.POST.get('contact_number')
        email = request.POST.get('email')
        address = request.POST.get('address')
        established_date=request.POST.get('established_date')

        # Handle city selection (assign city name as a string to the CharField)
        selected_city_id = request.POST.get('city')
        if selected_city_id:
            try:
                selected_city = City.objects.get(id=selected_city_id)
                Hospital.city = selected_city.name  # Assign the city name (string) to the CharField
            except City.DoesNotExist:
                messages.error(request, "Selected city does not exist.")
                return redirect('edit_hospital_profile')
        else:
            messages.error(request, "Please select a valid city.")
        hospital.name = name
        hospital.contact_number = contact_number
        hospital.email = email
        hospital.address = address
        hospital.established_date =established_date
        if 'profile_picture' in request.FILES:
            hospital.profile_picture = request.FILES['profile_picture']
        hospital.save()
        messages.success(request, "Hospital profile has been updated successfully.")
        return redirect('hospital-profile', hospital_id=hospital.id)

    context = {
        'hospital': hospital,
        'active_page': 'settings',
    }
    return render(request, 'Hospital/edit_profile.html', context)


def change_hospital_password(request):
    if 'user_id' not in request.session:
        messages.error(request, "Please log in first.")
        return redirect('login')

    hospital = Hospital.objects.filter(id=request.session['user_id']).first()
    if not hospital:
        messages.error(request, "Hospital not found.")
        return redirect('login')

    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Directly compare stored password (NOT RECOMMENDED if hashed)
        if current_password != hospital.password:
            messages.error(request, "Current password is incorrect.")
        elif new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
        else:
            hospital.password = new_password  # ⚠️ Plain text storage (Not Secure)
            hospital.save()
            request.session.flush()  # Log out user after changing password
            messages.success(request, "Password changed successfully. Please log in again.")
            return redirect('login')

    return render(request, 'Hospital/hospital-password.html', {'hospital': hospital, 'active_page': 'settings'})
def attend(request, appointment_id):
    # Ensure the user is logged in and is a doctor
    if 'user_id' not in request.session:
        return redirect('login')  # Redirect to login page if the doctor is not logged in

    try:
        # Fetch the appointment object by ID
        appointment = Appointment.objects.get(id=appointment_id)

        # Check if the current user is the doctor responsible for this appointment
        if appointment.hospital.id != request.session['user_id']:
            messages.error(request, "You do not have permission to complete this appointment.")
            return redirect('upcoming_appointments')

        # Update the appointment status to 'Completed'
        appointment.status = 'Completed'
        appointment.save()

        # Provide feedback to the user
        messages.success(request, f"Appointment {appointment_id} has been marked as completed.")

        # Get patient and doctor information
        patient = appointment.patient
        doctor = appointment.doctor
        hospital = appointment.hospital

        doctor_query = urlencode({'doctor_id': doctor.id, 'patient_id': patient.id, 'appointment_id': appointment.id})
        hospital_query = urlencode(
            {'hospital_id': hospital.id, 'patient_id': patient.id, 'appointment_id': appointment.id})

        review_doctor_url = f"{reverse('submit_review_or_feedback')}?{doctor_query}"
        review_hospital_url = f"{reverse('submit_review_or_feedback')}?{hospital_query}"
        # Send an email to the patient with the review links
        subject = "Appointment Completed - Please Review Your Doctor and Hospital"
        message = f"Dear {patient.name},\n\nYour appointment with Dr. {doctor.name} has been marked as completed. We would appreciate it if you could take a moment to review both the doctor and the hospital:\n\n" \
                  f"Review Doctor: {request.build_absolute_uri(review_doctor_url)}\n" \
                  f"Review Hospital: {request.build_absolute_uri(review_hospital_url)}\n\n" \
                  "Thank you for your feedback!\n\nBest Regards,\nYour Hospital Team"
        from_email = 'your_email@example.com'
        to_email = [patient.email]

        send_mail(subject, message, from_email, to_email)

        # Redirect back to the upcoming appointments page
        return redirect('upcoming_appointments')

    except Appointment.DoesNotExist:
        messages.error(request, "Appointment not found.")
        return redirect('upcoming_appointments')


def submit_review_or_feedback(request):
    if 'user_id' not in request.session:
        return redirect('login')  # Ensure the user is logged in before submitting feedback or review

    patient = Patient.objects.get(id=request.session['user_id'])

    # Retrieve the form data
    hospital_id = request.GET.get('hospital_id')
    doctor_id = request.GET.get('doctor_id')
    patient_id = request.GET.get('patient_id')
    appointment_id = request.GET.get('appointment_id')
    rating = request.GET.get('rating')
    feedback = request.GET.get('feedback', '')  # Optional feedback for hospital
    comment = request.GET.get('comment', '')  # Optional comment for doctor

    try:
        # Ensure that hospital and doctor exist
        hospital = Hospital.objects.get(id=hospital_id)
        doctor = Doctor.objects.get(id=doctor_id)
        appointment = Appointment.objects.get(id=appointment_id)

        # Validate the rating is provided
        if not rating:
            messages.error(request, "Please provide a rating.")
            return redirect('past_appointments')

        # Save the hospital feedback if it's provided
        if feedback and comment:
            HospitalFeedback.objects.create(
                hospital=hospital,
                patient=patient,
                rating=rating,
                feedback=feedback
            )
            Review.objects.create(
                doctor=doctor,
                patient=patient,
                rating=rating,
                comment=comment
            )
            messages.success(request, "Thank you for providing feedback for the hospital and doctor!")

        # Redirect to the patient dashboard after submission
        return redirect('patient_dashboard')

    except ValidationError as e:
        messages.error(request, f"Validation Error: {e}")
    except Hospital.DoesNotExist:
        messages.error(request, "The hospital does not exist.")
    except Doctor.DoesNotExist:
        messages.error(request, "The doctor does not exist.")
    except Appointment.DoesNotExist:
        messages.error(request, "Appointment not found.")
    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {str(e)}")

    # Redirect back to the appointment details if there was an error
    return redirect('past_appointments')


def reviews(request):
    if 'user_id' not in request.session:
        return redirect('login')  # Ensure the user is logged in before submitting feedback or review

    patient = Patient.objects.get(id=request.session['user_id'])

    appointment_id = request.GET.get('appointment_id')
    doctor_id = request.GET.get('doctor_id')
    hospital_id = request.GET.get('hospital_id')
    patient_id = request.GET.get('patient_id')

    # If you need to use the appointment, doctor, or hospital in the view
    appointment = Appointment.objects.get(id=appointment_id) if appointment_id else None
    doctor = Doctor.objects.get(id=doctor_id) if doctor_id else None
    hospital = Hospital.objects.get(id=hospital_id) if hospital_id else None

    return render(request, 'Patients/reviews.html',
                  {'patient': patient, 'appointment': appointment, 'doctor': doctor, 'hospital': hospital})
def logout(request):
    if request.method == 'POST':
        # Check if the 'user_id' exists in the session
        if 'user_id' in request.session:
            # Clear the session to log the user out
            del request.session['user_id']
            messages.success(request, "You have successfully logged out.")
        else:
            # If there's no 'user_id', they aren't logged in
            messages.error(request, "You are not logged in.")

        # Redirect to the login page or homepage
        return redirect('login')