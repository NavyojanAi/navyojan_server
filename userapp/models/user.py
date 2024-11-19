from django.db import models
from django.contrib.auth.models import User

from navyojan.models import BaseModel
from userapp.validators import validate_pdf
from userapp.models import Category,ScholarshipData,SubscriptionPlan
from django.utils import timezone

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
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    education_level = models.CharField(max_length=50, blank=True)
    field_of_study = models.CharField(max_length=100, blank=True)

    #following are permission assigned based on user's package
    is_reviewer = models.BooleanField(default=False)
    is_host_user= models.BooleanField(default=False) # True if he is scholarshipprovider
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE,blank=True, null=True, related_name='userprofiles')

class UserProfileScholarshipProvider(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name="hostprofile")
    organisation = models.CharField(max_length=40,blank=True)
    org_site = models.URLField(blank=True)
    hosted_scholarships = models.ManyToManyField(ScholarshipData,related_name='host')

    can_host_scholarships = models.BooleanField(default=False)

# ScholarshipData.host = who actually hosted it 
# ScholarshipData.host.user.email


# THIS KEEPS TRACK OF FOR WHICH SCHOLARSHIP ARE OPENED FOR USERS AND ARE APPROVED OR REJECTED BY ADMIN
class UserScholarshipStatus(BaseModel):
    STATUS=(
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected','Rejected')
    )
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    scholarship = models.ForeignKey(ScholarshipData,on_delete=models.CASCADE)
    status = models.CharField(max_length = 10, default="pending", choices = STATUS)
    
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
    
    

class UserSubscriptionInfo:
    def __init__(self,user):
        self.user = user 

    def is_subscribed(self):
        return self.user.plan_tracker.filter(end_date__gte=timezone.now()).exists()

    def get_current_plan(self):
        current_plan = self.user.plan_tracker.filter(end_date__gte=timezone.now()).order_by('-plan__amount').first()
        return current_plan.plan if current_plan else None

    def is_eligible_for_auto_apply(self):
        current_plan = self.get_current_plan()
        return current_plan and current_plan.title == "Get Notified and Auto Apply"          
    
    
# user = User.objects.get(id=1)
# subscription_info = UserSubscriptionInfo(user)
# print(subscription_info.is_subscribed())
# print(subscription_info.get_current_plan())
# print(subscription_info.is_eligible_for_auto_apply())

# is_subscribed() method checks if the user has any active subscription plan. It returns True if there's any UserPlanTracker entry for this user with an end date in the future.
# get_current_plan() method retrieves the current active plan for the user. If the user has multiple active plans, it returns the most expensive one.
# is_eligible_for_auto_apply() checks if the user's current plan is the "Get Notified and Auto Applied" plan.