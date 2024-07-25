from django.shortcuts import render
from rest_framework import viewsets
from .models import UserProfile, ScholarshipData
from .serializers import UserProfileSerializer, ScholarshipDataSerializer
from .permission import IsAuthenticated


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()      #created a queryset that retrieves all the objects from the UserProfile model
    serializer_class = UserProfileSerializer   #a serializer is a class that converts complex data, such as querysets and model instances, into native Python data types that can be easily rendered into formats like JSON
    authentication_classes = [IsAuthenticated]   #a list of authentication classes that the view is using

class ScholarshipDataViewSet(viewsets.ModelViewSet):
    queryset = ScholarshipData.objects.all()
    serializer_class = ScholarshipDataSerializer
