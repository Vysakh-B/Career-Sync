from django.db import models
from django.contrib.auth.models import User  # Using Django's default User model

class ChatSession(models.Model):
    """
    Represents a unique chat session for a user applying to a company position.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    position_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'company_name', 'position_name')  # Ensures one session per user-company-position

    def __str__(self):
        return f"{self.user.username} - {self.company_name} - {self.position_name}"

class ChatMessage(models.Model):
    """
    Stores all chat messages linked to a specific ChatSession.
    """
    chat_session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=[('user', 'User'), ('ai', 'AI')])  
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.chat_session} - {self.sender}: {self.message[:30]}..."
