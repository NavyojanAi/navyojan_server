import random

from django.utils import timezone

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from rest_framework import status,viewsets,generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser

from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication


from userapp.models import UserScholarshipStatus,UserProfile, OTP,UserProfileScholarshipProvider,UserDocuments,UserPreferences, ScholarshipData, UserScholarshipApplicationData
from userapp.serializers import UserScholarshipStatusSerializer,UserDisplaySerializer,UserProfileSerializer, UserProfileScholarshipProviderSerializer,UserDocumentsSerializer,UserPreferencesSerializer,UserScholarshipDataSerializer
from userapp.permission import IsActivePermission, IsReviewerUser,CanHostSites
from userapp.authentication import FirebaseAuthentication


DEFAULT_AUTH_CLASSES = [JWTAuthentication, FirebaseAuthentication]


class AdminStatisticsView(APIView):
    permission_classes = [IsActivePermission,IsAdminUser, IsReviewerUser]  # Allow only admin users to view these statistics
    authentication_classes = DEFAULT_AUTH_CLASSES

    def get(self, request, *args, **kwargs):
        # User statistics

        # Filter users created in the current month
        users_created_this_month = UserProfile.objects.filter(
            datetime_created__year=timezone.now().year,
            datetime_created__month=timezone.now().month
        )

        # If you want to count the number of users
        total_users_this_month = users_created_this_month.count()
        total_users = User.objects.count()
        total_reviewers = UserProfile.objects.filter(is_reviewer=True).count()
        total_customers = UserProfile.objects.filter(is_host_user=False).count()  # non-host users
        total_providers = UserProfile.objects.filter(is_host_user=True).count()
        total_admins = User.objects.filter(is_staff=True).count()
        total_subscribed_users = UserProfile.objects.filter(premium_account_privilages=True)

        # Scholarship statistics
        total_scholarships = ScholarshipData.objects.count()
        total_approved_scholarships = ScholarshipData.objects.filter(is_approved=True).count()
        total_unapproved_scholarships = ScholarshipData.objects.filter(is_approved=False).count()

        # applications
        total_applications = UserScholarshipApplicationData.objects.count()


        data = {
            "user_stats": {
                "total_users": total_users,
                "total_reviewers": total_reviewers,
                "total_customers": total_customers,
                "total_providers":total_providers,
                "total_admins": total_admins,
                "users_this_month":total_users_this_month,
                "total-subscribed_users":total_subscribed_users
            },
            "scholarship_stats": {
                "total_scholarships": total_scholarships,
                "approved_scholarships": total_approved_scholarships,
                "unapproved_scholarships": total_unapproved_scholarships,
                "total_applications":total_applications
            }
        }

        return Response(data)
    
class HostUserListView(generics.ListAPIView):
    permission_classes = [IsActivePermission,IsAdminUser, IsReviewerUser]
    serializer_class = UserDisplaySerializer

    def get_queryset(self):
        # Fetch all UserProfile objects where is_host_user=True
        return User.objects.filter(userprofile__is_host_user=True)

class UserListView(generics.ListAPIView):
    permission_classes = [IsActivePermission,IsAdminUser, IsReviewerUser]
    serializer_class = UserDisplaySerializer

    def get_queryset(self):
        # Fetch all UserProfile objects where is_host_user=True
        return User.objects.filter(userprofile__is_host_user=False)

class UserScholarshipStatusViewset(viewsets.ModelViewSet):
    queryset = UserScholarshipStatus.objects.all()
    serializer_class = UserScholarshipStatusSerializer
    authentication_classes = DEFAULT_AUTH_CLASSES
    http_method_names = ["get","patch"]

    def get_permissions(self):
        if self.request.method in ['PATCH']:
            return [IsActivePermission, IsAdminUser, IsReviewerUser, CanHostSites]
        else:
            return [IsActivePermission, CanHostSites]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            if instance.status == "approved":
                scholarship = instance.scholarship
                scholarship.is_approved = True
                scholarship.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()      
    serializer_class = UserProfileSerializer  
    authentication_classes = DEFAULT_AUTH_CLASSES  
    http_method_names = ["get", "patch"]
    permission_classes = [IsActivePermission]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

class UserProfileScholarshipProviderViewset(viewsets.ModelViewSet):
    queryset= UserProfileScholarshipProvider.objects.all()
    serializer_class = UserProfileScholarshipProviderSerializer
    authentication_classes = DEFAULT_AUTH_CLASSES
    http_method_names = ["get","patch"]
    permission_classes = [IsActivePermission] 

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

class UserDocumentsViewset(viewsets.ModelViewSet):
    queryset=UserDocuments.objects.all()
    serializer_class=UserDocumentsSerializer
    authentication_classes = DEFAULT_AUTH_CLASSES
    http_method_names = ["get","patch"]
    permission_classes=[IsActivePermission]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

class UserPreferencesViewset(viewsets.ModelViewSet):
    queryset = UserPreferences.objects.all()
    serializer_class = UserPreferencesSerializer
    authentication_classes=DEFAULT_AUTH_CLASSES
    http_method_names=["get","patch"]
    permission_classes=[IsActivePermission]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    
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



