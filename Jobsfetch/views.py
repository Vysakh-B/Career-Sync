from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from .models import JobApplication, Job
from django.shortcuts import redirect
import json
from django.contrib import messages
from chatbot.models import ChatSession

# Create your views here.
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
    return render(request, 'job-single.html', {'data': fetched, 'flg': flg, 'job_description': job_description_preview,'qualification':qual,'responsibilities':resp})
def profile(request):
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
