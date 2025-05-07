from django.urls import path

from . import views

urlpatterns = [
    path("healthz/", views.health_check, name="health_check"),
    path("create-superuser/", views.create_superuser, name="create_superuser"),
    path("conversations/", views.list_conversations, name="list_conversations"),
    path(
        "conversations/create/", views.create_conversation, name="create_conversation"
    ),
    path(
        "conversations/<int:conversation_id>/",
        views.get_conversation,
        name="get_conversation",
    ),
    path(
        "llm-interactions/log/", views.log_llm_interaction, name="log_llm_interaction"
    ),
]
