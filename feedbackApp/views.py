from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Feedback
from .serializers import FeedbackSerializer
from userApp.models import CustomUser
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
def create_feedback(request):
    logger.info(f"Received request data: {request.data}")

    email = request.data.get('email')
    if not email:
        # If email field is not provided, try 'user' field
        email = request.data.get('user')

    if not email:
        logger.error("Email not provided in the request data.")
        return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)
    
    logger.info(f"Searching for user with email: {email}")
    
    try:
        user = CustomUser.objects.get(email=email)
        logger.info(f"Found user: {user.username}")

        data = {
            'user': user.id,  # Include the user's ID
            'request': request.data.get('request'),
            'feedback': request.data.get('feedback')
        }

        serializer = FeedbackSerializer(data=data)

        if serializer.is_valid():
            logger.info("Serializer is valid. Attempting to save feedback.")
            feedback = serializer.save()  # Save feedback
            logger.info(f"Feedback saved for user_id: {user.id}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except CustomUser.DoesNotExist:
        logger.error(f"User with email {email} does not exist.")
        return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception("Unexpected error occurred:")
        return Response({'error': 'Unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def list_feedbacks(request):
    """
    Retrieve all feedbacks available.
    """
    feedbacks = Feedback.objects.all()
    serializer = FeedbackSerializer(feedbacks, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
def update_feedback(request, pk):
    """
    Update an existing feedback by ID.
    """
    try:
        feedback = Feedback.objects.get(pk=pk)
    except Feedback.DoesNotExist:
        return Response({'error': 'Feedback does not exist.'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = FeedbackSerializer(feedback, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_feedback(request, pk):
    """
    Delete a feedback by ID.
    """
    try:
        feedback = Feedback.objects.get(pk=pk)
    except Feedback.DoesNotExist:
        return Response({'error': 'Feedback does not exist.'}, status=status.HTTP_404_NOT_FOUND)
    
    feedback.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def search_feedback_by_content(request):
    """
    Search feedbacks by content.
    """
    query_param = request.query_params.get('query', '')
    feedbacks = Feedback.objects.filter(feedback__icontains=query_param)
    serializer = FeedbackSerializer(feedbacks, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def search_feedback_by_request(request):
    """
    Search feedbacks by request content.
    """
    query_param = request.query_params.get('query', '')
    feedbacks = Feedback.objects.filter(request__icontains=query_param)
    serializer = FeedbackSerializer(feedbacks, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def search_feedback_by_email(request):
    """
    Search feedbacks by user email.
    """
    query_param = request.query_params.get('query', '')
    feedbacks = Feedback.objects.filter(user__email__icontains=query_param)
    serializer = FeedbackSerializer(feedbacks, many=True)
    return Response(serializer.data)



@api_view(['GET'])
def get_feedback_by_id(request, pk):
    """
    Retrieve a feedback by its ID.
    """
    try:
        feedback = Feedback.objects.get(pk=pk)
        serializer = FeedbackSerializer(feedback)
        return Response(serializer.data)
    except Feedback.DoesNotExist:
        return Response({'error': 'Feedback does not exist.'}, status=status.HTTP_404_NOT_FOUND)





from django.core.mail import send_mail
from django.conf import settings

@api_view(['POST'])
def respond_feedback(request, pk):
    """
    Respond to a feedback by ID, sending an email to the user.
    """
    try:
        feedback = Feedback.objects.get(pk=pk)
    except Feedback.DoesNotExist:
        return Response({'error': 'Feedback does not exist.'}, status=status.HTTP_404_NOT_FOUND)

    email = feedback.user.email
    username = feedback.user.username
    response_text = request.data.get('response')

    if not response_text:
        return Response({'error': 'Response text is required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Email content
    subject = "Response to Your Feedback"
    message = f"""
    Hello {username},

    Thanks for reaching us.

    {response_text}

    Thanks for working with us.
    """
    from_email = settings.DEFAULT_FROM_EMAIL

    try:
        send_mail(subject, message, from_email, [email])
        return Response({'message': 'Response sent successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.exception("Error sending email:")
        return Response({'error': 'Error sending email.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




'''
    Reports on feedbacks
'''

import io
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph
from rest_framework.decorators import api_view
from .models import Feedback

@api_view(['GET'])
def download_feedbacks_pdf(request):
    feedbacks = Feedback.objects.all()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    data = [['User', 'Request', 'Feedback']]
    style = getSampleStyleSheet()
    request_style = ParagraphStyle('request_style', fontSize=12, leading=14)
    feedback_style = ParagraphStyle('feedback_style', fontSize=12, leading=14)

    for feedback in feedbacks:
        user_email = feedback.user.email
        request_text = ' '.join([feedback.request[i:i+10] for i in range(0, len(feedback.request), 10)])
        feedback_text = ' '.join([feedback.feedback[i:i+20] for i in range(0, len(feedback.feedback), 20)])
        request_paragraph = Paragraph(request_text, request_style)
        feedback_paragraph = Paragraph(feedback_text, feedback_style)
        data.append([user_email, request_paragraph, feedback_paragraph])

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
    response['Content-Disposition'] = 'attachment; filename="feedbacks.pdf"'
    return response



import io
import pandas as pd
from django.http import HttpResponse
from rest_framework.decorators import api_view
from .models import Feedback

@api_view(['GET'])
def download_feedbacks_excel(request):
    feedbacks = Feedback.objects.all()
    data = []

    for feedback in feedbacks:
        user_email = feedback.user.email
        request_text = '\n'.join([feedback.request[i:i+10] for i in range(0, len(feedback.request), 10)])
        feedback_text = '\n'.join([feedback.feedback[i:i+20] for i in range(0, len(feedback.feedback), 20)])
        created_at = feedback.created_at.astimezone(tz=None).replace(tzinfo=None)
        data.append({
            "User": user_email,
            "Request": request_text,
            "Feedback": feedback_text,
            "Created At": created_at
        })

    df = pd.DataFrame(data)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Feedbacks')

    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="feedbacks.xlsx"'
    return response

