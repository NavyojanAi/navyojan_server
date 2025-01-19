from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from userapp.models import SubscriptionPlan
from userapp.serializers import SubscriptionPlanSerializer
from userapp.authentication import FirebaseAuthentication
from userapp.permission import IsVerifiedPermission

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from userapp.models import UserPlanTracker

DEFAULT_AUTH_CLASSES = [JWTAuthentication, FirebaseAuthentication] 


class SubscriptionPlanViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer

    permission_classes = [IsAuthenticated,IsVerifiedPermission]
    authentication_classes = DEFAULT_AUTH_CLASSES
    http_method_names = ['get']




