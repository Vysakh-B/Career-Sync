from datetime import datetime
from celery import shared_task
from django.core.mail import send_mail
from credentials.models import Registration

@shared_task
def send_interview_tips_task():
    now = datetime.now()
    current_time_str = now.strftime("%H:%M")
    print("Current time:", current_time_str)

    users_to_notify = Registration.objects.all()
    for reg in users_to_notify:
        try:
            free_times = reg.get_free_time()  # [{'hour': '12', 'minute': '00', 'period': 'AM'}, ...]

            for ft in free_times:
                # Convert to 24-hour format
                time_str_12h = f"{ft['hour']}:{ft['minute']} {ft['period']}"
                time_24h = datetime.strptime(time_str_12h, "%I:%M %p").strftime("%H:%M")

                print(f"Checking if {time_24h} == {current_time_str}")

                if current_time_str == time_24h:
                    print(f"Sending mail to {reg.user.email}")
                    send_mail(
                        'Your Interview Tip!',
                        'Here’s your daily tip for interview prep...',
                        'career.sync.ai@gmail.com',
                        [reg.user.email],
                        fail_silently=False
                    )
        except Exception as e:
            print(f"Error sending mail to {reg.user.email}: {str(e)}")
