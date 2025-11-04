from rest_framework.serializers import ModelSerializer
from .models import EachUserSession,ChatMessages
from django.contrib.auth.models import User


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email','password']

class ChatMessagesSerializer(ModelSerializer):

    class Meta:
        model = ChatMessages
        fields = ['id','content','isUser']

class EachUserChatSerializer(ModelSerializer):

    messages = ChatMessagesSerializer(many=True,read_only=True)

    class Meta:
        model = EachUserSession
        fields = ['id','topic','messages']
        