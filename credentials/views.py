from django.contrib.auth.models import User,auth
from django.contrib.auth.decorators import login_required
import json
from django.contrib.auth import logout as auth_logout
from . models import Registration
from django.shortcuts import render, redirect
import re
from django.contrib.auth import authenticate, login
from django.utils.timezone import now
from datetime import timedelta
import requests
from Jobsfetch.models import Job,JobApplication
from chatbot.models import ChatSession

# Create your views here.
def logout(request):
    if request.user.is_authenticated:
        ChatSession.objects.filter(user=request.user, jobid=None).delete()
    # Call Django's built-in logout function to clear the session and log out the user
    auth_logout(request)
    
    return redirect('index') 
def index(request):
    jobdatas = []
    if request.user.is_authenticated:
        user=request.user
        jobdatas = Job.objects.filter(user=user).order_by('-posted_at')[:5]
    return render(request,'index.html',{'data':jobdatas})
def applied(request):
    if request.user.is_authenticated:
        user_applied_jobs = Job.objects.filter(
            id__in=JobApplication.objects.filter(user=request.user).values_list('jobid', flat=True)
        )
    else:
        user_applied_jobs = Job.objects.none()  # Empty queryset if the user is not logged in
    return render(request,'applied.html',{'data':user_applied_jobs})
# Function to fetch jobs for a user

def fetch_jobs_for_user(user):
    try:
        reg = Registration.objects.get(user=user)

        # Ensure user has interested fields
        if not reg.interested_fields:
            return

        # Convert comma-separated fields into a search query
        job_query = " OR ".join(reg.interested_fields.split(','))
        delays = "1 day ago"

        url = "https://jsearch.p.rapidapi.com/search"
        headers = {
            "X-RapidAPI-Key": "97a33a383bmsh833011f8404780cp103a9ejsn86557266b941",
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }
        params = {
            "query": job_query,
            "page": 1,  # Fetch first page
            "num_pages": 1,  # Number of pages to fetch
            "job_posted_human_readable": delays
        }

        response = requests.get(url, headers=headers, params=params)
        jobs_data = response.json()

        # Save jobs in the database
        for job in jobs_data.get("data", []):  # Get job list safely
            Job.objects.update_or_create(
                job_id=job.get("job_id", ""),  # Use .get() to prevent KeyErrors
                defaults={
                    "user": user,
                    "title": job.get("job_title", "No Title"),  # If title is missing, set default
                    "company": job.get("employer_name", "Unknown"),
                    "location": job.get("job_location", "Not Specified"),
                    "description": job.get("job_description", ""),
                    "salary": job.get("job_salary", 0) or 0,
                    "experience_required": job.get("job_experience", 0) or 0,
                    "url": job.get("job_apply_link", ""),
                    "job_posted": job.get("job_posted_human_readable", "1 day ago"),
                    # Store qualifications & responsibilities as JSON strings
                    "qualification": json.dumps(job.get("job_highlights", {}).get("Qualifications", [])),
                    "responsibilities": json.dumps(job.get("job_highlights", {}).get("Responsibilities", [])),
                }
            )

        # Update last fetched time
        reg.last_fetched_at = now()
        reg.save()

    except Registration.DoesNotExist:
        pass  # User does not have a registration profile

# Modified sign-in view
def signin(request):
    if request.method == 'POST':
        email = request.POST['email']
        pswd = request.POST['password']
        user = authenticate(request, username=email, password=pswd)

        if user is not None:
            login(request, user)

            # Fetch jobs only if 24 hours have passed
            reg = Registration.objects.filter(user=user).first()
            if reg and (not reg.last_fetched_at or now() - reg.last_fetched_at > timedelta(hours=24)):
                fetch_jobs_for_user(user)

            return redirect('index')
        else:
            return render(request, 'login.html', {'data': 'Invalid credentials', 'fg': True})

    return render(request, 'login.html')


def signup(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        repassword = request.POST.get('repassword', '')
        experience = request.POST.get("experience") == "on"
        year = request.POST.get('year', 0)
        if year == "":
            year=0
        # if experience:
        #     if year < 1:
        #         err = "if experienced atleast on year is required."
        #         ch = True
        #         return render(request, 'signup.html', {'data': err, 'chk': ch})
        # else:
        #     year=0
        year = int(year)
        # currentsalary = request.POST.get("salary")
        currentsalary = request.POST.get("salary", "").strip()
        
        # currentsalary = int(currentsalary) if currentsalary.isdigit() else 0
        interested = request.POST.get("job_fields", "")
        job_fields_list = interested.split(",") if interested else []
        free_time_json = request.POST.get("freetime", "[]")
        try:
            free_time_list = json.loads(free_time_json)
        except json.JSONDecodeError:
            free_time_list = []

        # Convert free time to a readable string
        free_time_str = json.dumps(free_time_list, indent=2)

        ch = False
        # Validate email format
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email):
            err = "Invalid Email format"
            ch = True
            return render(request, 'signup.html', {'data': err, 'chk': ch})  

        if User.objects.filter(email=email).exists():
            err = "User already exists"
            ch = True
            return render(request, 'signup.html', {'data': err, 'chk': ch})  

        if password != repassword:
            err = "Passwords do not match"
            ch = True
            return render(request, 'signup.html', {'data': err, 'chk': ch})  

        if len(password) < 8:
            err = "Password must be at least 8 characters long."
            ch = True
            return render(request, 'signup.html', {'data': err, 'chk': ch})

        if not re.search(r'\d', password):
            err = "Password must contain atleast one number."
            ch = True
            return render(request, 'signup.html', {'data': err, 'chk': ch})
        if experience:
            if year < 1:
                err = "if experienced atleast on year is required."
                ch = True
                return render(request, 'signup.html', {'data': err, 'chk': ch})
            if currentsalary:  # Check if there is a value
                try:
                    currentsalary = int(currentsalary)
                except ValueError:
                    err = "Invalid salary"
                    ch = True
                    return render(request, 'signup.html', {'data': err, 'chk': ch})
            else:
                err = "if experienced salary is required."
                ch = True
                return render(request, 'signup.html', {'data': err, 'chk': ch})

        if not job_fields_list:  # Check if the list is empty
            err = "Please select atleast one interested field"
            ch = True
            return render(request, 'signup.html', {'data': err, 'chk': ch})


        # Create the user
        user = User.objects.create_user(username=email, email=email, password=password)
        user.save()

        # Create the Registration record
        Reg = Registration.objects.create(
            user=user,
            experienced=experience,
            years=year,
            salary=currentsalary,
            interested_fields=", ".join(job_fields_list),
            free_time=free_time_str
        )
        Reg.save()

        return redirect('signin')

    return render(request, 'signup.html')

def contact(request):
    return render(request,'contact.html')