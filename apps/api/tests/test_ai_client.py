import pytest
from pydantic import BaseModel

from app.ai.client import AIClient


class MockResponseModel(BaseModel):
    result: str


def test_ai_client_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(
        RuntimeError,
        match="OPENAI_API_KEY environment variable is not set",
    ):
        AIClient()


def test_ai_client_initializes_with_api_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    client = AIClient()

    assert client.client is not None


@pytest.mark.asyncio
async def test_ai_client_returns_structured_response(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    client = AIClient()

    expected = MockResponseModel(result="success")

    class MockResponse:
        output_parsed = expected

    async def mock_parse(**kwargs):
        assert kwargs["model"] == "gpt-5.6-luna"
        assert kwargs["input"] == "test prompt"
        assert kwargs["text_format"] is MockResponseModel

        return MockResponse()

    monkeypatch.setattr(
        client.client.responses,
        "parse",
        mock_parse,
    )

    result = await client.analyze(
        prompt="test prompt",
        response_model=MockResponseModel,
    )

    assert result == expected


@pytest.mark.asyncio
async def test_ai_client_raises_when_no_structured_response(
    monkeypatch,
):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    client = AIClient()

    class MockResponse:
        output_parsed = None

    async def mock_parse(**kwargs):
        return MockResponse()

    monkeypatch.setattr(
        client.client.responses,
        "parse",
        mock_parse,
    )

    with pytest.raises(
        RuntimeError,
        match="OpenAI returned no structured response",
    ):
        await client.analyze(
            prompt="test prompt",
            response_model=MockResponseModel,
        )