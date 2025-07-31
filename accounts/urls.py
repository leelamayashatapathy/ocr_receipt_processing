
from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    # Template-based URLs (Web Interface)
    path('login/', views.LoginTemplateView.as_view(), name='login'),
    path('register/', views.RegisterTemplateView.as_view(), name='register'),
    
    # API URLs
    path('api/register/', views.RegisterView.as_view(), name='api-register'),
    path('api/login/', views.LoginView.as_view(), name='api-login'),
    path('api/logout/', views.LogoutView.as_view(), name='api-logout'),
]