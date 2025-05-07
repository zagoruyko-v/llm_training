from django.contrib.auth.models import User
from rest_framework import serializers

from .models import LLMInteraction


class LLMInteractionSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = LLMInteraction
        fields = "__all__"
        read_only_fields = (
            "id",
            "timestamp",
            "conversation",
        )
