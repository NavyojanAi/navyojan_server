from django.db import models
from navyojan.models import BaseModel
from django.contrib.auth.models import User


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