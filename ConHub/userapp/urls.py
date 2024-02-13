from django.urls import path
from .views import Signup, Register, RegisterActivation, Login, Logout, Homepage


app_name = 'userapp'
urlpatterns = [
    # path('profile/', ProfilePage.as_view(), name='profile'),
    path('signup/', Signup.as_view(), name='signup'),
    path('register/<str:activation_key>/', RegisterActivation.as_view(), name='register_activation'),
    path('register/', Register.as_view(), name='register'),
    path('login', Login.as_view(), name='login'),
    path('logout/', Logout, name='logout'),
    path('', Homepage.as_view(), name='home'),
]