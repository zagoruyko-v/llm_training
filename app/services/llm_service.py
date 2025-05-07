import json
import logging
from typing import Dict, List, Optional

import psutil
import requests
from pydantic import BaseModel

from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Message(BaseModel):
    role: str
    content: str


class LLMService:
    def __init__(self):
        self.base_url = f"http://{settings.OLLAMA_HOST}:{settings.OLLAMA_PORT}"
        self.default_model = settings.DEFAULT_MODEL
        self.default_temperature = settings.DEFAULT_TEMPERATURE
        self.default_max_tokens = settings.DEFAULT_MAX_TOKENS

    def _check_memory_availability(self, required_gb: float = None) -> bool:
        """Check if enough memory is available for the model."""
        required_gb = required_gb or settings.MODEL_MEMORY_REQUIREMENT
        available_gb = psutil.virtual_memory().available / (1024 * 1024 * 1024)
        return available_gb >= required_gb

    def get_training_context(self, user_id=None, session_id=None, conversation_id=None):
        """Retrieve past interactions marked for training."""
        params = {}
        if user_id:
            params["user"] = user_id
        if session_id:
            params["session_id"] = session_id
        if conversation_id:
            params["conversation"] = conversation_id
        try:
            admin_url = f"http://{settings.DJANGO_ADMIN_HOST}:{settings.DJANGO_ADMIN_PORT}/chat/llm-interactions/log/"
            # This should be replaced with a dedicated endpoint for filtering in production
            resp = requests.get(admin_url, params=params, timeout=5)
            if resp.status_code == 200:
                return [item for item in resp.json() if item.get("include_in_training")]
        except Exception:
            pass
        return []

    def generate_response(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
        context: Optional[List[Message]] = None,
        session_id: Optional[str] = None,
        user_id: Optional[int] = None,
        use_training_context: bool = False,
        conversation_id: Optional[int] = None,
    ) -> Dict:
        """
        Generate a response from the LLM using Ollama's API.
        """
        model = model or self.default_model
        temperature = temperature or self.default_temperature
        max_tokens = max_tokens or self.default_max_tokens

        if not self._check_memory_availability():
            logger.warning(
                f"Low memory available. Model {model} might not work properly."
            )

        try:
            # First, prepare the prompt with context if any
            full_prompt = ""
            if system_prompt:
                full_prompt += f"System: {system_prompt}\n\n"
            if context:
                for msg in context:
                    full_prompt += f"{msg.role.capitalize()}: {msg.content}\n"
            full_prompt += f"User: {prompt}"

            logger.info(f"Sending request to Ollama with prompt: {full_prompt}")

            # Optionally add training context
            if use_training_context:
                training_contexts = self.get_training_context(
                    user_id=user_id,
                    session_id=session_id,
                    conversation_id=conversation_id,
                )
                if training_contexts:
                    if not context:
                        context = []
                    for item in training_contexts:
                        context.append(Message(role="user", content=item["prompt"]))
                        context.append(
                            Message(role="assistant", content=item["response"])
                        )

            payload = {
                "model": model,
                "messages": [{"role": "user", "content": full_prompt}],
                "stream": False,
                "options": {"temperature": temperature, "num_predict": max_tokens},
            }
            logger.info(f"Request payload: {payload}")

            response = requests.post(
                f"{self.base_url}/api/chat", json=payload, timeout=30
            )
            response.raise_for_status()

            # Get the raw response text
            raw_text = response.text
            logger.debug(f"Raw response text: {raw_text}")

            # Process each line as a separate JSON object
            full_response = ""
            last_response = None

            try:
                # Try to parse the entire response as a single JSON object first
                result = json.loads(raw_text)
                if result.get("message", {}).get("content"):
                    full_response = result["message"]["content"]
                    last_response = result
            except json.JSONDecodeError:
                # If that fails, try to parse line by line
                for line in raw_text.split("\n"):
                    if not line.strip():
                        continue

                    try:
                        chunk = json.loads(line)
                        if chunk.get("message", {}).get("content"):
                            full_response += chunk["message"]["content"]
                        if chunk.get("done"):
                            last_response = chunk
                    except json.JSONDecodeError as e:
                        logger.error(f"Error decoding JSON: {e}, line: {line}")
                        continue

            # Format the response to match our expected structure
            formatted_response = {
                "message": {
                    "content": full_response
                    or "Sorry, I couldn't generate a response.",
                    "role": "assistant",
                },
                "model": model,
                "usage": {
                    "prompt_tokens": (
                        last_response.get("prompt_eval_count", 0)
                        if last_response
                        else 0
                    ),
                    "completion_tokens": (
                        last_response.get("eval_count", 0) if last_response else 0
                    ),
                    "total_tokens": (
                        (
                            last_response.get("prompt_eval_count", 0)
                            + last_response.get("eval_count", 0)
                        )
                        if last_response
                        else 0
                    ),
                },
            }
            logger.info(f"Formatted response: {formatted_response}")

            # Log interaction to Django admin
            try:
                admin_url = f"http://{settings.DJANGO_ADMIN_HOST}:{settings.DJANGO_ADMIN_PORT}/chat/llm-interactions/log/"
                llm_data = {
                    "prompt": prompt,
                    "response": formatted_response["message"]["content"],
                    "model_name": model,
                    "temperature": temperature,
                    "top_p": None,
                    "frequency_penalty": None,
                    "presence_penalty": None,
                    "context": [msg.dict() for msg in context] if context else None,
                    "retrieved_documents": None,
                    "streamed": False,
                    "session_id": session_id,
                    "user": user_id,
                }
                requests.post(admin_url, json=llm_data, timeout=5)
            except Exception as log_exc:
                logger.error(f"Failed to log LLM interaction to Django: {log_exc}")

            return formatted_response
        except (requests.RequestException, json.JSONDecodeError) as e:
            error_msg = f"Error communicating with Ollama: {str(e)}"
            if "model requires more system memory" in str(e):
                error_msg += "\nTry using a smaller model like 'mistral:7b-instruct-q4'"
            logger.error(error_msg)
            raise Exception(error_msg)

    def list_models(self) -> List[str]:
        """
        List all available models in Ollama.
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            return [model["name"] for model in response.json().get("models", [])]
        except requests.exceptions.RequestException as e:
            logger.error(f"Error listing models: {str(e)}")
            raise Exception(f"Error listing models: {str(e)}")

    def pull_model(self, model_name: str) -> Dict:
        """
        Pull a model from Ollama's model library.
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/pull", json={"name": model_name}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error pulling model: {str(e)}")
            raise Exception(f"Error pulling model: {str(e)}")

    def evaluate_response(
        self, prompt: str, response: str, criteria: Optional[Dict] = None
    ) -> Dict:
        """
        Evaluate an LLM response using another model instance.
        """
        default_criteria = {
            "relevance": "Is the response relevant to the prompt?",
            "accuracy": "Is the information accurate?",
            "completeness": "Is the response complete?",
            "clarity": "Is the response clear and well-structured?",
        }

        eval_criteria = criteria or default_criteria
        eval_prompt = f"""
        Please evaluate the following AI response to a prompt.
        Rate each criterion from 1-10 and provide a brief explanation.

        Prompt: {prompt}
        Response: {response}

        Criteria to evaluate:
        {eval_criteria}

        Format your response as JSON with 'scores' and 'explanations' keys.
        """

        try:
            eval_result = self.generate_response(
                prompt=eval_prompt,
                system_prompt="You are an expert AI evaluator. Be objective and critical.",
                temperature=0.3,  # Lower temperature for more consistent evaluation
            )
            return eval_result
        except Exception as e:
            logger.error(f"Error during evaluation: {str(e)}")
            raise Exception(f"Error during evaluation: {str(e)}")
