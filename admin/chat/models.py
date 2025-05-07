from django.contrib.auth.models import User
from django.db import models
from django.db.models import JSONField


class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.title or 'Untitled'} - {self.user.username}"


class LLMInteraction(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    conversation = models.ForeignKey(
        Conversation, null=True, blank=True, on_delete=models.SET_NULL
    )
    prompt = models.TextField()
    response = models.TextField()
    model_name = models.CharField(max_length=100)
    temperature = models.FloatField(default=0.7)
    top_p = models.FloatField(null=True, blank=True)
    frequency_penalty = models.FloatField(null=True, blank=True)
    presence_penalty = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    context = JSONField(null=True, blank=True)
    retrieved_documents = JSONField(null=True, blank=True)
    streamed = models.BooleanField(default=False)
    # Feedback fields for future
    rating = models.IntegerField(null=True, blank=True)
    thumbs_up = models.BooleanField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    session_id = models.CharField(max_length=255, null=True, blank=True)
    score = models.IntegerField(null=True, blank=True)
    feedback_comment = models.TextField(null=True, blank=True)
    include_in_training = models.BooleanField(default=False)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.model_name} | {self.prompt[:30]}... -> {self.response[:30]}..."
