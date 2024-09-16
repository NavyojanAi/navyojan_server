import random

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser

from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication


from userapp.models import UserProfile, OTP,UserProfileScholarshipProvider,UserDocuments,UserPreferences, ScholarshipData
from userapp.serializers import UserProfileSerializer, UserProfileScholarshipProviderSerializer,UserDocumentsSerializer,UserPreferencesSerializer,UserScholarshipDataSerializer
from userapp.permission import IsActivePermission, IsReviewerUser
from userapp.authentication import FirebaseAuthentication


DEFAULT_AUTH_CLASSES = [SessionAuthentication, FirebaseAuthentication]

class AdminStatisticsView(APIView):
    permission_classes = [IsAdminUser, IsReviewerUser]  # Allow only admin users to view these statistics

    def get(self, request, *args, **kwargs):
        # User statistics
        total_users = User.objects.count()
        total_reviewers = UserProfile.objects.filter(is_reviewer=True).count()
        total_customers = UserProfile.objects.filter(is_host_user=False).count()  # non-host users
        total_admins = User.objects.filter(is_staff=True).count()

        # Scholarship statistics
        total_scholarships = ScholarshipData.objects.count()
        total_approved_scholarships = ScholarshipData.objects.filter(is_approved=True).count()
        total_unapproved_scholarships = ScholarshipData.objects.filter(is_approved=False).count()

        data = {
            "user_stats": {
                "total_users": total_users,
                "total_reviewers": total_reviewers,
                "total_customers": total_customers,
                "total_admins": total_admins,
            },
            "scholarship_stats": {
                "total_scholarships": total_scholarships,
                "approved_scholarships": total_approved_scholarships,
                "unapproved_scholarships": total_unapproved_scholarships,
            }
        }

        return Response(data)

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()      
    serializer_class = UserProfileSerializer  
    authentication_classes = DEFAULT_AUTH_CLASSES  
    http_method_names = ["get", "patch"]
    permission_classes = [IsActivePermission]

class UserProfileScholarshipProviderViewset(viewsets.ModelViewSet):
    queryset= UserProfileScholarshipProvider.objects.all()
    serializer_class = UserProfileScholarshipProviderSerializer
    authentication_classes = DEFAULT_AUTH_CLASSES
    http_method_names = ["get","patch"]
    permission_classes = [IsActivePermission] 

class UserDocumentsViewset(viewsets.ModelViewSet):
    queryset=UserDocuments.objects.all()
    serializer_class=UserDocumentsSerializer
    authentication_classes = DEFAULT_AUTH_CLASSES
    http_method_names = ["get","patch"]
    permission_classes=[IsActivePermission]

class UserPreferencesViewset(viewsets.ModelViewSet):
    queryset = UserPreferences.objects.all()
    serializer_class = UserPreferencesSerializer
    authentication_classes=DEFAULT_AUTH_CLASSES
    http_method_names=["get","patch"]
    permission_classes=[IsActivePermission]
    
class GenerateOTP(APIView):
    def post(self, request):
        user = request.user
        otp_type = request.data.get('otp_type')
        
        if otp_type == 'phone':
            phone_number = user.userprofile.phone_number
            if phone_number:
                otp = random.randint(100000, 999999)
                OTP.objects.update_or_create(user=user, otp_type=otp_type, defaults={'otp': otp, 'verified': False})

                # Send OTP via msg97
                # send_otp_via_msg97(user.userprofile.phone_number)
                
                return Response({"message": "OTP sent to phone number"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Phone number not found"}, status=status.HTTP_400_BAD_REQUEST)
        
        elif otp_type == 'email':
            email = user.email
            if email:
                otp = random.randint(100000, 999999)
                OTP.objects.update_or_create(user=user, otp_type=otp_type, defaults={'otp': otp, 'verified': False})

                # Send OTP via email
                send_mail('Your OTP Code', f'Your OTP code is {otp}', 'noreply@example.com', [email])
                
                return Response({"message": "OTP sent to email"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Email not found"}, status=status.HTTP_400_BAD_REQUEST)
        
        else:
            return Response({"error": "Invalid OTP type"}, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTP(APIView):
    def post(self, request):
        user = request.user
        otp = request.data.get('otp')
        otp_type = request.data.get('otp_type')
        
        otp_instance = get_object_or_404(OTP, user=user, otp_type=otp_type)
        
        if otp_instance.otp == otp:
            otp_instance.verified = True
            otp_instance.save()
            
            if otp_type == 'phone':
                user.userprofile.is_phone_number_verified = True
            elif otp_type == 'email':
                user.userprofile.is_email_verified = True
            
            user.userprofile.save()
            
            return Response({"message": f"{otp_type.capitalize()} verified"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)



