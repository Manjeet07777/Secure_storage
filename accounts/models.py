from django.db import models
from django.contrib.auth.models import User

class StoredFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    original_filename = models.CharField(max_length=255)
    stored_filename = models.CharField(max_length=255)  # actual saved file name
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.original_filename
