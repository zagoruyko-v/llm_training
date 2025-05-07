from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import connection
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import Conversation, LLMInteraction

# Create your tests here.


class MigrationTest(TestCase):
    def test_migrations_apply_cleanly(self):
        # This will apply all migrations and fail if any are broken
        try:
            call_command("migrate", verbosity=0, interactive=False)
        except Exception as e:
            self.fail(f"Migrations failed: {e}")
        # Check that all expected tables exist
        with connection.cursor() as cursor:
            cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname='public';")
            tables = [row[0] for row in cursor.fetchall()]
            self.assertIn("chat_conversation", tables)
            self.assertIn("chat_llminteraction", tables)


class ChatViewsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.force_authenticate(user=self.user)

    def test_healthz(self):
        url = reverse("health_check")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("status", resp.json())

    def test_create_superuser(self):
        url = reverse("create_superuser")
        resp = self.client.post(url)
        self.assertIn(resp.status_code, [200, 201])

    def test_create_and_list_conversation(self):
        create_url = reverse("create_conversation")
        resp = self.client.post(
            create_url, {"title": "Test Conversation", "user_id": self.user.id}
        )
        self.assertEqual(resp.status_code, 201)
        conv_id = resp.json()["id"]
        list_url = reverse("list_conversations")
        resp2 = self.client.get(list_url)
        self.assertEqual(resp2.status_code, 200)
        self.assertTrue(any(c["id"] == conv_id for c in resp2.json()))

    def test_get_conversation(self):
        conv = Conversation.objects.create(user=self.user, title="Test")
        url = reverse("get_conversation", args=[conv.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["id"], conv.id)

    def test_llm_interaction_logging(self):
        url = reverse("log_llm_interaction")
        data = {
            "prompt": "Hello, world!",
            "response": "Hi there!",
            "model_name": "mistral",
            "temperature": 0.7,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "context": None,
            "retrieved_documents": None,
            "streamed": False,
            "session_id": "test-session-123",
        }
        response = self.client.post(url, data, format="json")
        if response.status_code != 201:
            print("RESPONSE:", response.status_code, response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(LLMInteraction.objects.count(), 1)
        interaction = LLMInteraction.objects.first()
        print("INTERACTION:", interaction)
        self.assertEqual(interaction.prompt, data["prompt"])
        self.assertEqual(interaction.response, data["response"])
        self.assertEqual(interaction.session_id, data["session_id"])
