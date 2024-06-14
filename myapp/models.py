from django.db import models
# auth_app/models.py
from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import datetime, timedelta

class OTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = datetime.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)

# Model to store images and dates
class Driver_info(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    plate = models.CharField(max_length=100)

    def __str__(self):
        return self.plate

class Images(models.Model):
    image = models.ImageField(upload_to='images/')
    received_at = models.DateTimeField(auto_now_add=True)
    driver = models.ForeignKey(Driver_info, on_delete=models.CASCADE)
    intersection = models.CharField(max_length=255, default="Chinhoyi Intersection Robot A")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, default=-17.353175)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, default=30.205885)
    camera_id = models.CharField(max_length=255, default="1")
    extract_text = models.CharField(max_length=255, default="True")

    def __str__(self):
        return f"Image from {self.intersection} at {self.received_at} - ({self.latitude}, {self.longitude})"

class UploadedImage(models.Model):
    image = models.ImageField(upload_to='tids/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.image.name