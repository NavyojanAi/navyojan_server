from django.shortcuts import render
from rest_framework import viewsets
from .models import UserProfile, ScholarshipData
from .serializers import UserProfileSerializer, ScholarshipDataSerializer
from userapp.permission import IsActivePermission
from rest_framework.authentication import SessionAuthentication
from userapp.google_authentication import FirebaseAuthentication


DEFAULT_AUTH_CLASSES = [SessionAuthentication, FirebaseAuthentication]


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()      
    serializer_class = UserProfileSerializer  
    authentication_classes = DEFAULT_AUTH_CLASSES  
    permission_classes = [IsActivePermission]

class ScholarshipDataViewSet(viewsets.ModelViewSet):
    queryset = ScholarshipData.objects.all()
    serializer_class = ScholarshipDataSerializer
    authentication_classes = DEFAULT_AUTH_CLASSES
    permission_classes = [IsActivePermission]
