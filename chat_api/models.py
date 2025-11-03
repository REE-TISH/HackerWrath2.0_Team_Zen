from django.db import models

# Create your models here.


class EachUserChat(models.Model):
    user_id = models.CharField(max_length=100, unique=True)
    chat_history = models.JSONField(default=list)

    def __str__(self):
        return self.user_id