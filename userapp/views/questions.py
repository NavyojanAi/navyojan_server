from rest_framework import viewsets,status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response

from userapp.models import QuestionResponses,Questions
from userapp.serializers import QuestionResponsesSerializer, QuestionsSerializer
from userapp.permission import IsActivePermission
from userapp.authentication import FirebaseAuthentication
from userapp.pagination import CustomPagination

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

DEFAULT_AUTH_CLASSES = [JWTAuthentication, FirebaseAuthentication] 

class QuestionResponsesViewSet(viewsets.ModelViewSet):
    queryset = QuestionResponses.objects.all()
    serializer_class = QuestionResponsesSerializer
    permission_classes = [IsActivePermission]
    authentication_classes = DEFAULT_AUTH_CLASSES

    def get_queryset(self):
        filtered_queryset = self.queryset.filter(content_type__model='user', object_id=self.request.user.id)
        return filtered_queryset
    



class QuestionResponsesBulkViewSet(viewsets.ModelViewSet):
    queryset = QuestionResponses.objects.all()
    serializer_class = QuestionResponsesSerializer
    permission_classes = [IsActivePermission]  
    authentication_classes = DEFAULT_AUTH_CLASSES

    @swagger_auto_schema(
        operation_description="Create multiple question responses in bulk.",
        operation_summary="Bulk create question responses",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['question_responses'],
            properties={
                'question_responses': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'question': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'answer': openapi.Schema(type=openapi.TYPE_STRING),
                            'content_type': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'object_id': openapi.Schema(type=openapi.TYPE_INTEGER)
                        }
                    )
                )
            }
        )
    )
    def create(self, request, *args, **kwargs):
        question_responses_data = request.data.get('question_responses', [])

        if not question_responses_data:
            return Response({'error': 'No question responses provided'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=question_responses_data, many=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class QuestionsViewSet(viewsets.ModelViewSet):
    queryset = Questions.objects.all()
    serializer_class = QuestionsSerializer
    permission_classes = [IsActivePermission]
    authentication_classes = DEFAULT_AUTH_CLASSES
    pagination_class = CustomPagination
    http_method_names = ["get"]

    @swagger_auto_schema(
        operation_description="Retrieve a list of questions.",
        operation_summary="Get questions",
        manual_parameters=[
            openapi.Parameter(
                'category',
                openapi.IN_QUERY,
                description="Filter questions by category",
                type=openapi.TYPE_INTEGER
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Filter questions based on category from query parameters
        category = request.query_params['category']
        if category:
            queryset = queryset.filter(category=category)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
