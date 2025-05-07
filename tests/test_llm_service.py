import pytest

from app.services.llm_service import LLMService, Message


@pytest.fixture
def llm_service():
    return LLMService()


def test_generate_response(llm_service):
    # Test basic response generation
    result = llm_service.generate_response(prompt="What is 2+2?", temperature=0.1)
    assert "response" in result
    assert "model" in result


def test_list_models(llm_service):
    # Test listing available models
    models = llm_service.list_models()
    assert isinstance(models, list)


def test_generate_with_context(llm_service):
    # Test response generation with context
    context = [
        Message(role="system", content="You are a helpful assistant."),
        Message(role="user", content="What is 2+2?"),
        Message(role="assistant", content="4"),
        Message(role="user", content="What is 3+3?"),
    ]

    result = llm_service.generate_response(
        prompt="What is 4+4?", context=context, temperature=0.1
    )
    assert "response" in result
    assert "model" in result
