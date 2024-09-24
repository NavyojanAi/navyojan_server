from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from userapp.models import SubscriptionPlan
from userapp.serializers import SubscriptionPlanSerializer
from userapp.authentication import FirebaseAuthentication
from userapp.permission import IsVerfiedPermission

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

    permission_classes = [IsAuthenticated,IsVerfiedPermission]
    authentication_classes = DEFAULT_AUTH_CLASSES
    http_method_names = ['get']


class SubscribeUserView(APIView):
    permission_classes = [IsAuthenticated, IsVerfiedPermission]
    authentication_classes = DEFAULT_AUTH_CLASSES

    def post(self, request):
        plan_id = request.data.get('plan_id')
        try:
            plan = SubscriptionPlan.objects.get(id=plan_id)
        except SubscriptionPlan.DoesNotExist:
            return Response({"error": "Invalid plan ID"}, status=status.HTTP_400_BAD_REQUEST)

        end_date = timezone.now() + timedelta(days=plan.duration)
        
        UserPlanTracker.objects.create(
            user=request.user,
            plan=plan,
            end_date=end_date
        )

        return Response({"message": "Successfully subscribed to plan"}, status=status.HTTP_200_OK)

