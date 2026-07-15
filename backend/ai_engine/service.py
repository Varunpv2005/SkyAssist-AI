import json
import logging
import re
from dataclasses import dataclass

import httpx

from ai_engine.prompt_templates.remediate import REMEDIATE_SYSTEM, REMEDIATE_USER
from ai_engine.prompt_templates.troubleshoot import (
    TROUBLESHOOT_SYSTEM,
    TROUBLESHOOT_USER,
)
from database.config import settings

logger = logging.getLogger("skyassist")


@dataclass
class RemediationResult:
    recommended_fixes: list[str]
    troubleshooting_steps: list[str]
    confidence_score: float
    source: str


@dataclass
class AIAnalysisResult:
    root_cause: str
    explanation: str
    resolution_steps: list[str]
    confidence_score: float
    source: str


FALLBACK_RESPONSES = {
    "auth": AIAnalysisResult(
        root_cause="Authentication failure due to invalid credentials or account lockout",
        explanation=(
            "The log indicates a failed authentication attempt. This commonly occurs when "
            "credentials are incorrect, the account is locked, or the auth service is degraded."
        ),
        resolution_steps=[
            "Verify the user's credentials and account status",
            "Check authentication service health and logs",
            "Review recent failed login attempts for brute-force patterns",
            "Confirm SSO/LDAP integration is functioning correctly",
        ],
        confidence_score=0.78,
        source="fallback",
    ),
    "timeout": AIAnalysisResult(
        root_cause="API request exceeded configured timeout threshold",
        explanation=(
            "The upstream service did not respond within the allowed time window. "
            "This may indicate backend overload, network latency, or misconfigured timeouts."
        ),
        resolution_steps=[
            "Check upstream service health and response times",
            "Review and adjust API gateway timeout settings",
            "Inspect backend resource utilization (CPU, memory)",
            "Test connectivity between gateway and backend services",
        ],
        confidence_score=0.75,
        source="fallback",
    ),
    "database": AIAnalysisResult(
        root_cause="Database connectivity failure or connection pool exhaustion",
        explanation=(
            "The application cannot establish or maintain database connections. "
            "This is often caused by DB server downtime or exhausted connection pools."
        ),
        resolution_steps=[
            "Verify database server is running and accepting connections",
            "Check connection pool configuration and active connections",
            "Review database server logs for errors",
            "Validate network connectivity and firewall rules to DB port",
        ],
        confidence_score=0.82,
        source="fallback",
    ),
    "default": AIAnalysisResult(
        root_cause="Security event detected requiring further investigation",
        explanation=(
            "Based on the provided log snippet and incident context, a security-related "
            "issue has been identified. Additional log correlation may be needed."
        ),
        resolution_steps=[
            "Review the full log file for related events",
            "Check service health dashboards",
            "Correlate with recent configuration changes",
            "Escalate to senior engineer if issue persists",
        ],
        confidence_score=0.65,
        source="fallback",
    ),
}


def _parse_ai_response(raw: str) -> AIAnalysisResult:
    json_match = re.search(r"\{[\s\S]*\}", raw)
    if not json_match:
        raise ValueError("No JSON found in AI response")

    data = json.loads(json_match.group())
    steps = data.get("resolution_steps", [])
    if isinstance(steps, str):
        steps = [steps]

    return AIAnalysisResult(
        root_cause=data.get("root_cause", "Unable to determine root cause"),
        explanation=data.get("explanation", "Analysis completed."),
        resolution_steps=steps,
        confidence_score=min(float(data.get("confidence_score", 0.7)), 0.99),
        source="ollama",
    )


def _fallback_analysis(
    question: str, log_snippet: str, severity: str
) -> AIAnalysisResult:
    combined = f"{question} {log_snippet}".lower()
    if any(k in combined for k in ("auth", "login", "credential", "unauthorized")):
        return FALLBACK_RESPONSES["auth"]
    if any(k in combined for k in ("timeout", "timed out", "504", "slow")):
        return FALLBACK_RESPONSES["timeout"]
    if any(k in combined for k in ("database", "connection pool", "sql", "db ")):
        return FALLBACK_RESPONSES["database"]
    return FALLBACK_RESPONSES["default"]


