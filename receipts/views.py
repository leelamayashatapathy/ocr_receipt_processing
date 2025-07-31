from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum, Q
from django.views.generic import TemplateView, ListView, DetailView
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import ReceiptFile, Receipt
from .serializers import ReceiptFileSerializer
import os
from django.conf import settings
from django.utils import timezone
import hashlib
import fitz  
import pytesseract
from django.http import Http404
import re
from datetime import datetime
import numpy as np
from pdf2image import convert_from_path
import json

# Authentication Views
class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            })
        else:
            return Response({'error': 'Invalid credentials'}, status=400)

class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=400)
        
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists'}, status=400)
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        })

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Successfully logged out'})
        except Exception:
            return Response({'message': 'Successfully logged out'})

# Template Views
class HomeView(TemplateView):
    template_name = 'receipts/home.html'

class LoginTemplateView(TemplateView):
    template_name = 'receipts/login.html'

class RegisterTemplateView(TemplateView):
    template_name = 'receipts/register.html'

class UploadTemplateView(TemplateView):
    template_name = 'receipts/upload.html'

class ReceiptsListTemplateView(ListView):
    model = Receipt
    template_name = 'receipts/receipts_list.html'
    context_object_name = 'receipts'
    paginate_by = 10

    def get_queryset(self):
        queryset = Receipt.objects.all().order_by('-created_at')
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(merchant_name__icontains=search_query) |
                Q(total_amount__icontains=search_query)
            )
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calculate summary statistics
        receipts = Receipt.objects.all()
        context['total_amount'] = receipts.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        context['processed_count'] = receipts.filter(total_amount__isnull=False).count()
        context['pending_count'] = receipts.filter(total_amount__isnull=True).count()
        
        return context

class ReceiptDetailTemplateView(DetailView):
    model = Receipt
    template_name = 'receipts/receipt_detail.html'
    context_object_name = 'receipt'

# Text Extraction View
class ExtractTextView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, format=None):
        file_id = request.data.get('file_id')
        try:
            receipt_file = ReceiptFile.objects.get(id=file_id)
        except ReceiptFile.DoesNotExist:
            return Response({'detail': 'Receipt not found.'}, status=404)

        try:
            poppler_path = r"C:\poppler\poppler-24.08.0\Library\bin"
            images = convert_from_path(receipt_file.file_path, poppler_path=poppler_path)

            raw_text = ''
            for img in images:
                raw_text += pytesseract.image_to_string(
                    img,
                    config='--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,$:/- '
                )

            return Response({
                'extracted_text': raw_text,
                'file_name': receipt_file.file_name
            })

        except Exception as e:
            return Response({
                'detail': 'Could not extract text from receipt.',
                'error': str(e)
            }, status=500)

# API Views (existing)
class UploadReceiptView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        file_obj = request.FILES.get('file')
        if not file_obj or not file_obj.name.lower().endswith('.pdf'):
            return Response({'detail': 'Invalid file. Only PDFs allowed.'}, status=400)

        # Compute file hash for duplicate detection
        file_hash = hashlib.sha256(file_obj.read()).hexdigest()
        file_obj.seek(0)
        file_name = file_obj.name
        save_dir = os.path.join(settings.MEDIA_ROOT, 'receipts')
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, file_name)

        existing = ReceiptFile.objects.filter(file_name=file_name).first()
        if existing:
            existing.updated_at = timezone.now()
            existing.save()
            return Response(ReceiptFileSerializer(existing).data, status=200)

        with open(file_path, 'wb+') as destination:
            for chunk in file_obj.chunks():
                destination.write(chunk)

        receipt_file = ReceiptFile.objects.create(
            file_name=file_name,
            file_path=file_path,
            is_valid=False,
            is_processed=False
        )
        serializer = ReceiptFileSerializer(receipt_file)
        return Response(serializer.data, status=201)

class ValidateReceiptView(APIView):
    def post(self, request, format=None):
        file_id = request.data.get('file_id')
        try:
            receipt_file = ReceiptFile.objects.get(id=file_id)
        except ReceiptFile.DoesNotExist:
            return Response({'detail': 'Receipt not found.'}, status=404)
        try:
            with fitz.open(receipt_file.file_path) as doc:
                if doc.page_count == 0:
                    raise ValueError('PDF has no pages.')
            receipt_file.is_valid = True
            receipt_file.invalid_reason = None
        except Exception as e:
            receipt_file.is_valid = False
            receipt_file.invalid_reason = str(e)
        receipt_file.save()
        return Response({
            'is_valid': receipt_file.is_valid,
            'invalid_reason': receipt_file.invalid_reason
        })

