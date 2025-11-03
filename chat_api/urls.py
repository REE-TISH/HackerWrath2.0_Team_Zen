from django.urls import path
from rest_framework_simplejwt.views import ( TokenObtainPairView, TokenRefreshView )
from . import views

urlpatterns = [
    path('chat/', views.chat_view, name='chat_view'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Login
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # Refresh
    path('create-user/', views.CreateUserView.as_view(), name='create_user'),  # User Registration
]