from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from chat_api.serializer import UserSerializer,ChatMessagesSerializer,EachUserChatSerializer
from django.contrib.auth.models import User
from .models import EachUserSession,ChatMessages
from rest_framework import generics
from rest_framework.response import Response
from Langgraph.main import runChat
# Create your views here.

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_view(request, *args, **kwargs):
    response = runChat(request.data['data'])
    session = EachUserSession.objects.get(id=kwargs['session_id'])
    ChatMessages.objects.create(related_Session=session,content=request.data['data'],isUser=True)
    response_model = ChatMessages.objects.create(related_Session=session,content=response,isUser=False)
    return Response({
        'id':response_model.id,
        'content':response,
        'isUser':False
    })

class EachUserSessionView(generics.ListAPIView):
    queryset = EachUserSession.objects.prefetch_related('messages').all()
    serializer_class = EachUserChatSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        qs = EachUserSession.objects.filter(related_user=self.request.user)
        return qs

class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CreateChatSessionView(generics.CreateAPIView):
    queryset = EachUserSession.objects.all()
    serializer_class = EachUserChatSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createChatSessionViewFunction(request):
    EachUserSession.objects.create(related_user=request.user,topic=f"{request.user.username} New_chat ")
    return Response({'status':'success'})