class ProcessReceiptView(APIView):
    def preprocess_ocr_text(self, text: str) -> str:
        text = re.sub(r'(\d{1,2}/\d{1,2}/\d{2})(\d{1,2}:\d{2}[APMapm]{2})', r'\1 \2', text)
        return text

    def post(self, request, format=None):
        file_id = request.data.get('file_id')
        try:
            receipt_file = ReceiptFile.objects.get(id=file_id)
        except ReceiptFile.DoesNotExist:
            return Response({'detail': 'Receipt not found.'}, status=404)

        if not receipt_file.is_valid:
            return Response({'detail': 'File is not valid.'}, status=400)

        try:
            poppler_path = r"C:\poppler\poppler-24.08.0\Library\bin"
            images = convert_from_path(receipt_file.file_path, poppler_path=poppler_path)

            raw_text = ''
            for img in images:
                raw_text += pytesseract.image_to_string(
                    img,
                    config='--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,$:/- '
                )

            print("Tesseract extracted text:")
            print(raw_text)

            # Preprocess OCR text
            text = self.preprocess_ocr_text(raw_text)
            lines = [line.strip() for line in text.splitlines() if line.strip()]

          
            merchant_name = None
            business_keywords = [
                'RESTAURANT', 'STORE', 'SHOP', 'CAFE', 'MARKET', 'GROCERY',
                'LLC', 'INC', 'BAKERY', 'PHARMACY', 'DINER', 'GRILL', 'DELI'
            ]
            skip_keywords = [
                'DINEIN', 'ORDER', 'TABLE', 'SERVER', 'TOTAL', 'SUBTOTAL', 'TAX',
                'THANK', 'YOUR', 'GUESTS', 'AMOUNT', 'COPY'
            ]

            def looks_like_business_name(line):
                line_upper = line.upper()
                if any(kw in line_upper for kw in skip_keywords):
                    return False
                if re.search(r'\d{2}[\/\-\.]\d{2}[\/\-\.]\d{2,4}', line):  # date
                    return False
                if re.search(r'[\d,]+\.\d{2}', line):  # amount
                    return False
                if any(kw in line_upper for kw in business_keywords):
                    return True
                alpha_ratio = sum(c.isalpha() for c in line) / max(len(line), 1)
                return alpha_ratio > 0.5

            for line in lines[:10]:
                if looks_like_business_name(line):
                    merchant_name = line.strip()
                    break

            if not merchant_name and len(lines) >= 3:
                merchant_name = lines[1].strip()

            if merchant_name:
                merchant_name = re.sub(r'\d+$', '', merchant_name).strip()

         
            purchased_at = None
            date_patterns = [
                r'\d{2}/\d{2}/\d{4} \d{1,2}:\d{2}',     
                r'\d{2}/\d{2}/\d{2} \d{1,2}:\d{2}',    
                r'\d{2}/\d{2}/\d{4}',                    
                r'\d{2}/\d{2}/\d{2}',                    
                r'\d{4}-\d{2}-\d{2}',                    
                r'\d{2}-\d{2}-\d{4}',                   
                r'\d{2}/\d{2}/\d{2}\d{1,2}:\d{2}[APMapm]{2}',  
            ]

            for pattern in date_patterns:
                match = re.search(pattern, text)
                if match:
                    date_str = match.group(0)
                    for fmt in [
                        "%m/%d/%Y %H:%M", "%m/%d/%y %H:%M",
                        "%m/%d/%Y", "%m/%d/%y",
                        "%Y-%m-%d", "%d-%m-%Y",
                        "%m/%d/%y%I:%M%p"
                    ]:
                        try:
                            purchased_at = datetime.strptime(date_str, fmt)
                            break
                        except ValueError:
                            continue
                if purchased_at:
                    break

            
            total_amount = None
            total_patterns = [
                r'TOTAL\s+([\d,]+\.\d{2})',
                r'TOTAL:\s*([\d,]+\.\d{2})',
                r'TOTAL\s*\$([\d,]+\.\d{2})',
                r'GRAND\s*TOTAL\s*[:$]?\s*([\d,]+\.\d{2})',
                r'AMOUNT\s*[:$]?\s*([\d,]+\.\d{2})',
                r'BALANCE\s*[:$]?\s*([\d,]+\.\d{2})',
            ]

            for pattern in total_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        total_amount = float(match.group(1).replace(',', ''))
                        break
                    except ValueError:
                        continue

            if not total_amount:
                amounts = re.findall(r'[\d,]+\.\d{2}', text)
                if amounts:
                    try:
                        total_amount = max([float(a.replace(',', '')) for a in amounts])
                    except ValueError:
                        pass

         
            receipt = Receipt.objects.create(
                purchased_at=purchased_at,
                merchant_name=merchant_name,
                total_amount=total_amount,
                file_path=receipt_file.file_path
            )
            receipt_file.is_processed = True
            receipt_file.save()

            return Response({
                'receipt_id': receipt.id,
                'merchant_name': receipt.merchant_name,
                'total_amount': receipt.total_amount,
                'purchased_at': receipt.purchased_at
            })

        except Exception as e:
            return Response({
                'detail': 'Could not extract text from receipt.',
                'error': str(e)
            }, status=500)

class ReceiptsListView(APIView):
    def get(self, request, format=None):
        receipts = Receipt.objects.all()
        data = [
            {
                'id': r.id,
                'merchant_name': r.merchant_name,
                'total_amount': r.total_amount,
                'purchased_at': r.purchased_at
            } for r in receipts
        ]
        return Response(data)

class ReceiptDetailView(APIView):
    def get(self, request, id, format=None):
        try:
            r = Receipt.objects.get(id=id)
        except Receipt.DoesNotExist:
            return Response({'detail': 'Receipt not found.'}, status=404)
        data = {
            'id': r.id,
            'merchant_name': r.merchant_name,
            'total_amount': r.total_amount,
            'purchased_at': r.purchased_at,
            'file_path': r.file_path
        }
        return Response(data)

    def delete(self, request, id, format=None):
        try:
            receipt = Receipt.objects.get(id=id)
            receipt.delete()
            return Response({'detail': 'Receipt deleted successfully.'}, status=204)
        except Receipt.DoesNotExist:
            return Response({'detail': 'Receipt not found.'}, status=404)
