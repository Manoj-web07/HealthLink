from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from .models import Patient, Doctor, Hospital, Appointment, HospitalFeedback,Staff,Treatment,Disease
from django.utils.timezone import make_aware
from datetime import datetime,timedelta
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
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
    # Ensure the user is logged in
    if 'user_id' not in request.session:
        return redirect('login')  # Redirect if the patient is not logged in

    # Fetch the patient object using session data
    try:
        patient = Patient.objects.get(id=request.session['user_id'])
    except Patient.DoesNotExist:
        return redirect('login')  # Redirect if patient doesn't exist

    # Retrieve the filter criteria from the request
    treatment_type = request.GET.get('treatment_type', '')
    disease = request.GET.get('disease', '')
    hospital = request.GET.get('hospital', '')
    city = request.GET.get('city', '')
    nearby = request.GET.get('nearby', False)

    # Filter doctors based on treatment type
    doctors = Doctor.objects.all()

    # Filter by treatment type if provided
    if treatment_type:
        doctors = doctors.filter(treatment_type=treatment_type)

    # Filter by disease if provided
    if disease:
        doctors = doctors.filter(diseases__id=disease)

    # Filter by hospital if provided
    if hospital:
        doctors = doctors.filter(hospital__id=hospital)

    # Filter by city if provided
    if city:
        doctors = doctors.filter(city__icontains=city)

    # Optionally filter by nearby doctors if "nearby" is selected (you can add more complex logic based on geolocation)
    if nearby and city:
        # Implement logic for finding nearby doctors (this example assumes city is enough for now)
        # You could enhance this with geolocation or use an external API if you prefer
        pass

    # Get available diseases for the filter
    diseases = Disease.objects.all()

    # Get available hospitals for the filter
    hospitals = Hospital.objects.all()

    context = {
        'patient': patient,
        'doctors': doctors,
        'diseases': diseases,
        'hospitals': hospitals,
        'active_page': 'doctor-listing',
    }

    return render(request, 'Patients/doctor-listing.html', context)