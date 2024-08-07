from django.urls import path, include
from django.urls import path

from rest_framework.routers import DefaultRouter

from userapp.views import UserProfileViewSet, ScholarshipDataViewSet, GenerateOTP, VerifyOTP


router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet)
router.register(r'scholarships', ScholarshipDataViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('profiles/generate-otp/', GenerateOTP.as_view(), name='generate-otp'),
    path('profiles/verify-otp/', VerifyOTP.as_view(), name='verify-otp'),
]