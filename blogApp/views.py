from django.http import JsonResponse
from .models import Blog
from userApp.models import CustomUser
from rest_framework.decorators import api_view
from .serializers import BlogSerializer
import base64

@api_view(['POST'])
def create_blog(request):
    if request.method == 'POST':
        title = request.data.get('title')
        content = request.data.get('content')
        email = request.data.get('email')
        picture_data = request.data.get('picture')

        if not (title and content and email and picture_data):
            return JsonResponse({'error': 'Incomplete data provided'}, status=400)

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'User with the provided email does not exist'}, status=404)

        # Decode the base64-encoded picture data to binary
        picture_binary = base64.b64decode(picture_data)

        # Create a new Blog instance
        blog = Blog.objects.create(
            content=content,
            author=user,
            picture=picture_binary
        )

        return JsonResponse({'message': 'Blog saved successfully'}, status=201)

    


@api_view(['GET'])
def list_blogs(request):
    if request.method == 'GET':
        blogs = Blog.objects.all()
        serializer = BlogSerializer(blogs, many=True)
        return JsonResponse(serializer.data, safe=False)


@api_view(['PUT'])
def update_blog(request, pk):
    try:
        blog = Blog.objects.get(pk=pk)
    except Blog.DoesNotExist:
        return JsonResponse({'error': 'Blog does not exist'}, status=404)

    if request.method == 'PUT':
        title = request.data.get('title')
        content = request.data.get('content')
        email = request.data.get('email')
        picture_data = request.data.get('picture')

        # Update the blog fields if the data is provided
        if title:
            blog.title = title
        if content:
            blog.content = content
        if email:
            # Assuming author is updated based on email
            try:
                user = CustomUser.objects.get(email=email)
                blog.author = user
            except CustomUser.DoesNotExist:
                return JsonResponse({'error': 'User with the provided email does not exist'}, status=404)
        if picture_data:
            # Decode the base64-encoded picture data
            picture_binary = base64.b64decode(picture_data)
            blog.picture = picture_binary

        blog.save()
        return JsonResponse({'message': 'Blog updated successfully'})



@api_view(['DELETE'])
def delete_blog(request, pk):
    try:
        blog = Blog.objects.get(pk=pk)
    except Blog.DoesNotExist:
        return JsonResponse({'error': 'Blog does not exist'}, status=404)

    if request.method == 'DELETE':
        blog.delete()
        return JsonResponse({'message': 'Blog deleted successfully'}, status=204)


@api_view(['GET'])
def search_blogs_by_user(request, email):
    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'User with the provided email does not exist'}, status=404)

    if request.method == 'GET':
        blogs = Blog.objects.filter(author=user)
        blog_data = []

        for blog in blogs:
            blog_dict = {
                'id': blog.id,
                'content': blog.content,
                'author': blog.author.id,
                'created_at': blog.created_at,
                'picture': base64.b64encode(blog.picture).decode('utf-8') if blog.picture else None
            }
            blog_data.append(blog_dict)

        return JsonResponse(blog_data, safe=False)