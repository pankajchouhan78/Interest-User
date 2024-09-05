from django.db import models
from django.contrib.auth.models import AbstractUser, User


class Interest_User(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    interest_list = models.ManyToManyField(
        User, blank=True, related_name="interested_by", symmetrical=False
    )


class Interest(models.Model):
    from_user = models.ForeignKey(
        User, related_name="sent_interests", on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(
        User, related_name="received_interests", on_delete=models.CASCADE
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.from_user} to {self.to_user} "


class ChatMessage(models.Model):
    sender = models.ForeignKey(
        User, related_name="sent_messages", on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        User, related_name="received_messages", on_delete=models.CASCADE
    )
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} to {self.receiver}: {self.message}"
