from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status


from django.contrib.auth import authenticate, login, logout, get_user_model

from userapp.models import UserProfile,UserProfileScholarshipProvider,UserDocuments,UserPreferences
from userapp.forms import CustomUserCreationForm

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
        input_form['username']=generate_unique_username(first_name=input_form['first_name'],last_name=input_form['last_name'])
        form = CustomUserCreationForm(input_form)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                signup_type = request.data['signup_type']
                if signup_type == 'scholarshipProviders':
                    upsp,_=UserProfileScholarshipProvider.objects.get_or_create(user=user)
                else:
                    #NOTE:more signup types can comeup further
                    pass
                user_profile,_ = UserProfile.objects.get_or_create(user=user,account_type="regular",is_host_user=True)
                user_documents,_=UserDocuments.objects.get_or_create(user=user)
                user_preferences,_=UserPreferences.objects.get_or_create(user=user)
                login(request, user)
                return Response({'message': 'Signup successful'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Signup successful but login failed'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'Invalid form data', 'error': form.errors}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        return Response({
            "format":{
                "first_name":"Enter your first name",
                "last_name":"Enter your last name",
                "email":"Enter your email id",
                "password1":"Enter your password",
                "password2":"Re-Enter your password"
            }
            },status=200)
    else:
        return Response({'message': 'Only POST/GET requests are allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST','GET'])
def login_view(request):
    if request.method == 'POST':
        data = request.data
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'Email/Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        return Response({
            "format":{
                "email":"Enter your email id",
                "password":"Enter your password"
            }
            },status=200)
    else:
        return Response({'message': 'Only POST/GET requests are allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
    else:
        return Response({'detail':"You are not authenticated user"},status=status.HTTP_400_BAD_REQUEST)
