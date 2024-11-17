from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
import random

from navyojan.models import BaseModel
from scripts import encrypt_data,decrypt_data

class EmailVerification(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6, validators=[RegexValidator(r'^\d{1,6}$')])
    
    def save(self, *args, **kwargs):
        self.otp = ''.join(random.choice('0123456789') for i in range(6))
        self.otp = encrypt_data(self.otp)
        super(EmailVerification, self).save(*args, **kwargs)
