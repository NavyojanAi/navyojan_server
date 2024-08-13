from django.contrib import admin
from userapp.models import UserProfile, ScholarshipData, UserScholarshipApplicationData,Category,OTP
# Register your models here.

admin.site.register(UserProfile)
admin.site.register(ScholarshipData)
admin.site.register(UserScholarshipApplicationData)
admin.site.register(Category)
admin.site.register(OTP)

