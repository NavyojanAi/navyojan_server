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


DEFAULT_AUTH_CLASSES = [SessionAuthentication, FirebaseAuthentication]


class ScholarshipDataViewSet(viewsets.ModelViewSet):
    queryset = ScholarshipData.objects.all()
    serializer_class = ScholarshipDataSerializer
    authentication_classes = DEFAULT_AUTH_CLASSES
    permission_classes = [IsActivePermission]

class UserScholarshipDataViewset(viewsets.ModelViewSet):
    queryset = UserScholarshipApplicationData.objects.all()
    serializer_class = UserScholarshipDataSerializer
    authentication_classes = DEFAULT_AUTH_CLASSES
    permission_classes = [IsActivePermission,IsVerfiedPermission]

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user.id)
        return queryset



class ScholarshipListAPIView(APIView):
    def get(self, request):
        category_name = request.query_params.get('category_name')
        
        scholarships = ScholarshipData.objects.all()
        
        if category_name:
            try:
                category = Category.objects.get(id=category_name)
                scholarships = scholarships.filter(categories=category)
            except Category.DoesNotExist:
                return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ScholarshipDataSerializer(scholarships, many=True)
        return Response(serializer.data)
    