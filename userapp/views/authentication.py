from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework.decorators import api_view,permission_classes
from rest_framework import status


from django.contrib.auth import authenticate,get_user_model
from django.conf import settings

from userapp.models import UserProfile,UserProfileScholarshipProvider,UserDocuments,UserPreferences
from userapp.forms import CustomUserCreationForm
from userapp.permission import IsActivePermission

def generate_unique_username(first_name, last_name):
    User = get_user_model()
    base_username = f"{first_name}_{last_name}".lower()
    username = base_username
    counter = 1
    
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1
        
    return username

@api_view(['POST','GET'])
def signup_view(request):
    if request.method == 'POST':
        input_form = request.data
        input_form['username'] = generate_unique_username(first_name=input_form['first_name'], last_name=input_form['last_name'])
        form = CustomUserCreationForm(input_form)
        if form.is_valid():
            user = form.save()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')

            # Authenticate user
            user = authenticate(request, username=email, password=password)
            if user is not None:
                signup_type = request.data.get('signup_type')
                if signup_type == 'scholarshipProviders':
                    UserProfileScholarshipProvider.objects.get_or_create(user=user)
                user_profile, _ = UserProfile.objects.get_or_create(user=user, account_type="regular", is_host_user=True)
                UserDocuments.objects.get_or_create(user=user)
                UserPreferences.objects.get_or_create(user=user)
                
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                return Response({
                    'message': 'Signup successful',
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Signup successful but login failed'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'Invalid form data', 'error': form.errors}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        return Response({
            "format": {
                "first_name": "Enter your first name",
                "last_name": "Enter your last name",
                "email": "Enter your email id",
                "password1": "Enter your password",
                "password2": "Re-Enter your password"
            }
        }, status=200)

@api_view(['POST', 'GET'])
def login_view(request):
    if request.method == 'POST':
        data = request.data
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(request, username=email, password=password)
            if user is not None:
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                response = {
                    'message': 'Login successful',
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
                response.set_cookie(
                    key='refreshToken',
                    value=str(refresh),
                    httponly=True,
                    max_age=settings.REFRESH_TOKEN_COOKIE_MAX_AGE,  # Set the cookie's lifetime
                    path=settings.REFRESH_TOKEN_COOKIE_PATH,  # Set the cookie path (typically /api/refresh)
                )

                return Response(response, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        return Response({
            "format": {
                "email": "Enter your email id",
                "password": "Enter your password"
            }
        }, status=200)

@api_view(['POST'])
# @permission_classes([IsActivePermission])  # Ensure only active users can log out
def logout_view(request):
    # Retrieve the refresh token from the request data
    refresh_token= request.COOKIES.get('refresh_token')

    if not refresh_token:
        return Response({'message': 'Refresh token not provided'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Validate and blacklist the token
        token = RefreshToken(refresh_token)
        token.blacklist()  # Blacklist the token
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
    except TokenError as e:
        return Response({'message': 'Invalid or expired refresh token', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'message': 'Failed to blacklist token', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)