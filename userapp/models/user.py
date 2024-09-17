from django.db import models
from django.contrib.auth.models import User

from navyojan.models import BaseModel
from userapp.validators import validate_pdf
from userapp.models import Category,ScholarshipData


class BaseUserProfile(BaseModel):
    ACCOUNT_TYPE_CHOICES = (
        ('regular', 'Regular'),
        ('google', 'Google'),
    )
    
    GENDER_CHOICES = (
        ('male','Male'),
        ('female','Female'),
        ('others','Others'),
    )
    
    # opted_categories = models.ManyToManyField('scholarships.Category', related_name='opted_users', blank=True)
    account_type = models.CharField(max_length=7, choices=ACCOUNT_TYPE_CHOICES,null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True)
    gender = models.CharField(max_length = 10, blank=True, choices = GENDER_CHOICES)  #default to be removed later
    is_email_verified = models.BooleanField(default=False)
    is_phone_number_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.account_type}"

class UserProfile(BaseUserProfile):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name="userprofile")
    education_level = models.CharField(max_length=50, blank=True)
    field_of_study = models.CharField(max_length=100, blank=True)

    #following are permission assigned based on user's package
    is_reviewer = models.BooleanField(default=False)
    is_host_user= models.BooleanField(default=False) # True if he is scholarshipprovider
    free_account_privilages = models.BooleanField(default=True)
    premium_account_privilages = models.BooleanField(default=False)

class UserProfileScholarshipProvider(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name="hostprofile")
    organisation = models.CharField(max_length=40,blank=True)
    org_site = models.URLField(blank=True)
    hosted_scholarships = models.ManyToManyField(ScholarshipData,related_name='host')

    can_host_scholarships = models.BooleanField(default=False)

class UserScholarshipStatus(BaseModel):
    STATUS=(
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected','Rejected')
    )
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    scholarship = models.ForeignKey(ScholarshipData,on_delete=models.CASCADE)
    status = models.CharField(max_length = 10, default="pending", choices = STATUS)
    class Meta:
        permissions = [
            ("can_access_admin_model", "Can access the model in admin"),
        ]
    def __str__(self):
        return f"{self.user.username} - {self.scholarship.title} - {self.status}"

# TODO: Need to setup s3bucket and iam role for django app to store pdfs in cloud. for now its locally stored
class UserDocuments(BaseModel):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='documents')
    certificate_tenth = models.FileField(upload_to='tenth_pdfs/',validators=[validate_pdf],blank=True)
    certificate_inter = models.FileField(upload_to='inter_pdfs/',validators=[validate_pdf],blank=True)
    certificate_disability = models.FileField(upload_to='disability_pdfs/',validators=[validate_pdf],blank=True)
    certificate_sports = models.FileField(upload_to='sports_pdfs/',validators=[validate_pdf],blank=True)

class UserPreferences(BaseModel):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='category_preferences')
    categories = models.ManyToManyField(Category,related_name='users') # NOTE: related name will be used for keeping track of user that have shown preference in this category

    
class OTP(BaseModel):
    OTP_TYPE_CHOICES = (
        ('phone', 'Phone'),
        ('email', 'Email'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="otps")
    otp = models.CharField(max_length=6)
    otp_type = models.CharField(max_length=5, choices=OTP_TYPE_CHOICES)
    verified = models.BooleanField(default=False)