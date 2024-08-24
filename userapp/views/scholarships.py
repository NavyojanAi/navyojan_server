from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from django.core.paginator import Paginator


from userapp.models import ScholarshipData, UserScholarshipApplicationData, Category
from userapp.serializers import ScholarshipDataSerializer, UserScholarshipDataSerializer, CategorySerializer
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
    permission_classes = [IsActivePermission]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ScholarshipDataFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        total_pages = (len(queryset)//10)+1
        paginator = Paginator(queryset,10)
        page_number = self.request.query_params.get('page', 1)
        page_queryset = paginator.get_page(page_number)

        serializer = self.get_serializer(page_queryset, many=True)
        response_data = serializer.data
        response_data['total_pages']=total_pages
        return Response(response_data)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    http_method_names = ["get"]

class UserScholarshipDataViewset(viewsets.ModelViewSet):
    queryset = UserScholarshipApplicationData.objects.all()
    serializer_class = UserScholarshipDataSerializer
    http_method_names = ["get", "post", "patch"]
    authentication_classes = DEFAULT_AUTH_CLASSES
    permission_classes = [IsActivePermission,IsVerfiedPermission]

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user.id)
        return queryset

