from navyojan.models import BaseModel

import django_filters

from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField

class Documents(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    display_name = models.CharField(max_length=255, unique=True, null=True)
    description = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = ''.join(word.capitalize() for word in self.name.split('_'))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.display_name

class Eligibility(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    display_name = models.CharField(max_length=255, unique=True, null=True)
    description = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = ''.join(word.capitalize() for word in self.name.split('_'))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.display_name

class ScholarshipData(BaseModel):
    title = models.CharField(max_length=255,null=True)
    eligibility = models.ManyToManyField(Eligibility,related_name='scholarships',blank=True)
    document_needed = models.ManyToManyField(Documents,related_name='scholarships',blank=True)
    how_to_apply = ArrayField(models.CharField(null=True,blank=True,max_length=512),default=list,null=True,blank=True)
    amount = models.IntegerField(null=True,blank=True)      #filter
    published_on = models.DateField(null = True,default=None,blank=True)   #filter
    state = models.CharField(null = True ,max_length=255,default=None,blank=True)   #skip filter for time being
    deadline = models.DateField(null=True,default=None,blank=True)    #filtered by default
    link = models.URLField(null=True,default=None,blank=True)
    categories = models.ManyToManyField('Category', related_name='scholarships', blank=True)  #filter
    is_approved = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.id} - {self.title}"
class Category(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    display_name = models.CharField(max_length=255, unique=True, null=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

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