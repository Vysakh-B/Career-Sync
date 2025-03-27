from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from .models import JobApplication, Job
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
import json
from django.contrib import messages
from chatbot.models import ChatSession

# Create your views here.
@login_required(login_url='index')
def jobs(request):
    user=request.user
    jobdata = Job.objects.filter(user=user)
    # for i in jobdata:
    #     print(i.id)
    return render(request,'job-listings.html',{'data':jobdata})
def jobdetails(request, id):
    fetched = get_object_or_404(Job, id=id)  # Handles non-existent job IDs safely
    job_description = fetched.description.split("•")  # Split by bullet points
    job_description = [point.strip() for point in job_description if point.strip()]  # Remove empty items

    # Keep only the first point as a list (for iteration in template)
    job_description_preview = job_description[:1]  # Returns a list with only the first point

    qual = json.loads(fetched.qualification) if fetched.qualification else []
    resp = json.loads(fetched.responsibilities) if fetched.responsibilities else []
    flg = JobApplication.objects.filter(jobid=fetched, user=request.user).exists()  # Direct check
    jobdatas = Job.objects.filter(user=request.user).order_by('-posted_at')[:5]
    return render(request, 'job-single.html', {'data': fetched, 'flg': flg, 'job_description': job_description_preview,'qualification':qual,'responsibilities':resp,'jobdata':jobdatas})
def profile(request):
    if request.method == 'POST':
        experience = request.POST.get("experience") == "on"
        year = request.POST.get('year', 0)
        if year == "":
            year=0
        year = int(year)
        currentsalary = request.POST.get("salary", "").strip()
        
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
        if experience:
            if year < 1:
                err = "if experienced atleast on year is required."
                ch = True
                return render(request, 'profile.html', {'data': err, 'chk': ch})
            if currentsalary:  # Check if there is a value
                try:
                    currentsalary = int(currentsalary)
                except ValueError:
                    err = "Invalid salary"
                    ch = True
                    return render(request, 'profile.html', {'data': err, 'chk': ch})
            else:
                err = "if experienced salary is required."
                ch = True
                return render(request, 'profile.html', {'data': err, 'chk': ch})

        if not job_fields_list:  # Check if the list is empty
            err = "Please select atleast one interested field"
            ch = True
            return render(request, 'profile.html', {'data': err, 'chk': ch})

    return render(request,'profile.html')
def mark_applied(request):
    if request.method == "POST" and request.user.is_authenticated:
        job_id = request.POST.get("job_id")
        print(job_id)
        job = Job.objects.get(id=job_id)
        user_profile = request.user  # Assuming Profile model

            # Check if the user already applied
        if not JobApplication.objects.filter(user=user_profile, jobid=job).exists():
            JobApplication.objects.create(user=user_profile, jobid=job)
            ChatSession.objects.create(user=user_profile,jobid=job,company_name=job.company,position_name=job.title)
            messages.success(request, "Application status updated!")

        return redirect("jobs")  # Redirect after form submission

    messages.error(request, "Invalid request.")
    return redirect("jobs")
def delete_apply(request,id):
    jid = get_object_or_404(JobApplication, jobid=id)  # Ensures object exists or returns 404
    cht = get_object_or_404(ChatSession, jobid=id)
    jid.delete()  # Delete the object
    cht.delete()
    return redirect("applied")  # Redirect after deletion
