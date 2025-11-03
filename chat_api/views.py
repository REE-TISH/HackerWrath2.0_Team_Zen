from rest_framework.decorators import api_view,permission_classes
from chat_api.serializer import UserSerializer
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.response import Response
from Langgraph.main import runChat
# Create your views here.

@api_view(['POST'])
def chat_view(request, *args, **kwargs):
    response = runChat(request.data['data'])
    return Response({
        'chat_response':response
    })


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
