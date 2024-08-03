from django.db import models
from navyojan.models import BaseModel
from django.contrib.auth.models import User

class UserProfile(BaseModel):
    ACCOUNT_TYPE_CHOICES = (
        ('regular', 'Regular'),
        ('google', 'Google'),
    )
    account_type = models.CharField(max_length=7, choices=ACCOUNT_TYPE_CHOICES,null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name="userprofile")
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    education_level = models.CharField(max_length=50, blank=True)
    field_of_study = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=50, blank=True)
    is_email_verified = models.BooleanField(default=False)
    is_phone_number_verified = models.BooleanField(default=False)

    #following are permission assigned based on user's package 
    free_account_privilages = models.BooleanField(default=True)
    premium_account_privilages = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.account_type}"
    
class OTP(BaseModel):
    OTP_TYPE_CHOICES = (
        ('phone', 'Phone'),
        ('email', 'Email'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    otp_type = models.CharField(max_length=5, choices=OTP_TYPE_CHOICES)
    verified = models.BooleanField(default=False)