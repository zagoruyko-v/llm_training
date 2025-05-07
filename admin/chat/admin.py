from django.contrib import admin

from .models import Conversation, LLMInteraction


@admin.register(Conversation)
class LLMConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "created_at", "updated_at")
    list_filter = ("user", "created_at")
    search_fields = ("title", "user__username")
    date_hierarchy = "created_at"
    readonly_fields = ("id", "user", "created_at", "updated_at", "title")

    def get_model_perms(self, request):
        perms = super().get_model_perms(request)
        perms["add"] = perms["change"] = perms["delete"] = perms["view"] = True
        return perms

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs

    def get_verbose_name(self):
        return "LLM Conversation"

    def get_verbose_name_plural(self):
        return "LLM Conversations"


@admin.register(LLMInteraction)
class LLMInteractionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "conversation",
        "timestamp",
        "model_name",
        "temperature",
        "top_p",
        "frequency_penalty",
        "presence_penalty",
        "streamed",
        "prompt_preview",
        "response_preview",
        "score",
        "feedback_comment",
        "include_in_training",
    )
    list_filter = (
        "model_name",
        "temperature",
        "top_p",
        "frequency_penalty",
        "presence_penalty",
        "streamed",
        "timestamp",
        "user",
        "conversation",
        "score",
        "include_in_training",
    )
    search_fields = (
        "prompt",
        "response",
        "model_name",
        "user__username",
        "conversation__title",
        "comment",
        "feedback_comment",
    )
    date_hierarchy = "timestamp"
    readonly_fields = (
        "id",
        "user",
        "conversation",
        "timestamp",
        "model_name",
        "temperature",
        "top_p",
        "frequency_penalty",
        "presence_penalty",
        "streamed",
        "prompt",
        "response",
        "context",
        "retrieved_documents",
        "session_id",
        "comment",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "user",
                    "conversation",
                    "timestamp",
                    "model_name",
                    "temperature",
                    "top_p",
                    "frequency_penalty",
                    "presence_penalty",
                    "streamed",
                    "prompt",
                    "response",
                    "context",
                    "retrieved_documents",
                    "session_id",
                    "comment",
                )
            },
        ),
        (
            "Evaluation",
            {"fields": ("score", "feedback_comment", "include_in_training")},
        ),
    )

    def prompt_preview(self, obj):
        return obj.prompt[:50] + "..." if len(obj.prompt) > 50 else obj.prompt

    prompt_preview.short_description = "Prompt"

    def response_preview(self, obj):
        return obj.response[:50] + "..." if len(obj.response) > 50 else obj.response

    response_preview.short_description = "Response"
