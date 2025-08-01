from django.urls import path
from . import views

app_name = 'receipts'

urlpatterns = [
    # Template-based URLs (Web Interface)
    path('', views.HomeView.as_view(), name='home'),
    path('upload/', views.UploadTemplateView.as_view(), name='upload'),
    path('receipts/', views.ReceiptsListTemplateView.as_view(), name='receipts'),
    path('extract-text/', views.ExtractTextTemplateView.as_view(), name='extract-text'),
    path('receipts/<int:pk>/', views.ReceiptDetailTemplateView.as_view(), name='receipt-detail'),
    
    # API URLs
    path('api/upload/', views.UploadReceiptView.as_view(), name='api-upload'),
    path('api/validate/', views.ValidateReceiptView.as_view(), name='api-validate'),
    path('api/process/', views.ProcessReceiptView.as_view(), name='api-process'),
    path('api/extract-text/', views.ExtractTextView.as_view(), name='api-extract-text'),
    path('api/receipts/', views.ReceiptsListView.as_view(), name='api-receipts'),
    path('api/receipts/<int:id>/', views.ReceiptDetailView.as_view(), name='api-receipt-detail'),
] 