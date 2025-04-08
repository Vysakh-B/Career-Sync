from celery import shared_task
from django.utils import timezone
from credentials.models import Registration
from django.core.mail import send_mail

@shared_task
def send_interview_tips_task():
    now = timezone.localtime()
    current_time_str = now.strftime("%H:%M")

    users_to_notify = Registration.objects.all()
    for reg in users_to_notify:
        try:
            free_times = reg.get_free_time()  # e.g., ['14:00', '18:00']
            if current_time_str in free_times:
                send_mail(
                    'Your Interview Tip!',
                    'Here’s your daily tip for interview prep...',
                    'career.sync.ai@gmail.com',  # from email
                    [reg.user.email],
                    fail_silently=False
                )
        except Exception as e:
            print(f"Error sending mail to {reg.user.email}: {str(e)}")
