from userapp.models import EmailVerification

from rest_framework import viewsets, status
from rest_framework.response import Response
# from django.core.mail import send_mail
from tasks import send_email_task,decrypt_data
from navyojan import settings
from userapp.authentication import FirebaseAuthentication
from logs import logger
from rest_framework_simplejwt.authentication import JWTAuthentication

from userapp.permission import IsVerfiedPermission, IsActivePermission

from rest_framework.decorators import action

DEFAULT_AUTH_CLASSES = [JWTAuthentication, FirebaseAuthentication]
class EmailVerificationViewSet(viewsets.ViewSet):
    authentication_classes = DEFAULT_AUTH_CLASSES
    permission_classes = [IsActivePermission]

    def get_permissions(self):
        if self.action in ['send_otp', 'verify_otp']:
            return [IsVerfiedPermission()]
        return super().get_permissions()

    @action(detail=False, methods=['post'], url_path='send-otp')
    def send_otp(self, request):
        user = self.request.user
        email_verification=EmailVerification.objects.create(user=user)  # OTP generation handled in save()
        
        # Send OTP via email
        logger.debug(f"{email_verification.otp} --- {decrypt_data(email_verification.otp)}")
        subject = 'Your OTP Code'
        body = f'''Hi {self.request.user.first_name},\nYour OTP code is {decrypt_data(email_verification.otp)}\n\nRegards\nNavyojan Team'''
        logger.debug(f"sending otp to {user.email}")
        send_email_task.delay(
            subject=subject,
            body=body,
            to_user_emails=[user.email]
        )
        
        return Response({"message": "OTP sent successfully."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='verify-otp')
    def verify_otp(self, request):
        user = request.user
        otp_provided = request.data.get('otp')

        try:
            email_verification = EmailVerification.objects.filter(user=user).order_by('-datetime_created').first()
            decrypted_otp = decrypt_data(email_verification.otp)
            
            if decrypted_otp == otp_provided:
                up = user.userprofile
                up.is_email_verified=True
                up.save()
                subject = 'Email Verified Successfully'
                body = f'''Hi {user.first_name},\nYour email has been successfully verified.\n\nRegards\nNavyojan Team'''

                send_email_task.delay(
                    subject=subject,
                    body=body,
                    to_user_emails=[user.email]
                )
                return Response({"message": "OTP verified successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
        except EmailVerification.DoesNotExist:
            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

