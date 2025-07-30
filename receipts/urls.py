from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.UploadReceiptView.as_view(), name='upload'),
    path('validate/', views.ValidateReceiptView.as_view(), name='validate'),
    path('process/', views.ProcessReceiptView.as_view(), name='process-tesseract'),
    path('receipts/', views.ReceiptsListView.as_view(), name='receipts'),
    path('receipts/<int:id>/', views.ReceiptDetailView.as_view(), name='receipt-detail'),
] 