class AIEngine:
    @staticmethod
    def build_prompt(
        question: str,
        log_snippet: str = "",
        incident_details: str = "None",
        severity: str = "Unknown",
    ) -> str:
        return TROUBLESHOOT_USER.format(
            question=question,
            severity=severity,
            incident_details=incident_details,
            log_snippet=log_snippet or "No log snippet provided",
        )

    @staticmethod
    async def ask_ollama(prompt: str) -> AIAnalysisResult:
        url = f"{settings.OLLAMA_BASE_URL}/api/chat"

        logger.info("Calling Ollama at %s", url)
        logger.info("Using model: %s", settings.OLLAMA_MODEL)

        payload = {
            "model": settings.OLLAMA_MODEL,
            "messages": [
                {"role": "system", "content": TROUBLESHOOT_SYSTEM},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 512,
            },
        }

        async with httpx.AsyncClient(timeout=settings.OLLAMA_TIMEOUT) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()

            logger.info("Ollama raw response: %s", response.text)

            data = response.json()
            content = data.get("message", {}).get("content", "")

            logger.info("Ollama extracted content: %s", content)

            return _parse_ai_response(content)

    @staticmethod
    async def analyze(
        question: str,
        log_snippet: str = "",
        incident_details: str = "None",
        severity: str = "Unknown",
    ) -> AIAnalysisResult:
        prompt = AIEngine.build_prompt(
            question, log_snippet, incident_details, severity
        )
        try:
            return await AIEngine.ask_ollama(prompt)
        except (httpx.HTTPError, ValueError, json.JSONDecodeError) as exc:
            logger.exception("Ollama analysis failed")
            return _fallback_analysis(question, log_snippet, severity)

    @staticmethod
    async def check_ollama_health() -> dict:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
                response.raise_for_status()
                models = [m.get("name", "") for m in response.json().get("models", [])]
                return {
                    "available": True,
                    "model": settings.OLLAMA_MODEL,
                    "models": models,
                }
        except httpx.HTTPError:
            return {
                "available": False,
                "model": settings.OLLAMA_MODEL,
                "models": [],
                "message": "Ollama not reachable — fallback mode active",
            }

    @staticmethod
    def _parse_remediation(raw: str) -> RemediationResult:
        json_match = re.search(r"\{[\s\S]*\}", raw)
        if not json_match:
            raise ValueError("No JSON in remediation response")
        data = json.loads(json_match.group())
        fixes = data.get("recommended_fixes", [])
        steps = data.get("troubleshooting_steps", [])
        if isinstance(fixes, str):
            fixes = [fixes]
        if isinstance(steps, str):
            steps = [steps]
        return RemediationResult(
            recommended_fixes=fixes,
            troubleshooting_steps=steps,
            confidence_score=min(float(data.get("confidence_score", 0.75)), 0.99),
            source="ollama",
        )

    @staticmethod
    def _fallback_remediation(
        incident_details: str, severity: str
    ) -> RemediationResult:
        analysis = _fallback_analysis(incident_details, incident_details, severity)
        return RemediationResult(
            recommended_fixes=[analysis.root_cause],
            troubleshooting_steps=analysis.resolution_steps,
            confidence_score=analysis.confidence_score,
            source="fallback",
        )

    @staticmethod
    async def generate_remediation(
        incident_details: str,
        severity: str = "Unknown",
        log_snippet: str = "",
        knowledge_context: str = "None",
    ) -> RemediationResult:
        prompt = REMEDIATE_USER.format(
            incident_details=incident_details,
            severity=severity,
            log_snippet=log_snippet or "No log snippet",
            knowledge_context=knowledge_context,
        )
        try:
            url = f"{settings.OLLAMA_BASE_URL}/api/chat"
            payload = {
                "model": settings.OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": REMEDIATE_SYSTEM},
                    {"role": "user", "content": prompt},
                ],
                "stream": False,
                "options": {"temperature": 0.3, "num_predict": 512},
            }
            async with httpx.AsyncClient(timeout=settings.OLLAMA_TIMEOUT) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                content = response.json().get("message", {}).get("content", "")
                return AIEngine._parse_remediation(content)
        except (httpx.HTTPError, ValueError, json.JSONDecodeError) as exc:
            logger.exception("Ollama remediation failed")
            return AIEngine._fallback_remediation(incident_details, severity)
