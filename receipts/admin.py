from django.contrib import admin
from .models import ReceiptFile, Receipt

# Register your models here.

admin.site.register(ReceiptFile)
admin.site.register(Receipt)
