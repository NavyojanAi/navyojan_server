from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from userapp.models import SubscriptionPlan
from userapp.serializers import SubscriptionPlanSerializer
from userapp.authentication import FirebaseAuthentication
from userapp.permission import IsVerfiedPermission

DEFAULT_AUTH_CLASSES = [JWTAuthentication, FirebaseAuthentication] 


class SubscriptionPlanViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer

    permission_classes = [IsAuthenticated,IsVerfiedPermission]
    authentication_classes = DEFAULT_AUTH_CLASSES
    http_method_names = ['get']

