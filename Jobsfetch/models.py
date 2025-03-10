from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Job(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job_id = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    salary = models.IntegerField(default=0)
    experience_required = models.IntegerField(default=0)
    url = models.URLField(blank=True, null=True)
    job_posted = models.CharField(max_length=100,blank=True)
    posted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id}"  # Updated here


class JobApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    jobid = models.ForeignKey(Job, on_delete=models.CASCADE)
    interview_date = models.CharField(max_length=20,default="")
    applied_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"{self.user.username} applied for Job ID {self.jobid}"  # Updated here




