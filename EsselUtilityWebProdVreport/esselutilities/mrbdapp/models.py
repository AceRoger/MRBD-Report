from django.db import models

# Create your models here.

class MeterImage(models.Model):
	meter_image = models.ImageField(upload_to='meter_reading')

class SuspiciousActivityImage(models.Model):
	suspicious_activity_image = models.ImageField(upload_to='suspicious_activity')

class UserProfileImage(models.Model):
	profile_image = models.ImageField(upload_to='user_profile')

class QrTemperedImage(models.Model):
	qr_tempered_image = models.ImageField(upload_to='qr_tempered')