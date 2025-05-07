from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Conversation
from .serializers import LLMInteractionSerializer

# Create your views here.


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint."""
    return JsonResponse({"status": "healthy", "service": "django-admin"})


@api_view(["POST"])
@permission_classes([AllowAny])
def create_superuser(request):
    """Create a superuser if none exists."""
    if User.objects.filter(is_superuser=True).exists():
        return Response(
            {"message": "Superuser already exists"}, status=status.HTTP_200_OK
        )

    try:
        User.objects.create_superuser("admin", "admin@example.com", "admin123")
        return Response(
            {"message": "Superuser created successfully"},
            status=status.HTTP_201_CREATED,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([AllowAny])
def create_conversation(request):
    """Create a new conversation."""
    try:
        user = None
        user_id = request.data.get("user_id")
        if user_id:
            from django.contrib.auth import get_user_model

            User = get_user_model()
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                user = None
        if not user:
            # fallback to anonymous or first user
            user = User.objects.first()
        title = request.data.get("title", "")
        session_id = request.data.get("session_id")
        conversation = Conversation.objects.create(
            user=user,
            title=title or (f"Session {session_id}" if session_id else "Untitled"),
        )
        return Response(
            {
                "id": conversation.id,
                "title": conversation.title,
                "created_at": conversation.created_at,
            },
            status=status.HTTP_201_CREATED,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def list_conversations(request):
    """List all conversations for the current user."""
    conversations = Conversation.objects.filter(user=request.user)
    return Response(
        [
            {
                "id": conv.id,
                "title": conv.title,
                "created_at": conv.created_at,
                "updated_at": conv.updated_at,
            }
            for conv in conversations
        ]
    )


@api_view(["GET"])
def get_conversation(request, conversation_id):
    """Get a specific conversation."""
    try:
        conversation = Conversation.objects.get(id=conversation_id, user=request.user)
        return Response(
            {
                "id": conversation.id,
                "title": conversation.title,
                "created_at": conversation.created_at,
                "updated_at": conversation.updated_at,
            }
        )
    except Conversation.DoesNotExist:
        return Response(
            {"error": "Conversation not found"}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def log_llm_interaction(request):
    """Log an LLM interaction (prompt, response, metadata, etc)."""
    serializer = LLMInteractionSerializer(data=request.data)
    if serializer.is_valid():
        print("VALIDATED DATA:", serializer.validated_data)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    print("SERIALIZER ERRORS:", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
