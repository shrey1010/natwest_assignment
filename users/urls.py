from django.urls import path
from .views import RegisterUserView, LoginUserView, LogoutUserView, GetAccessTokenView

urlpatterns = [
    path('register/',RegisterUserView.as_view(), name='register'),
    path('get-access-token/', GetAccessTokenView.as_view(), name='get-access-token'), 
    path('login/', LoginUserView.as_view(), name='login'),
    path('logout/', LogoutUserView.as_view(), name='logout')
]
