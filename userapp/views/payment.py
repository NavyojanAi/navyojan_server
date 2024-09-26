from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from userapp.models import SubscriptionPlan,UserPlanTracker
from rest_framework.permissions import IsAuthenticated

from django.utils.timezone import now
from datetime import timedelta
# authorize razorpay client with API Keys.
razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

class PaymentRequestView(APIView):
    def post(self, request):
        currency = 'INR'
        plan_id = request.data.get('plan_id')
        plan = SubscriptionPlan.objects.get(id=plan_id)
        amount = plan.amount

        # Create a Razorpay Order
        razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                           currency=currency,
                                                           payment_capture='0'))

        # order id of newly created order.
        razorpay_order_id = razorpay_order['id']

        # we need to pass these details to frontend.
        context = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_merchant_key': settings.RAZOR_KEY_ID,
            'razorpay_amount': amount,
            'currency': currency,
            'plan_id': plan_id
        }

        return Response(context, status=status.HTTP_200_OK)

@method_decorator(csrf_exempt, name='dispatch')
class PaymentHandlerView(APIView):
    def post(self, request):
        try:
            # get the required parameters from post request.
            payment_id = request.data.get('razorpay_payment_id', '')
            razorpay_order_id = request.data.get('razorpay_order_id', '')
            signature = request.data.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            # verify the payment signature.
            result = razorpay_client.utility.verify_payment_signature(
                params_dict)
            if result is not None:
                plan_id = request.data.get('plan_id')
                plan = SubscriptionPlan.objects.get(id=plan_id)
                amount = plan.amount 
                try:
                    # capture the payment
                    razorpay_client.payment.capture(payment_id, amount)
                    user = request.user
                    user_plan = UserPlanTracker.objects.create(user=user, plan=plan, end_date=now() + timedelta(days=plan.duration))
                    return Response({'message': 'Payment successful'}, status=status.HTTP_200_OK)
                except:
                    return Response({'error': 'Payment capture failed'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Signature verification failed'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'error': 'Invalid POST data'}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        return Response({'error': 'GET method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

class CheckUserSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        current_date = now()
        
        try:
            active_plan = UserPlanTracker.objects.get(
                user=user,
                end_date__gt=current_date
            )
            
            plan_data = {
                'has_active_plan': True,
                'plan_name': active_plan.plan.name,
                'end_date': active_plan.end_date
            }
        except UserPlanTracker.DoesNotExist:
            plan_data = {
                'has_active_plan': False
            }
        
        return Response(plan_data, status=status.HTTP_200_OK)

