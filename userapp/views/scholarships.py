from rest_framework import status
from rest_framework import viewsets
from userapp.models.scholarships import ScholarshipData, UserScholarshipApplicationData, Category
from userapp.serializers import ScholarshipDataSerializer, UserScholarshipDataSerializer
from userapp.permission import IsActivePermission, IsVerfiedPermission
from rest_framework.authentication import SessionAuthentication
from userapp.authentication import FirebaseAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from userapp.serializers.scholarships import CategorySerializer
from django.utils import timezone

DEFAULT_AUTH_CLASSES = [SessionAuthentication, FirebaseAuthentication]


class ScholarshipDataViewSet(viewsets.ModelViewSet):
    queryset = ScholarshipData.objects.all()
    serializer_class = ScholarshipDataSerializer
    http_method_names = ["get"]
    authentication_classes = DEFAULT_AUTH_CLASSES
    permission_classes = [IsActivePermission]

    def list(self, request, *args, **kwargs):
        category_id = request.data.get('category_id', None) # expects a integer(id)
        published_after = request.data.get('published_after', None)  # expects a date string (YYYY-MM-DD)
        amount_min = request.data.get('amount_min', None)  # expects an integer
        amount_max = request.data.get('amount_max', None)  # expects an integer
        
        queryset = self.get_queryset()
        
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                queryset = queryset.filter(categories=category)
            except Category.DoesNotExist:
                queryset = ScholarshipData.objects.none()
        else:
            return Response(
                "category doesn't exist",
                status=status.HTTP_400_BAD_REQUEST,
            )
            
        if published_after:
            queryset = queryset.filter(published_on__gte=published_after)
        else:
            queryset = queryset.filter(published_on__gte=timezone.now().date())

        # Filter scholarships within a specified amount range
        if amount_min and amount_max:
            queryset = queryset.filter(amount__range=(amount_min, amount_max))
        elif amount_min:
            queryset = queryset.filter(amount__gte=amount_min)
        elif amount_max:
            queryset = queryset.filter(amount__lte=amount_max)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# published_on
# amount

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    http_method_names = ["get"]
    authentication_classes = DEFAULT_AUTH_CLASSES
    permission_classes = [IsActivePermission]

class UserScholarshipDataViewset(viewsets.ModelViewSet):
    queryset = UserScholarshipApplicationData.objects.all()
    serializer_class = UserScholarshipDataSerializer
    http_method_names = ["get", "post", "patch"]
    authentication_classes = DEFAULT_AUTH_CLASSES
    permission_classes = [IsActivePermission,IsVerfiedPermission]

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user.id)
        return queryset

