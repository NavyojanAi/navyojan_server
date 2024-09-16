from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from django.core.paginator import Paginator

from django.utils.timezone import now
from userapp.models import ScholarshipData, UserScholarshipApplicationData, Category
from userapp.serializers import ScholarshipDataSerializer, UserScholarshipDataSerializer, CategorySerializer
from userapp.authentication import FirebaseAuthentication
from userapp.permission import IsActivePermission,CanHostSites,IsActiveAndCanHostOrIsReviewer
from userapp.filters import ScholarshipDataFilter

from rest_framework.authentication import SessionAuthentication
from rest_framework import viewsets

from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend

# DEFAULT_AUTH_CLASSES = [SessionAuthentication, FirebaseAuthentication]


class ScholarshipDataViewSet(viewsets.ModelViewSet):
    queryset = ScholarshipData.objects.all()
    serializer_class = ScholarshipDataSerializer
    http_method_names = ["get","post","patch","delete"]

    filter_backends = [DjangoFilterBackend]
    filterset_class = ScholarshipDataFilter

    def get_permissions(self):
        if self.request.method in ['POST', 'DELETE']:
            return [IsActivePermission(), CanHostSites()]
        elif self.request.method in ['PATCH']:
            return [IsActiveAndCanHostOrIsReviewer()]
        else:
            return []
        
    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        # Default filter for deadline: only show scholarships with deadline >= today
        return queryset.filter(deadline__gte=now())
    

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        paginator = Paginator(queryset, 10)
        page_number = self.request.query_params.get('page', 1)
        page_queryset = paginator.get_page(page_number)

        # Serialize the data
        serializer = self.get_serializer(page_queryset, many=True)
        
        # Create response structure
        response_data = {
            'results': serializer.data,
            'total_pages': paginator.num_pages
        }

        return Response(response_data)
        
    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            scholarship=serializer.save()
            user = self.request.user
            user.hostprofile.hosted_scholarships.add(scholarship)
            user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance not in request.user.hostprofile.hosted_scholarships.all():
            return Response(status=status.HTTP_401_UNAUTHORIZED)        
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    http_method_names = ["get"]

class UserScholarshipApplicationDataViewset(viewsets.ModelViewSet):
    queryset = UserScholarshipApplicationData.objects.all()
    serializer_class = UserScholarshipDataSerializer
    http_method_names = ["get", "post", "patch"]
    # authentication_classes = DEFAULT_AUTH_CLASSES
    # permission_classes = [IsActivePermission,IsVerfiedPermission]

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user.id)
        return queryset

