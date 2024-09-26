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


from userapp.models import UserScholarshipStatus,UserProfile, OTP,UserProfileScholarshipProvider,UserDocuments,UserPreferences, ScholarshipData, UserScholarshipApplicationData, UserPlanTracker
from userapp.serializers import UserScholarshipStatusSerializer,UserDisplaySerializer,UserProfileSerializer, UserProfileScholarshipProviderSerializer,UserDocumentsSerializer,UserPreferencesSerializer,UserScholarshipDataSerializer
from userapp.permission import IsActivePermission, IsReviewerUser,CanHostScholarships
from userapp.authentication import FirebaseAuthentication


DEFAULT_AUTH_CLASSES = [JWTAuthentication, FirebaseAuthentication]


class AdminStatisticsView(APIView):
    permission_classes = [IsActivePermission, IsAdminUser]  # Allow only admin users to view these statistics
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

        total_subscribed_users = UserProfile.objects.exclude(plan=None).count()


        # Scholarship statistics
        total_scholarships = ScholarshipData.objects.count()
        total_approved_scholarships = ScholarshipData.objects.filter(is_approved=True).count()
        total_unapproved_scholarships = ScholarshipData.objects.filter(is_approved=False).count()

        # applications
        total_applications = UserScholarshipApplicationData.objects.count()


        # Monthly application data
        current_year = timezone.now().year
        last_year = current_year - 1

        current_year_data = self.get_monthly_application_data(current_year)
        last_year_data = self.get_monthly_application_data(last_year)

        # Latest scholarships with status
        latest_scholarships = self.get_latest_scholarships()
        latest_scholarship_applications = self.get_latest_scholarship_applications()

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
            },
            "monthly_application_data": [
                {"name": "This year", "data": current_year_data},
                {"name": "Last year", "data": last_year_data},
            ],
            "latest_scholarships": latest_scholarships,
            "latest_scholarship_applications": latest_scholarship_applications
        }

        return Response(data)

    def get_monthly_application_data(self, year):
        monthly_data = []
        for month in range(1, 13):
            count = UserScholarshipApplicationData.objects.filter(
                datetime_created__year=year,
                datetime_created__month=month
            ).count()
            monthly_data.append(count)
        return monthly_data

    def get_latest_scholarships(self):
        latest_scholarships = ScholarshipData.objects.order_by('-datetime_created')[:5]
        scholarship_data = []
        for scholarship in latest_scholarships:
            status = UserScholarshipStatus.objects.filter(scholarship=scholarship).first()
            scholarship_data.append({
                "id": scholarship.id,
                "title": scholarship.title,
                "status": status.status if status else "Unknown"
            })
        return scholarship_data
    
    def get_latest_scholarship_applications(self):
        try:
            latest_applications = UserScholarshipApplicationData.objects.order_by('-datetime_created')[:5]
        except Exception as e:
            latest_applications = UserScholarshipApplicationData.objects.order_by('-datetime_created')
        data = UserScholarshipDataSerializer(latest_applications, many=True).data
        return data
    
class HostUserListView(generics.ListAPIView):
    permission_classes = [IsActivePermission,IsAdminUser, IsReviewerUser]
    serializer_class = UserDisplaySerializer
    authentication_classes = DEFAULT_AUTH_CLASSES
    def get_queryset(self):
        # Fetch all UserProfile objects where is_host_user=True
        return User.objects.filter(userprofile__is_host_user=True)

class UserListView(generics.ListAPIView):
    permission_classes = [IsActivePermission,IsAdminUser, IsReviewerUser]
    serializer_class = UserDisplaySerializer

    def get_queryset(self):
        # Fetch all UserProfile objects where is_host_user=True
        return User.objects.filter(userprofile__is_host_user=False)

class userScholarshipStatusListView(generics.ListAPIView):
    queryset = UserScholarshipStatus.objects.all()
    permission_classes = [IsActivePermission,IsAdminUser, IsReviewerUser]
    serializer_class = UserScholarshipStatusSerializer
    authentication_classes = DEFAULT_AUTH_CLASSES

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        print(f"Number of objects: {queryset.count()}")  # Add this line
        return super().list(request, *args, **kwargs)

class UserScholarshipStatusViewset(viewsets.ModelViewSet):
    queryset = UserScholarshipStatus.objects.all()
    serializer_class = UserScholarshipStatusSerializer
    authentication_classes = DEFAULT_AUTH_CLASSES
    http_method_names = ["get","patch"]

    def get_permissions(self):
        if self.request.method == 'PATCH':
            return [IsActivePermission(), IsAdminUser(), IsReviewerUser()]
        return [IsActivePermission(), CanHostScholarships()]

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
    http_method_names = ["get"]
    permission_classes = [IsActivePermission]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        
        # Add subscription information
        user = instance.user
        data['is_subscribed'] = user.is_subscribed()
        current_plan = user.get_current_plan()
        if current_plan:
            data['current_plan'] = {
                'title': current_plan.title,
                'amount': current_plan.amount,
                'duration': current_plan.duration
            }
        else:
            data['current_plan'] = None

        return Response(data)

class UserProfilePatchView(APIView):
    authentication_classes = DEFAULT_AUTH_CLASSES
    permission_classes = [IsActivePermission]

    def patch(self, request):
        instance = get_object_or_404(UserProfile, user=request.user)
        serializer = UserProfileSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserProfileScholarshipProviderViewset(viewsets.ModelViewSet):
    queryset= UserProfileScholarshipProvider.objects.all()
    serializer_class = UserProfileScholarshipProviderSerializer
    authentication_classes = DEFAULT_AUTH_CLASSES
    http_method_names = ["get"]
    permission_classes = [IsActivePermission] 

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    
class UserProfileScholarshipProviderPatchView(APIView):
    authentication_classes = DEFAULT_AUTH_CLASSES
    permission_classes = [IsActivePermission]

    def patch(self, request):
        instance = get_object_or_404(UserProfileScholarshipProvider, user=request.user)
        serializer = UserProfileScholarshipProviderSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserDocumentsViewset(viewsets.ModelViewSet):
    queryset=UserDocuments.objects.all()
    serializer_class=UserDocumentsSerializer
    authentication_classes = DEFAULT_AUTH_CLASSES
    http_method_names = ["get"]
    permission_classes=[IsActivePermission]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

class UserDocumentsPatchView(APIView):
    authentication_classes = DEFAULT_AUTH_CLASSES
    permission_classes = [IsActivePermission]

    def patch(self, request):
        instance = get_object_or_404(UserDocuments, user=request.user)
        serializer = UserDocumentsSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserPreferencesViewset(viewsets.ModelViewSet):
    queryset = UserPreferences.objects.all()
    serializer_class = UserPreferencesSerializer
    authentication_classes=DEFAULT_AUTH_CLASSES
    http_method_names=["get"]
    permission_classes=[IsActivePermission]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

class UserPreferencesPatchView(APIView):
    authentication_classes = DEFAULT_AUTH_CLASSES
    permission_classes = [IsActivePermission]

    def patch(self, request):
        instance = get_object_or_404(UserPreferences, user=request.user)
        serializer = UserPreferencesSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
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


