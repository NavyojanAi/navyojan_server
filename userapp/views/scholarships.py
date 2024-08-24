from userapp.authentication import FirebaseAuthentication
from userapp.serializers.scholarships import CategorySerializer
from userapp.permission import IsActivePermission, IsVerfiedPermission
from userapp.filters import ScholarshipDataFilter
from userapp.serializers import ScholarshipDataSerializer, UserScholarshipDataSerializer
from userapp.models.scholarships import ScholarshipData, UserScholarshipApplicationData, Category

from rest_framework.authentication import SessionAuthentication
from rest_framework import viewsets

from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend

DEFAULT_AUTH_CLASSES = [SessionAuthentication, FirebaseAuthentication]


class ScholarshipDataViewSet(viewsets.ModelViewSet):
    queryset = ScholarshipData.objects.all()
    serializer_class = ScholarshipDataSerializer
    http_method_names = ["get"]
    # authentication_classes = DEFAULT_AUTH_CLASSES
    # permission_classes = [IsActivePermission]

    # Enable filtering
    filter_backends = [DjangoFilterBackend]
    filterset_class = ScholarshipDataFilter


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    http_method_names = ["get"]
    # authentication_classes = DEFAULT_AUTH_CLASSES
    # permission_classes = [IsActivePermission]

class UserScholarshipDataViewset(viewsets.ModelViewSet):
    queryset = UserScholarshipApplicationData.objects.all()
    serializer_class = UserScholarshipDataSerializer
    http_method_names = ["get", "post", "patch"]
    authentication_classes = DEFAULT_AUTH_CLASSES
    permission_classes = [IsActivePermission,IsVerfiedPermission]

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user.id)
        return queryset

