from django.contrib import admin
from userapp.models import User, UserProfile, ScholarshipData, UserScholarshipApplicationData
# Register your models here.

admin.site.register(UserProfile)
admin.site.register(ScholarshipData)
admin.site.register(UserScholarshipApplicationData)
