from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
import random

from navyojan.models import BaseModel
from tasks import encrypt_data
class EmailVerification(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(validators=[RegexValidator(r'^\d{1,4}$')])
    
    def save(self, *args, **kwargs):
        self.otp = ''.join(random.choice('0123456789') for i in range(4))
        self.otp = encrypt_data(self.otp)
        super(EmailVerification, self).save(*args, **kwargs)
