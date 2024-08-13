from django.db import models
from navyojan.models import BaseModel
from django.contrib.auth.models import User
from django.utils import timezone

class ScholarshipData(BaseModel):
    title = models.CharField(max_length=255,null=True)
    eligibility = models.TextField(null=True,blank=True)
    document_needed = models.TextField(null=True,blank=True)
    how_to_apply = models.TextField(null=True,blank=True)
    published_on = models.DateField(null = True,default=None,blank=True)
    state = models.CharField(null = True ,max_length=255,default=None,blank=True)
    deadline = models.DateField(null=True,default=None,blank=True)
    link = models.URLField(null=True,default=None,blank=True)
    categories = models.ManyToManyField('Category', related_name='scholarships', blank=True)
    
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