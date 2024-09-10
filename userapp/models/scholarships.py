from navyojan.models import BaseModel

import django_filters

from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField

class ScholarshipData(BaseModel):
    title = models.CharField(max_length=255,null=True)
    eligibility = ArrayField(models.CharField(null=True,blank=True,max_length=20),default=None,null=True,blank=True)
    document_needed = ArrayField(models.CharField(default=None,null=True,blank=True,max_length=20),default=None,null=True,blank=True)
    how_to_apply = ArrayField(models.CharField(null=True,blank=True,max_length=20),default=None,null=True,blank=True)
    amount = models.IntegerField(null=True,blank=True)      #filter
    published_on = models.DateField(null = True,default=None,blank=True)   #filter
    state = models.CharField(null = True ,max_length=255,default=None,blank=True)   #skip filter for time being
    deadline = models.DateField(null=True,default=None,blank=True)    #filtered by default
    link = models.URLField(null=True,default=None,blank=True)
    categories = models.ManyToManyField('Category', related_name='scholarships', blank=True)  #filter
    
    def __str__(self):
        return f"{self.id} - {self.title}"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default filter for deadline
        self.filters['deadline'] = django_filters.DateFilter(field_name='deadline', lookup_expr='gte', initial=now)
        self.filters['deadline'].extra.update({
            'initial': now()
        })
    
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