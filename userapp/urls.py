from django.urls import path, include
from rest_framework.routers import DefaultRouter
from userapp.views import UserProfileViewSet, ScholarshipDataViewSet
from userapp.authentication_views import signup_view, login_view, logout_view




router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet)
router.register(r'scholarships', ScholarshipDataViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]