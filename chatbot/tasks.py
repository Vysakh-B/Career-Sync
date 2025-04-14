import random
from datetime import datetime
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from credentials.models import Registration

INTERVIEW_TIPS = [
    "Always tailor your resume for the job you're applying to.",
    "Be honest about your skills – authenticity wins.",
    "Use the STAR method (Situation, Task, Action, Result) for behavioral questions.",
    "Research the company’s mission and culture before the interview.",
    "Ask thoughtful questions at the end of the interview.",
    "Dress appropriately, even for virtual interviews.",
    "Keep answers concise and focused – avoid rambling.",
    "Practice common questions like 'Tell me about yourself.'",
    "Follow up with a thank-you email after the interview.",
    "Demonstrate a growth mindset by sharing how you learn from mistakes.",
]

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
                time_str_12h = f"{ft['hour']}:{ft['minute']} {ft['period']}"
                time_24h = datetime.strptime(time_str_12h, "%I:%M %p").strftime("%H:%M")

                print(f"Checking if {time_24h} == {current_time_str}")

                if current_time_str == time_24h:
                    print(f"Sending mail to {reg.user.email}")

                    random_tip = random.choice(INTERVIEW_TIPS)

                    subject = "Your Daily Interview Tip – Stay Sharp with Career Sync!"
                    from_email = "career.sync.ai@gmail.com"
                    to_email = [reg.user.email]

                    context = {
                        'username': reg.user.username,
                        'tip': random_tip,
                    }

                    text_content = f"Hi {context['username']},\n\n{context['tip']}\n\nGood luck!\nTeam Career Sync"
                    html_content = render_to_string('email_templates/interview_tip.html', context)

                    msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()

        except Exception as e:
            print(f"Error sending mail to {reg.user.email}: {str(e)}")
