from django.contrib.auth.models import User
from firebase_admin import auth
from rest_framework import authentication
from rest_framework import exceptions
from userapp.models import UserProfile

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
            userProfile = UserProfile.objects.get_or_create(user=user,account_type="google")
            return (user, None)
        except:
            raise exceptions.AuthenticationFailed("Invalid token")