from userapp.models import Verification

from rest_framework import viewsets, status
from rest_framework.response import Response
# from django.core.mail import send_mail
from tasks import send_email_task,decrypt_data,send_text_task
from navyojan import settings
from userapp.authentication import FirebaseAuthentication
from logs import logger 
from rest_framework_simplejwt.authentication import JWTAuthentication

from userapp.permission import IsVerifiedPermission, IsActivePermission

from rest_framework.decorators import action

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

DEFAULT_AUTH_CLASSES = [JWTAuthentication, FirebaseAuthentication]
class VerificationViewSet(viewsets.ViewSet):
    authentication_classes = DEFAULT_AUTH_CLASSES
    permission_classes = [IsActivePermission]

    def get_permissions(self):
        if self.action in ['send_otp', 'verify_otp']:
            return [IsVerifiedPermission()]
        return super().get_permissions()

    @action(detail=False, methods=['post'], url_path='send-otp')
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'verification_type': openapi.Schema(type=openapi.TYPE_STRING, description='Type of verification: "email" or "phone".')
            },
            required=['verification_type']
        ),
        responses={
            200: openapi.Response('OTP sent successfully.'),
            400: openapi.Response('Invalid request.')
        }
    )
    def send_otp(self, request):
        user = self.request.user
        verification_type = request.data.get('verification_type')  # 'email' or 'phone'
        
        verification = Verification.objects.create(user=user, verification_type=verification_type)  # OTP generation handled in save()
        
        if verification_type == 'email':
            # Send OTP via email
            logger.debug(f"{verification.otp} --- {decrypt_data(verification.otp)}")
            subject = 'Your OTP Code'
            body = f'''Hi {user.first_name},\nYour OTP code is {decrypt_data(verification.otp)}\n\nRegards\nNavyojan Team'''
            logger.debug(f"sending otp to {user.email}")
            send_email_task.delay(
                subject=subject,
                body=body,
                to_user_emails=[user.email]
            )
        elif verification_type == 'phone':
            # Send OTP via SMS
            logger.debug(f"{verification.otp} --- {decrypt_data(verification.otp)}")
            message = f"Hi {user.first_name}, your OTP code is {decrypt_data(verification.otp)}"
            logger.debug(f"sending otp to {user.phone_number}")
            send_text_task.delay(
                phone_number=user.phone_number,
                message=message
            )
        
        return Response({"message": "OTP sent successfully."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='verify-otp')
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'otp': openapi.Schema(type=openapi.TYPE_STRING, description='The OTP code provided by the user.'),
                'verification_type': openapi.Schema(type=openapi.TYPE_STRING, description='Type of verification: "email" or "phone".')
            },
            required=['otp', 'verification_type']
        ),
        responses={
            200: openapi.Response('OTP verified successfully.'),
            400: openapi.Response('Invalid OTP.')
        }
    )
    def verify_otp(self, request):
        user = request.user
        otp_provided = request.data.get('otp')
        verification_type = request.data.get('verification_type')  # 'email' or 'phone'

        try:
            verification = Verification.objects.filter(user=user, verification_type=verification_type).order_by('-datetime_created').first()
            decrypted_otp = decrypt_data(verification.otp)
            
            if decrypted_otp == otp_provided:
                up = user.userprofile
                if verification_type == 'email':
                    up.is_email_verified = True
                    subject = 'Email Verified Successfully'
                    body = f'''Hi {user.first_name},\nYour email has been successfully verified.\n\nRegards\nNavyojan Team'''
                    send_email_task.delay(
                        subject=subject,
                        body=body,
                        to_user_emails=[user.email]
                    )
                elif verification_type == 'phone':
                    up.is_phone_verified = True
                    message = f"Hi {user.first_name}, your phone number has been successfully verified."
                    send_text_task.delay(
                        phone_number=user.phone_number,
                        message=message
                    )
                up.save()
                return Response({"message": "OTP verified successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
        except Verification.DoesNotExist:
            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)


