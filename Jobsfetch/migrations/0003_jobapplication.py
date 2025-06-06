# Generated by Django 5.1.6 on 2025-02-24 07:59

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Jobsfetch', '0002_job_experience_required_job_url_alter_job_job_id_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='JobApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interview_date', models.CharField(default='', max_length=20)),
                ('applied_at', models.DateTimeField(auto_now_add=True)),
                ('jobid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Jobsfetch.job')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
