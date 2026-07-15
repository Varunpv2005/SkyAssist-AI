import httpx
import pytest
from unittest.mock import AsyncMock, patch

from ai_engine.service import AIEngine, _fallback_analysis, _parse_ai_response


def test_parse_ai_response():
    raw = """Here is my analysis:
    {
      "root_cause": "Auth service down",
      "explanation": "The auth service is not responding.",
      "resolution_steps": ["Restart auth service", "Check logs"],
      "confidence_score": 0.87
    }"""
    result = _parse_ai_response(raw)
    assert result.root_cause == "Auth service down"
    assert len(result.resolution_steps) == 2
    assert result.confidence_score == 0.87
    assert result.source == "ollama"


def test_fallback_auth():
    result = _fallback_analysis(
        "Why did login fail?",
        "2026-06-15 ERROR Login failed for user admin",
        "High",
    )
    assert result.source == "fallback"
    assert "auth" in result.root_cause.lower() or "credential" in result.root_cause.lower()


def test_fallback_timeout():
    result = _fallback_analysis(
        "Why timeout?",
        "API timeout on /api/v1/proxy",
        "High",
    )
    assert "timeout" in result.root_cause.lower()


def test_build_prompt():
    prompt = AIEngine.build_prompt(
        question="Why did this error occur?",
        log_snippet="ERROR auth failure",
        incident_details="INC-1001 AUTH_FAILURE",
        severity="High",
    )
    assert "Why did this error occur?" in prompt
    assert "ERROR auth failure" in prompt
    assert "High" in prompt


@pytest.mark.asyncio
async def test_analyze_uses_fallback_when_ollama_down():
    with patch.object(AIEngine, "ask_ollama", side_effect=httpx.ConnectError("connection refused")):
        result = await AIEngine.analyze(
            question="Why did login fail?",
            log_snippet="ERROR Login failed",
            severity="High",
        )
    assert result.source == "fallback"
    assert result.root_cause
    assert len(result.resolution_steps) >= 3


@pytest.mark.asyncio
async def test_analyze_uses_ollama_when_available():
    mock_result = _parse_ai_response(
        '{"root_cause":"Test","explanation":"Test exp",'
        '"resolution_steps":["Step 1"],"confidence_score":0.9}'
    )
    with patch.object(AIEngine, "ask_ollama", return_value=mock_result):
        result = await AIEngine.analyze(question="Test question")
    assert result.source == "ollama"
    assert result.confidence_score == 0.9
