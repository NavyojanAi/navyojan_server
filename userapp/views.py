from django.shortcuts import render
from rest_framework import viewsets
from .models import UserProfile, ScholarshipData
from .serializers import UserProfileSerializer, ScholarshipDataSerializer
from userapp.permission import IsActivePermission
from rest_framework.authentication import SessionAuthentication
from userapp.authentication import FirebaseAuthentication


# from rest_framework.views import APIView
# from rest_framework.response import Response

DEFAULT_AUTH_CLASSES = [SessionAuthentication, FirebaseAuthentication]


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()      #created a queryset that retrieves all the objects from the UserProfile model
    serializer_class = UserProfileSerializer   #a serializer is a class that converts complex data, such as querysets and model instances, into native Python data types that can be easily rendered into formats like JSON
    authentication_classes = DEFAULT_AUTH_CLASSES   #a list of authentication classes that the view is using
    permission_classes = [IsActivePermission]
class ScholarshipDataViewSet(viewsets.ModelViewSet):
    queryset = ScholarshipData.objects.all()
    serializer_class = ScholarshipDataSerializer
    authentication_classes = DEFAULT_AUTH_CLASSES
    permission_classes = [IsActivePermission]




# UserProfileViewSet for apiView
# class UserProfileView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         profile = UserProfile.objects.get(user=request.user)
#         serializer = UserProfileSerializer(profile)
#         return Response(serializer.data)


# View for APPLYING SCHOLARSHIP 
# from rest_framework import status
# from .models import ScholarshipData, ScholarshipApplication

# class ApplyScholarshipView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, scholarship_id):
#         try:
#             scholarship = ScholarshipData.objects.get(id=scholarship_id)
#             ScholarshipApplication.objects.create(user=request.user, scholarship=scholarship)
#             return Response({"message": "Application submitted successfully"}, status=status.HTTP_201_CREATED)
#         except ScholarshipData.DoesNotExist:
#             return Response({"error": "Scholarship not found"}, status=status.HTTP_404_NOT_FOUND)
#         except IntegrityError:
#             return Response({"error": "You have already applied for this scholarship"}, status=status.HTTP_400_BAD_REQUEST)