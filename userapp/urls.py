from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet, ScholarshipDataViewSet



router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet)
router.register(r'scholarships', ScholarshipDataViewSet)


urlpatterns = [
    path('', include(router.urls)),
    # path('profile/', UserProfileView.as_view(), name='user_profile'),
    # path('apply-scholarship/<int:scholarship_id>/', ApplyScholarshipView.as_view(), name='apply_scholarship'),
    
]