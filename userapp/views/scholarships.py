from rest_framework import status
from rest_framework import viewsets,generics
from rest_framework.response import Response

from django.core.paginator import Paginator

from django.utils.timezone import now
from userapp.models import UserScholarshipStatus,ScholarshipData, UserScholarshipApplicationData, Category,Documents,Eligibility
from userapp.serializers import ScholarshipDataSerializer, UserScholarshipDataSerializer, CategorySerializer,DocumentSerializer,EligibilitySerializer
from userapp.authentication import FirebaseAuthentication
from userapp.permission import IsActivePermission,CanHostScholarships,IsActiveAndCanHostOrIsReviewer, IsVerifiedPermission,IsReviewerUser
from userapp.filters import ScholarshipDataFilter

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import viewsets
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAdminUser
from logs.logger_setup import logger  # Import the logger

DEFAULT_AUTH_CLASSES = [JWTAuthentication, FirebaseAuthentication] 


class ScholarshipDataViewSet(viewsets.ModelViewSet):
    queryset = ScholarshipData.objects.all()
    serializer_class = ScholarshipDataSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ScholarshipDataFilter
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        try:
            if self.action == 'list' and self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.userprofile.is_reviewer):
                return ScholarshipData.objects.all()
            return ScholarshipData.objects.filter(is_approved=True)
        except Exception as e:
            logger.debug(f'Error retrieving scholarship data: {str(e)}')
            return ScholarshipData.objects.none()  # Return an empty queryset on error

    def get_permissions(self):
        try:
            if self.action == 'list' and self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.userprofile.is_reviewer):
                return [IsActivePermission(), IsReviewerUser(), IsAdminUser()]
            elif self.request.method in ['POST', 'DELETE']:
                return [IsActivePermission(), CanHostScholarships()]
            elif self.request.method == 'PATCH':
                return [IsActiveAndCanHostOrIsReviewer()]
            else:
                return []
        except Exception as e:
            logger.debug(f'Error getting permissions: {str(e)}')
            return []  # Return empty permissions on error

    def get_authenticators(self):
        try:
            if self.request.method in ['POST', 'PATCH', 'DELETE']:
                return [auth() for auth in DEFAULT_AUTH_CLASSES]
            return []
        except Exception as e:
            logger.debug(f'Error getting authenticators: {str(e)}')
            return []  # Return empty authenticators on error

    def filter_queryset(self, queryset):
        try:
            queryset = super().filter_queryset(queryset)
            if not (self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.userprofile.is_reviewer)):
                queryset = queryset.filter(deadline__gte=now())
            return queryset
        except Exception as e:
            logger.debug(f'Error filtering queryset: {str(e)}')
            return queryset  # Return the original queryset on error

    def list(self, request, *args, **kwargs):
        try:
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
        except Exception as e:
            logger.debug(f'Error listing scholarships: {str(e)}')
            return Response({'error': 'Failed to retrieve scholarships'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                scholarship = serializer.save()
                user = request.user
                user.hostprofile.hosted_scholarships.add(scholarship)
                UserScholarshipStatus.objects.get_or_create(user=user, scholarship=scholarship)  # Reviewer needs to approve this scholarship
                user.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.debug(f'Error creating scholarship: {str(e)}')
            return Response({'error': 'Failed to create scholarship'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            user = request.user
            if instance not in user.hostprofile.hosted_scholarships.all():
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            user.hostprofile.hosted_scholarships.remove(instance)
            self.perform_destroy(instance)
            return Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            logger.debug(f'Error destroying scholarship: {str(e)}')
            return Response({'error': 'Failed to delete scholarship'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

    def get_permissions(self):
        if self.action in ['create']:
            return [IsActivePermission(), IsVerifiedPermission()]
        elif self.action in ['list', 'retrieve']:
            return [IsActivePermission()]
        elif self.action in [ 'partial_update']:
            return [IsActivePermission(), IsAdminUser() | CanHostScholarships()]
        else:
            return []

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.userprofile.is_reviewer:
            return self.queryset.all()
        elif hasattr(user, 'hostprofile') and user.hostprofile.can_host_scholarships and user.userprofile.is_host_user:
            return self.queryset.filter(scholarship__host=user)
        else:
            return self.queryset.filter(user=user)

    def create(self, request, *args, **kwargs):
        user = request.user
        scholarship_id = request.data.get('scholarship')

        if not scholarship_id:
            return Response({'error': 'Scholarship ID is required'}, status=status.HTTP_400_BAD_REQUEST)

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
        if hasattr(request.user, 'hostprofile') and request.user.hostprofile.can_host_scholarships:
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
