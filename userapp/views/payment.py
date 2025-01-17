import razorpay
from datetime import timedelta


from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.conf import settings
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction

from userapp.models import SubscriptionPlan, UserPlanTracker, UserPayments
from userapp.serializers import UserPaymentsSerializer
from userapp.permission import IsActivePermission
from django.contrib.auth.models import User
from userapp.authentication import FirebaseAuthentication

from logs.logger_setup import logger


DEFAULT_AUTH_CLASSES = [JWTAuthentication, FirebaseAuthentication]

# authorize razorpay client with API Keys.
razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET)
)


class PaymentRequestView(APIView):
    authentication_classes = DEFAULT_AUTH_CLASSES
    permission_classes = [IsAuthenticated]
    def post(self, request):
        currency = "INR"
        plan_id = request.data.get("plan_id")
        user_id = self.request.user.id
        logger.debug(f"User ID: {user_id}")
        try:
            plan = SubscriptionPlan.objects.get(id=plan_id)
            # Convert amount to paise (multiply by 100)
            amount = int(float(plan.amount))

            # Create a Razorpay Order
            razorpay_order = razorpay_client.order.create(
                dict(amount=amount, currency=currency, payment_capture="1")
            )

            # order id of newly created order.
            razorpay_order_id = razorpay_order["id"]

            # we need to pass these details to frontend.
            context = {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_merchant_key": settings.RAZOR_KEY_ID,
                "razorpay_amount": amount,
                "currency": currency,
                "plan_id": plan_id,
                "user_id": user_id,
                "callback_url": "/api/paymenthandler/",
            }

            return Response(context, status=status.HTTP_200_OK)
        except SubscriptionPlan.DoesNotExist:
            logger.debug(f"Plan with id {plan_id} does not exist.")
            return Response(
                {"error": "Plan not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.debug(f"Error creating payment request: {str(e)}")
            return Response(
                {"error": "An error occurred while creating the payment request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(csrf_exempt, name="dispatch")
class PaymentHandlerView(APIView):
    @transaction.atomic
    def post(self, request):
        try:
            # get the required parameters from post request.
            payment_id = request.data.get("razorpay_payment_id", "")
            razorpay_order_id = request.data.get("razorpay_order_id", "")
            signature = request.data.get("razorpay_signature", "")
            amount = request.data.get("razorpay_amount", "")
            user_id = request.data.get("user_id", "")

            try:
                amount = int(float(amount))
            except (TypeError, ValueError):
                logger.debug(f"Invalid amount format: {amount}")
                return Response(
                    {"error": "Invalid amount format"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            params_dict = {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            }
            logger.debug(f"Payment signature verification result: {params_dict}")
            logger.debug(f"Amount: {amount}")
            # verify the payment signature.
            result = razorpay_client.utility.verify_payment_signature(params_dict)
            logger.debug(f"Payment signature verification result: {result}")
            if result is not None:
                plan_id = request.data.get("plan_id")
                plan = SubscriptionPlan.objects.get(id=plan_id)

                try:
                    # Check if payment already exists
                    if UserPayments.objects.filter(payment_id=payment_id).exists():
                        logger.debug(f"Payment {payment_id} has already been processed")
                        return Response(
                            {"message": "Payment already processed"},
                            status=status.HTTP_200_OK,
                        )

                    # Try to capture the payment
                    payment = razorpay_client.payment.fetch(payment_id)
                    if payment["status"] != "captured":
                        razorpay_client.payment.capture(payment_id, amount)

                    logger.debug(
                        f"Payment captured successfully for plan {plan_id} with amount {amount}"
                    )
                    user = User.objects.get(id=user_id)
                    logger.debug(
                        f"User {user.id} is making payment for plan {plan_id} with amount {amount}"
                    )
                    user_plan = UserPlanTracker.objects.create(
                        user=user,
                        plan=plan,
                        end_date=now() + timedelta(days=plan.duration),
                    )
                    logger.debug(
                        f"User plan created for user {user.id} with plan {plan_id} and end date {user_plan.end_date}"
                    )
                    user_payments = UserPayments.objects.create(
                        user=user,
                        plan=plan,
                        razorpay_order_id=razorpay_order_id,
                        payment_id=payment_id,
                        signature=signature,
                    )
                    logger.debug(
                        f"User payment created for user {user.id} with plan {plan_id} and payment ID {payment_id}"
                    )
                    userprofile = user.userprofile
                    userprofile.plan = plan
                    userprofile.save()
                    return Response(
                        {"message": "Payment successful"}, status=status.HTTP_200_OK
                    )
                except Exception as e:
                    logger.debug(f"Payment capture failed: {str(e)}")
                    return Response(
                        {"error": "Payment capture failed"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                logger.debug("Signature verification failed.")
                return Response(
                    {"error": "Signature verification failed"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except SubscriptionPlan.DoesNotExist:
            logger.debug(f'Plan with id {request.data.get("plan_id")} does not exist.')
            return Response(
                {"error": "Plan not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.debug(f"Error processing payment: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        return Response(
            {"error": "GET method not allowed"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


class CheckUserSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        current_date = now()

        try:
            active_plan = UserPlanTracker.objects.get(
                user=user, end_date__gt=current_date
            )

            plan_data = {
                "has_active_plan": True,
                "plan_name": active_plan.plan.name,
                "end_date": active_plan.end_date,
            }
        except UserPlanTracker.DoesNotExist:
            plan_data = {"has_active_plan": False}

        return Response(plan_data, status=status.HTTP_200_OK)


class UserPaymentsViewset(ModelViewSet):
    queryset = UserPayments.objects.all()
    serializer_class = UserPaymentsSerializer
    authentication_classes = DEFAULT_AUTH_CLASSES
    permission_classes = [IsActivePermission]
    http_method_names = ["get"]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        response_data = {"results": serializer.data}

        return Response(response_data)
