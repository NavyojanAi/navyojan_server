from userapp.models import EmailVerification

from rest_framework import viewsets, status
from rest_framework.response import Response
from django.core.mail import send_mail
from scripts import decrypt_data
from navyojan import settings
from rest_framework.decorators import action

class EmailVerificationViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['post'], url_path='send-otp')
    def send_otp(self, request):
        user = request.user
        email_verification=EmailVerification.objects.create(user=user)  # OTP generation handled in save()
        
        # Send OTP via email
        print(f"{email_verification.otp} --- {decrypt_data(email_verification.otp)}")
        send_mail(
            'Your OTP Code',
            f'Your OTP code is {decrypt_data(email_verification.otp)}',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        
        return Response({"message": "OTP sent successfully."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='verify-otp')
    def verify_otp(self, request):
        user = request.user
        otp_provided = request.data.get('otp')

        try:
            email_verification = EmailVerification.objects.filter(user=user).order_by('-created_at').first()
            decrypted_otp = decrypt_data(email_verification.otp)
            
            if decrypted_otp == otp_provided:
                up = user.userprofile
                up.is_email_verified=True
                up.save()
                return Response({"message": "OTP verified successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
        except EmailVerification.DoesNotExist:
            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

