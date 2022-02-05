from django.urls import path, include
from user import views

urlpatterns = [
    path('api/register/', views.Registration.as_view(), name='user-create'),
    path('api/login/', views.Login.as_view(), name='user-login'),
    path('api/logout/', views.Logout.as_view(), name='user-logout'),
]