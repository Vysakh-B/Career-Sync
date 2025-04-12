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
from django.core.mail import send_mail

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator


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

        if not reg.interested_fields:
            return True  # No interest fields, but not an error

        job_query = " OR ".join(reg.interested_fields.split(','))
        delays = "1 day ago"

        url = "https://jsearch.p.rapidapi.com/search"
        headers = {
            "X-RapidAPI-Key": "97a33a383bmsh833011f8404780cp103a9ejsn86557266b941",
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }
        params = {
            "query": job_query,
            "page": 1,
            "num_pages": 1,
            "job_posted_human_readable": delays
        }

        response = requests.get(url, headers=headers, params=params, timeout=5)
        response.raise_for_status()  # Raises HTTPError for bad responses

        jobs_data = response.json()

        for job in jobs_data.get("data", []):
            Job.objects.update_or_create(
                job_id=job.get("job_id", ""),
                defaults={
                    "user": user,
                    "title": job.get("job_title", "No Title"),
                    "company": job.get("employer_name", "Unknown"),
                    "location": job.get("job_location", "Not Specified"),
                    "description": job.get("job_description", ""),
                    "salary": job.get("job_salary", 0) or 0,
                    "experience_required": job.get("job_experience", 0) or 0,
                    "url": job.get("job_apply_link", ""),
                    "job_posted": job.get("job_posted_human_readable", "1 day ago"),
                    "qualification": json.dumps(job.get("job_highlights", {}).get("Qualifications", [])),
                    "responsibilities": json.dumps(job.get("job_highlights", {}).get("Responsibilities", [])),
                }
            )

        reg.last_fetched_at = now()
        reg.save()
        return True

    except requests.exceptions.RequestException:
        return False  # Network or API error
    except Registration.DoesNotExist:
        return True  # No registration is not an error in this case
# Modified sign-in view

def signin(request):
    if request.method == 'POST':
        email = request.POST['email']
        pswd = request.POST['password']
        user = authenticate(request, username=email, password=pswd)

        if user is not None:

            reg = Registration.objects.filter(user=user).first()
            if reg and (not reg.last_fetched_at or now() - reg.last_fetched_at > timedelta(hours=24)):
                result = fetch_jobs_for_user(user)
                if not result:
                    return redirect('not_found')  # This should be the name of your 404 URL
            login(request, user)

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
        currentsalary = request.POST.get("salary", "").strip()
        currentsalary = int(currentsalary) if currentsalary.isdigit() else 0 

        
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
    flag = False
    success_flag = False
    errormsg = ""
    if request.method == "POST":
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        user_email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        if not fname:
            flag = True
            errormsg = "First name is required."
            return render(request,'contact.html',{'flag':flag,'sf':success_flag,'err':errormsg})
        elif not lname:
            flag = True
            errormsg = "Last name is required."
            return render(request,'contact.html',{'flag':flag,'sf':success_flag,'err':errormsg})
        elif not user_email:
            flag = True
            errormsg = "Email is required."
            return render(request,'contact.html',{'flag':flag,'sf':success_flag,'err':errormsg})
        elif not subject:
            flag = True
            errormsg = "Subject is required."
            return render(request,'contact.html',{'flag':flag,'sf':success_flag,'err':errormsg})
        elif not message:
            flag = True
            errormsg = "Message cannot be empty."
            return render(request,'contact.html',{'flag':flag,'sf':success_flag,'err':errormsg})
        else:

            # Compose the full email body
            email_body = f"""
            You received a new message from the contact form.

            Name: {fname} {lname}
            Email: {user_email}

            Subject: {subject}

            Message:
            {message}
            """

            try:
                send_mail(
                    subject=f"Contact Form - {subject}",
                    message=email_body,
                    from_email='career.sync.ai@gmail.com',
                    recipient_list=['career.sync.ai@gmail.com'],
                    fail_silently=False,
                )
                # messages.success(request, "Your message was sent successfully.")
                success_flag=True
                errormsg = "Your message was sent successfully."

            except Exception as e:
                print("Error sending email:", e)
                # messages.error(request, "There was an error sending your message. Please try again later.")
                flag = True
                errormsg = "There was an error sending your message. Please try again later.."

            return render(request,'contact.html',{'flag':flag,'sf':success_flag,'err':errormsg})  # Adjust this if your URL name is different
    return render(request,'contact.html',{'flag':flag,'sf':success_flag,'err':errormsg})

def forgot_password(request):
    flg = False
    errormsg = ""
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            flg = True
            errormsg='Please enter an email.'
            return render(request,'forgot_password.html',{'flg':flg,'err':errormsg})
        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = request.build_absolute_uri(f'/reset-password/{uid}/{token}/')
            
            # Send email
            send_mail(
                'Password Reset Request - Career Sync',
                f'Hi {user.username},\n\nClick the link below to reset your password:\n{reset_link}\n\nIf you did not request this, ignore this email.',
                'career.sync.ai@gmail.com',
                [user.email],
                fail_silently=False,
            )
            flg = True
            errormsg='Password reset link has been sent to your email.'
            return render(request,'forgot_password.html',{'flg':flg,'err':errormsg})
        except User.DoesNotExist:
            flg = True
            errormsg='No account found with that email.'
    return render(request,'forgot_password.html',{'flg':flg,'err':errormsg})

def reset_password_view(request, uidb64, token):
    flg = False
    errormsg = ""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError, OverflowError):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('password')
            confirm_password = request.POST.get('confirmPassword')
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                flg = True
                errormsg = 'Your password has been reset. You can now log in.'
                return redirect('signin')
            else:
                flg = True
                errormsg = 'Passwords do not match.'
                # messages.error(request, 'Passwords do not match.')

        return render(request, 'reset_password.html', {'validlink': True,'flg':flg,'err':errormsg})
    else:
        return render(request, 'reset_password.html', {'validlink': False,'flg':flg,'err':errormsg})
def not_found(request):
    return render(request,'404_page.html')