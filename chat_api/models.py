from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class EachUserSession(models.Model):
    related_user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="sessions")
    topic = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.related_user.username}'s {self.topic}"
    

class ChatMessages(models.Model):
    related_Session = models.ForeignKey(EachUserSession,on_delete=models.CASCADE,related_name="messages")
    content = models.TextField(blank=False)
    isUser = models.BooleanField()

    def __str__(self):
        return f"{self.related_Session.topic}'s Messages"