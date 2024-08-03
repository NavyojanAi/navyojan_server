from rest_framework import viewsets
from userapp.models import ScholarshipData, UserScholarshipApplicationData
from userapp.serializers import ScholarshipDataSerializer, UserScholarshipDataSerializer
from userapp.permission import IsActivePermission, IsVerfiedPermission
from rest_framework.authentication import SessionAuthentication
from userapp.authentication import FirebaseAuthentication

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
