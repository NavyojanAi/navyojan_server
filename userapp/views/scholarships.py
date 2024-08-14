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

DEFAULT_AUTH_CLASSES = [SessionAuthentication, FirebaseAuthentication]


class ScholarshipDataViewSet(viewsets.ModelViewSet):
    queryset = ScholarshipData.objects.all()
    serializer_class = ScholarshipDataSerializer
    http_method_names = ["get"]
    authentication_classes = DEFAULT_AUTH_CLASSES
    permission_classes = [IsActivePermission]

    def list(self, request, *args, **kwargs):
        category_id = request.data.get('category_id', None) # expects a integer(id)
        
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                queryset = self.get_queryset().filter(categories=category)
            except Category.DoesNotExist:
                queryset = ScholarshipData.objects.none()
        else:
            return Response(
                "category doesn't exist",
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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



# class ScholarshipListAPIView(APIView):
#     def get(self, request):
#         category_name = request.query_params.get('category_name')
        
#         scholarships = ScholarshipData.objects.all()
        
#         if category_name:
#             try:
#                 category = Category.objects.get(id=category_name)
#                 scholarships = scholarships.filter(categories=category)
#             except Category.DoesNotExist:
#                 return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
        
#         serializer = ScholarshipDataSerializer(scholarships, many=True)
#         return Response(serializer.data)
    