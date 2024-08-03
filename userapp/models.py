from django.db import models
from navyojan.models import BaseModel
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(BaseModel):
    ACCOUNT_TYPE_CHOICES = (
        ('regular', 'Regular'),
        ('google', 'Google'),
    )
    account_type = models.CharField(max_length=7, choices=ACCOUNT_TYPE_CHOICES,null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    education_level = models.CharField(max_length=50, blank=True)
    field_of_study = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.account_type}"


class ScholarshipData(BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    eligibility = models.TextField()
    amount = models.DecimalField(max_digits=7, decimal_places=2) 
    deadline = models.DateField() 
    link = models.URLField()

    def __str__(self):
        return f"{self.id} - {self.title}"
    


class UserScholarshipApplicationData(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scholarship_applications')
    scholarship = models.ForeignKey(ScholarshipData,on_delete=models.CASCADE,related_name='applicants')
    is_interested = models.BooleanField(default=False)
    is_applied = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'scholarship')

    def __str__(self):
        return f"{self.user.username} - {self.scholarship.title}"