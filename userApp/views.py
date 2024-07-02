import io
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.crypto import get_random_string
import plotly
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import CustomUser
from . serializers import CustomUserSerializer
import random
import string
from feedbackApp.serializers import FeedbackSerializer
from feedbackApp.models import Feedback
import io
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph
from rest_framework.decorators import api_view
from .models import CustomUser
from .serializers import CustomUserSerializer



@api_view(['GET'])
def index(request):
    return Response({"message": "Welcome to the accounts API"})


@api_view(['POST'])
def signup(request):
    data = request.data
    email = data.get('email')
    phone = data.get('phone')
    username = data.get('username')
    password = data.get('password')
    # name = data.get('name')
    role='user'
    
    password1 = make_password(password)

    # Check if email is provided and not empty
    if not email or not email.strip():
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if email already exists in the database
    if CustomUser.objects.filter(email=email).exists():
        return Response({'error': 'Email is already registered'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if phone number is provided and valid
    if not phone or not phone.strip():
        return Response({'error': 'Phone number is required'}, status=status.HTTP_400_BAD_REQUEST)
    if len(phone) != 10 or not phone.isdigit():
        return Response({'error': 'Phone number must be 10 digits'}, status=status.HTTP_400_BAD_REQUEST)


    # Check if phone number already exists in the database
    if CustomUser.objects.filter(phone=phone).exists():
        return Response({'error': 'Phone number is already registered'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if username is provided and not empty
    if not username or not username.strip():
        return Response({'error': 'Username is required'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if username already exists in the database
    if CustomUser.objects.filter(username=username).exists():
        return Response({'error': 'Username is already taken'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = CustomUser.objects.create(username=username, email=email, phone=phone, password=password1, role=role)

        # Send email with account details
        subject = 'Your Account Details'
        message = f'Hello,\n\nThank you for signing up with us. Here are your account details:\n\nUsername: {username}\nPassword: {password}\n\nPlease verify your password using these credentials.'
        from_email = 'Policy-Link-Rwanda'
        recipient_list = [email]
        send_mail(subject, message, from_email, recipient_list)

        return Response({'message': 'User saved successfully'},
                        status=status.HTTP_200_OK)
    except:
        print('\n\n Failed to save user\n\n')
        return Response({'error': 'Failed to save data'}, status=status.HTTP_400_BAD_REQUEST)





# serializers.py
from rest_framework import serializers
from userApp.models import CustomUser

class AdminFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'user', 'request', 'feedback']

class StaffFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['feedback']

@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    try:
        user = CustomUser.objects.get(username=username)
        if not check_password(password, user.password):
            return Response({'error': 'Invalid password.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if user.role == 'admin':
                print('Login successful, you have logged in as admin')
                return Response({
                    'message': 'Login successful, you have logged in as admin',
                    'role': 'admin'
                }, status=status.HTTP_200_OK)
            elif user.role == 'user':
                print('Login successful, you have logged in as user')
                return Response({
                    'message': 'Login successful',
                    'role': 'user'
                }, status=status.HTTP_200_OK)
            else:
                print(f'Unknown user role: {user.role}')
                return Response({'message': 'Login successfully', 'role': user.role}, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response({'error': 'Invalid username.'}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def user_dashboard(request):
    return Response({"message": "Welcome to the user dashboard"})


@api_view(['GET'])
def admin_dashboard(request):
    return Response({"message": "Welcome to the admin dashboard"})



@api_view(['GET'])
def staff_dashboard(request):
    return Response({"message": "Welcome to the staff dashboard"})


@api_view(['GET'])
def view_all_users(request):
    users = CustomUser.objects.all()
    serializer = CustomUserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['PUT'])
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    data = request.data

    serializer = CustomUserSerializer(user, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_user(request, user_id):
    try:
        user = CustomUser.objects.get(pk=user_id)
        user.delete()
        return Response({'success': True}, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def logout_view(request):
    logout(request)
    return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)




'''
    Reports about users
'''


from django.http import HttpResponse, JsonResponse
from .models import CustomUser
from django.db.models import Count


@api_view(['GET'])
def total_users(request):
    total_users = CustomUser.objects.count()
    return JsonResponse({'total_users': total_users})





@api_view(['GET'])
def all_users(request):
    users = CustomUser.objects.all()
    user_data = [{'username': user.username, 'email': user.email, 'role': user.role} for user in users]
    return JsonResponse({'users': user_data})





from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import CustomUser

@api_view(['POST'])

def reset_password(request):
    username = request.data.get('username')
    email = request.data.get('email')
    new_password = request.data.get('new_password')

    try:
        user = CustomUser.objects.get(username=username, email=email)
        
        # Update the user's password
        user.password = make_password(new_password)
        user.save()

        # Send email notification about the password change
        subject = 'Your Password Has Been Changed'
        message = f'Hello {user.username},\n\nYour password has been successfully changed.\n\nIf you did not request this change, please contact support immediately.'
        from_email = 'Policy-Link-Rwanda'
        recipient_list = [email]
        send_mail(subject, message, from_email, recipient_list)

        return Response({'message': 'Password changed successfully. Please check your email for confirmation.'}, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response({'error': 'Invalid username or email.'}, status=status.HTTP_400_BAD_REQUEST)




# userAccount/views.py
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import CustomUser

def get_user_by_id(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'phone': user.phone,
        'role': user.role,
        'created_at': user.created_at,
        'last_login': user.last_login,
    }
    return JsonResponse(user_data)








@api_view(['POST'])
def create_user(request):
    data = request.data
    email = data.get('email')
    phone = data.get('phone')
    first_name = data.get('firstname')
    last_name = data.get('lastname')
    role = data.get('role')

    # Generate a unique username based on the first name and a random 3-digit number from the phone number
    username = first_name[:5] + ''.join(random.choices(string.digits, k=3))

    # Generate a random password
    password = get_random_string(length=6)

    try:
        user = CustomUser.objects.create_user(
            email=email,
            username=username,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            password=password,
            role=role
        )

        # Send email with account details
        subject = 'Your Account Details'
        message = f'Hello {first_name} {last_name},\n\nThank you for signing up with us. Here are your account details:\n\nUsername: {username}\nPassword: {password}\n\nPlease verify your password using these credentials.'
        from_email = 'Policy-Link-Rwanda'
        recipient_list = [email]
        send_mail(subject, message, from_email, recipient_list)

        return Response({'message': 'User created successfully. Check your email for login details.'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
    
    
@api_view(['GET'])
def download_users_pdf(request):
    users = CustomUser.objects.all()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    data = [['Username', 'Email', 'Phone', 'Role']]
    style = getSampleStyleSheet()
    phone_style = ParagraphStyle('phone_style', fontSize=12, leading=14)

    for user in users:
        username = user.username
        email = user.email
        # email_text = '\n'.join([user.email[i:i+10] for i in range(0, len(user.email), 17)])
        phone_text = ' '.join([user.phone[i:i+10] for i in range(0, len(user.phone), 10)])
        role = user.role
        phone_paragraph = Paragraph(phone_text, phone_style)
        data.append([username, email, phone_paragraph, role])

    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])

    table = Table(data)
    table.setStyle(table_style)
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="users.pdf"'
    return response

import pandas as pd

@api_view(['GET'])
def download_users_excel(request):
    users = CustomUser.objects.all()
    data = [{
        'Username': user.username,
        'Email': user.email,
        'Phone': user.phone,
        'Role': user.role,
        # 'First Name': user.first_name,
        # 'Last Name': user.last_name
    } for user in users]
    df = pd.DataFrame(data)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Users')

    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="users.xlsx"'
    return response