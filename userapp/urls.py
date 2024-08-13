from django.urls import path, include
from django.urls import path

from rest_framework.routers import DefaultRouter

from userapp.views import UserProfileViewSet, ScholarshipDataViewSet, GenerateOTP, VerifyOTP, CategoryViewSet,UserScholarshipDataViewset

from userapp.views import UserProfileViewSet, ScholarshipDataViewSet, GenerateOTP, VerifyOTP
from userapp.views.scholarships import ScholarshipListAPIView

router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet)
router.register(r'scholarships', ScholarshipDataViewSet)
router.register(r'categories',CategoryViewSet)
router.register(r'scholarship_data',UserScholarshipDataViewset)

urlpatterns = [
    path('', include(router.urls)),
    path('profiles/generate-otp/', GenerateOTP.as_view(), name='generate-otp'),
    path('profiles/verify-otp/', VerifyOTP.as_view(), name='verify-otp'),
    # path('scholarships/', ScholarshipListAPIView.as_view(), name='scholarship-list'),
]