import uuid

from django.contrib.auth.models import User
from django.db import models


class ApiToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_tokens')
    key = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = uuid.uuid4().hex
        super().save(*args, **kwargs)

    def __str__(self):
        return f"ApiToken(user={self.user.username}, key={self.key})"
