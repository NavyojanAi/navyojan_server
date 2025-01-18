from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
import random

from navyojan.models import BaseModel
from tasks import encrypt_data

class Verification(BaseModel):
    VERIFICATION_CHOICES = [
        ('email', 'Email'),
        ('phone', 'Phone'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(validators=[RegexValidator(r'^\d{1,4}$')])
    verification_type = models.CharField(max_length=5, choices=VERIFICATION_CHOICES)
    
    def save(self, *args, **kwargs):
        self.otp = ''.join(random.choice('0123456789') for i in range(4))
        self.otp = encrypt_data(self.otp)
        super(Verification, self).save(*args, **kwargs)
