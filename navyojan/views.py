from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie


@ensure_csrf_cookie
def ensure_csrf(request):
    return JsonResponse({"status": "success"}, status=200)
