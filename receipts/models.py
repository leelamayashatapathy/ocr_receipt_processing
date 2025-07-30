from django.db import models

# Create your models here.

class ReceiptFile(models.Model):
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=512)
    is_valid = models.BooleanField(default=False)
    invalid_reason = models.TextField(null=True, blank=True)
    is_processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.file_name

class Receipt(models.Model):
    purchased_at = models.DateTimeField(null=True, blank=True)
    merchant_name = models.CharField(max_length=255, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    file_path = models.CharField(max_length=512)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.merchant_name} - {self.purchased_at}"
