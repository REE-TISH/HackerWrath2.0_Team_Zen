from django.urls import path
from rest_framework_simplejwt.views import ( TokenObtainPairView, TokenRefreshView )
from . import views

urlpatterns = [
    path('chat/<str:session_id>/', views.chat_view, name='chat_view'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Login
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # Refresh
    path('create-user/', views.CreateUserView.as_view(), name='create_user'),  # User Registration
    path('user-chat-session/',views.EachUserSessionView.as_view(),name='user-session'),
    path('create-chat-session/',views.createChatSessionViewFunction,name='create-session'),
]