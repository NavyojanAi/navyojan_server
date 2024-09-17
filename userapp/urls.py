from django.urls import path, include
from django.urls import path

from rest_framework.routers import DefaultRouter

from userapp.views import UserScholarshipStatusViewset,UserListView,HostUserListView,UserProfileViewSet, ScholarshipDataViewSet, GenerateOTP, VerifyOTP, CategoryViewSet,UserScholarshipApplicationDataViewset,UserProfileScholarshipProviderViewset,UserDocumentsViewset,UserPreferencesViewset,AdminStatisticsView

router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet)
router.register(r'scholarships', ScholarshipDataViewSet)
router.register(r'categories',CategoryViewSet)
router.register(r'user_scholarship_status',UserScholarshipApplicationDataViewset)
router.register(r'profile_sp',UserProfileScholarshipProviderViewset)
router.register(r'documents',UserDocumentsViewset)
router.register(r'preferences',UserPreferencesViewset)
router.register(r'scholarship_status',UserScholarshipStatusViewset)

urlpatterns = [
    path('', include(router.urls)),
    path('profiles/generate-otp/', GenerateOTP.as_view(), name='generate-otp'),
    path('profiles/verify-otp/', VerifyOTP.as_view(), name='verify-otp'),
    path('stats/', AdminStatisticsView.as_view(), name='navyojan-stats'),
    path('host-users/', HostUserListView.as_view(), name='host-user-list'),
    path('users/', UserListView.as_view(), name='user-list'),
]