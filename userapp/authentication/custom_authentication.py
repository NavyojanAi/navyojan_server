from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model



class EmailModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        if username is None:
            username = kwargs.get('username')
        if username is None or password is None:
            return None
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            # user = User.objects.get(username=username)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def get_user(self, user_id):
        User = get_user_model()
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        return user if self.user_can_authenticate(user) else None
