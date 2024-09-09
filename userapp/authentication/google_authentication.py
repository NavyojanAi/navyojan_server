from django.contrib.auth.models import User
from firebase_admin import auth
from rest_framework import authentication
from rest_framework import exceptions
from userapp.models import UserProfile,UserDocuments,UserPreferences,UserProfileScholarshipProvider

class FirebaseAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        if not auth_header:
            return None

        id_token = auth_header.split(" ").pop()
        try:
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token["uid"]
            user, created = User.objects.get_or_create(username=uid)
            signup_type = request.data['signup_type']
            if signup_type == 'scholarshipProviders':
                upsp,_=UserProfileScholarshipProvider.objects.get_or_create(user=user)
            else:
                #NOTE:more signup types can comeup further
                pass
            user_profile,_ = UserProfile.objects.get_or_create(user=user,account_type="google",is_email_verified=True,is_host_user=True)
            user_documents,_=UserDocuments.objects.get_or_create(user=user)
            user_preferences,_=UserPreferences.objects.get_or_create(user=user)
            return (user, None)
        except:
            raise exceptions.AuthenticationFailed("Invalid token")