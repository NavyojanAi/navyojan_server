from rest_framework import status
from rest_framework import viewsets,generics
from rest_framework.response import Response

from django.core.paginator import Paginator

from django.utils.timezone import now
from userapp.models import UserScholarshipStatus,ScholarshipData, UserScholarshipApplicationData, Category,Documents,Eligibility
from userapp.serializers import ScholarshipDataSerializer, UserScholarshipDataSerializer, CategorySerializer,DocumentSerializer,EligibilitySerializer
from userapp.authentication import FirebaseAuthentication
from userapp.permission import IsActivePermission,CanHostScholarships,IsActiveAndCanHostOrIsReviewer, IsVerfiedPermission,IsReviewerUser
from userapp.filters import ScholarshipDataFilter

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import viewsets
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAdminUser
DEFAULT_AUTH_CLASSES = [JWTAuthentication, FirebaseAuthentication] 


class ScholarshipDataViewSet(viewsets.ModelViewSet):
    queryset = ScholarshipData.objects.all()
    serializer_class = ScholarshipDataSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ScholarshipDataFilter
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        if self.action == 'list' and self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.userprofile.is_reviewer):
            return ScholarshipData.objects.all()
        return ScholarshipData.objects.filter(is_approved=True)

    def get_permissions(self):
        if self.action == 'list' and self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.userprofile.is_reviewer):
            return [IsActivePermission(), IsReviewerUser(), IsAdminUser()]
        elif self.request.method in ['POST', 'DELETE']:
            return [IsActivePermission(), CanHostScholarships()]
        elif self.request.method == 'PATCH':
            return [IsActiveAndCanHostOrIsReviewer()]
        else:
            return []

    def get_authenticators(self):
        if self.request.method in ['POST', 'PATCH', 'DELETE']:
            return [auth() for auth in DEFAULT_AUTH_CLASSES]
        return []

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        if not (self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.userprofile.is_reviewer)):
            queryset = queryset.filter(deadline__gte=now())
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        page_size = self.request.query_params.get('page_size', 10)
        page_number = self.request.query_params.get('page', 1)
        paginator = Paginator(queryset, page_size)

        page_queryset = paginator.get_page(page_number)

        # Serialize the data
        serializer = self.get_serializer(page_queryset, many=True)
        
        # Create response structure
        response_data = {
            'results': serializer.data,
            'total_pages': paginator.num_pages,
            'current_page': page_queryset.number,
            'has_next': page_queryset.has_next(),
            'has_previous': page_queryset.has_previous(),
        }

        return Response(response_data)
        
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            scholarship = serializer.save()
            user = request.user
            user.hostprofile.hosted_scholarships.add(scholarship)
            UserScholarshipStatus.objects.get_or_create(user=user,scholarship=scholarship) # Reviewer needs to approve this scholarship
            user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        if instance not in user.hostprofile.hosted_scholarships.all():
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        user.hostprofile.hosted_scholarships.remove(instance)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_202_ACCEPTED)

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Documents.objects.all()
    serializer_class = DocumentSerializer
    http_method_names = ["get"]

class EligibilityViewSet(viewsets.ModelViewSet):
    queryset = Eligibility.objects.all()
    serializer_class = EligibilitySerializer
    http_method_names = ["get"]

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    http_method_names = ["get"]

class UserScholarshipApplicationDataViewset(viewsets.ModelViewSet):
    queryset = UserScholarshipApplicationData.objects.all()
    serializer_class = UserScholarshipDataSerializer
    http_method_names = ["get", "post", "patch"]
    authentication_classes = DEFAULT_AUTH_CLASSES
    permission_classes = [IsActivePermission]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update']:
            return [IsActivePermission(), IsVerfiedPermission()]
        elif self.action == 'list':
            return [IsActivePermission()]
        else:
            return [IsActivePermission(), IsAdminUser() | CanHostScholarships()]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.userprofile.is_reviewer:
            return self.queryset.all()
        elif user.hostprofile.can_host_scholarships and user.userprofile.is_host_user:
            return self.queryset.filter(scholarship__host=user)
        else:
            return self.queryset.filter(user=user)

    def create(self, request, *args, **kwargs):
        user = request.user
        scholarship_id = request.data.get('scholarship')

        try:
            application = self.queryset.get(user=user, scholarship__id=scholarship_id)
            serializer = self.get_serializer(application, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserScholarshipApplicationData.DoesNotExist:
            return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if request.user.hostprofile.can_host_scholarships:
            queryset = queryset.filter(status='applied')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class UserScholarshipApplicationListView(generics.ListAPIView):
    queryset = UserScholarshipApplicationData.objects.all()
    serializer_class = UserScholarshipDataSerializer
    authentication_classes = DEFAULT_AUTH_CLASSES
    permission_classes = [IsActivePermission, CanHostScholarships]

    def get_queryset(self):
        return self.queryset.filter(scholarship__host=self.request.user,status='applied')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        page_size = int(request.query_params.get('page_size', 10))
        page_number = int(request.query_params.get('page', 1))
        
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page_number)

        serializer = self.get_serializer(page_obj, many=True)
        
        return Response({
            'num_pages': paginator.num_pages,
            'results': serializer.data,
            'current_page': page_obj.number,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        })
