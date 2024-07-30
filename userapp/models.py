from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    education_level = models.CharField(max_length=50, blank=True)
    field_of_study = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=50, blank=True)

#add preference field here to map to the scholarship data


    def __str__(self):
        return self.user.username


class ScholarshipData(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    eligibility = models.TextField()
    amount = models.CharField(max_length=100)  # Changed from DecimalField to CharField
    deadline = models.CharField(max_length=100)  # Changed from DateField to CharField
    link = models.URLField()

    def __str__(self):
        return self.title
    


class UserScholarshipsData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='scholarship_applications')
    scholarship = models.ManyToManyField(ScholarshipData, on_delete=models.CASCADE, related_name='applications')
    applied_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Seen', choices=[
        ('Interested', 'Interested'),   #sent the message for this to the user and its relevancy
        ('Applied', 'Applied'),
        # ('Interested but Not Applied','Interested but Not Applied'),
        ('Interested and Applied', 'Interested and Applied'),
        # ('Not Interested but Applied', 'Not Interested '),
        ('Seen', 'Seen'),
    ])

    class Meta:
        unique_together = ('user', 'scholarship')

    def __str__(self):
        return f"{self.user.username} - {self.scholarship.title}"