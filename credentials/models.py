from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
import json

class Registration(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    experienced = models.BooleanField(default=False)
    years = models.PositiveIntegerField(default=0)
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    interested_fields = models.TextField(help_text="Comma-separated job fields")
    free_time = models.JSONField(default=list, help_text="List of free time slots in JSON format")
    last_fetched_at = models.DateTimeField(null=True, blank=True)  # Track last API fetch time

    def set_free_time(self, times):
        """Store free time as JSON list."""
        self.free_time = json.dumps(times)

    def get_free_time(self):
        """Retrieve free time as Python list."""
        return json.loads(self.free_time) if self.free_time else []
    
    def __str__(self):
        return self.user.email
