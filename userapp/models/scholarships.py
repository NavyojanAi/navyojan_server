from django.db import models
from navyojan.models import BaseModel
from django.contrib.auth.models import User
from django.utils import timezone

class ScholarshipData(BaseModel):
    title = models.CharField(max_length=255)
    # description = models.TextField()
    eligibility = models.TextField(null=True,blank=True)
    # amount = models.DecimalField(max_digits=7, decimal_places=2) 
    document_needed = models.TextField(null=True,blank=True)
    how_to_apply = models.TextField(null=True,blank=True)
    published_on = models.DateField(default=timezone.now)
    state = models.CharField(max_length=255,default=None)
    deadline = models.DateField(default=timezone.now) 
    link = models.URLField(default=None)
    category = models.CharField(max_length=255,null=True)   #not a mandatory field
    # created_at = models.DateTimeField(auto_now_add=True)   #notes the time when the scholarship was added
    categories = models.ManyToManyField('Category', related_name='scholarships', blank=True)
    
    
    def __str__(self):
        return f"{self.id} - {self.title}"
    
    
class Category(BaseModel):
    CATEGORY_CHOICES = [
        ("MERIT", "Merit"),
        ("FEMALE", "Female"),
        ("MALE", "Male"),
        ("SPORTS", "Sports"),
        ("COLLEGE LEVEL", "College Level"),
        ("MINORITIES", "Minorities"),
        ("TALENT BASED", "Talent Based"),
        ("DIFFERENTLY ABLED", "Differently Abled"),
        ("SCHOOL LEVEL", "School Level"),
    ]

    name = models.CharField(max_length=255, unique=True, choices=CATEGORY_CHOICES)
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