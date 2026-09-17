"""
LLM Service - VW Group LLMaaS integration for AI-generated agent narratives.

Design: the deterministic AnalysisEngine/AgentOrchestrator methods remain the
single source of truth for facts (counts, IDs, scores, traceability). This
service only turns already-verified findings/evidence into a natural-language
narrative — it never invents facts, and every prompt instructs the model to
use only the data provided. If no provider is reachable, callers fall back
to their existing templated text so the app never breaks.

Provider selection (checked in this order, first match wins):
  1. VW Group LLMaaS (OpenAI SDK, via IDP client-credentials OAuth token)
     - LLMAAS_CLIENT_ID / LLMAAS_CLIENT_SECRET - Cloud IDP app credentials
     - LLMAAS_API_KEY   - LLMaaS gateway key (sent as X-LLM-API-CLIENT-ID header)
     - LLMAAS_BASE_URL  (default: https://llmapi.ai.vwgroup.com)
     - LLMAAS_MODEL     (default: gpt-4o)
  2. Local Ollama (no key needed, used only as a fallback)
     - OLLAMA_HOST  (default: http://localhost:11434)
     - OLLAMA_MODEL (default: llama3.2:3b)

All credentials are read from environment variables (backend/.env, which is
gitignored) - never hardcode secrets in source files.
"""

import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger("llm_service")

# --- VW Group LLMaaS configuration ---
LLMAAS_IDP_URL = os.environ.get(
    "LLMAAS_IDP_URL",
    "https://idp.cloud.vwgroup.com/auth/realms/kums-mfa/protocol/openid-connect/token",
)
LLMAAS_CLIENT_ID = os.environ.get("LLMAAS_CLIENT_ID", "").strip()
LLMAAS_CLIENT_SECRET = os.environ.get("LLMAAS_CLIENT_SECRET", "").strip()
LLMAAS_API_KEY = os.environ.get("LLMAAS_API_KEY", "").strip()
LLMAAS_BASE_URL = os.environ.get("LLMAAS_BASE_URL", "https://llmapi.ai.vwgroup.com").rstrip("/")
LLMAAS_MODEL = os.environ.get("LLMAAS_MODEL", "gpt-4o")
LLMAAS_EMBEDDING_MODEL = os.environ.get("LLMAAS_EMBEDDING_MODEL", "text-embedding-3-small")

# --- Local Ollama (fallback only) ---
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:3b")

REQUEST_TIMEOUT_SECONDS = 30

# In-memory cache for the IDP access token (client-credentials tokens are
# short-lived; refetch a little before they actually expire)
_token_cache: Dict[str, Any] = {"access_token": None, "expires_at": 0.0}


def is_llmaas_configured() -> bool:
    """Whether VW LLMaaS credentials have been supplied."""
    return bool(LLMAAS_CLIENT_ID and LLMAAS_CLIENT_SECRET and LLMAAS_API_KEY)


def is_ollama_available() -> bool:
    """Quick check whether the local Ollama server is reachable."""
    try:
        resp = httpx.get(f"{OLLAMA_HOST}/api/tags", timeout=2)
        return resp.status_code == 200
    except Exception:
        return False


def is_available() -> bool:
    """Whether ANY narrative provider (LLMaaS or local) is currently usable."""
    return is_llmaas_configured() or is_ollama_available()


def _get_idp_token() -> Optional[str]:
    """Fetch (and cache) an access token via the Cloud IDP client-credentials flow."""
    now = time.time()
    if _token_cache["access_token"] and now < _token_cache["expires_at"] - 30:
        return _token_cache["access_token"]

    try:
        resp = httpx.post(
            LLMAAS_IDP_URL,
            data={
                "client_id": LLMAAS_CLIENT_ID,
                "client_secret": LLMAAS_CLIENT_SECRET,
                "grant_type": "client_credentials",
            },
            timeout=15,
        )
        resp.raise_for_status()
        payload = resp.json()
        token = payload["access_token"]
        _token_cache["access_token"] = token
        _token_cache["expires_at"] = now + float(payload.get("expires_in", 300))
        return token
    except Exception as exc:
        logger.warning("LLMaaS IDP token fetch failed: %s", exc)
        return None


def _get_llmaas_client():
    """Build an OpenAI SDK client pointed at the VW LLMaaS gateway, or None."""
    token = _get_idp_token()
    if not token:
        return None
    try:
        from openai import OpenAI
        return OpenAI(
            api_key=token,
            base_url=LLMAAS_BASE_URL,
            default_headers={"X-LLM-API-CLIENT-ID": f"Bearer {LLMAAS_API_KEY}"},
        )
    except Exception as exc:
        logger.warning("Failed to construct LLMaaS client: %s", exc)
        return None


def _build_prompt(agent_role: str, instructions: str, data: Dict[str, Any]) -> str:
    return (
        f"{instructions}\n\n"
        "Only reference facts present in the JSON data below. Do not invent IDs, "
        "numbers, or names that are not present. Keep the response concise (max 150 words), "
        "written in plain prose for a technical audience.\n\n"
        f"DATA:\n{json.dumps(data, default=str)[:8000]}"
    )


def _generate_via_llmaas(agent_role: str, instructions: str, data: Dict[str, Any]) -> Optional[str]:
    client = _get_llmaas_client()
    if client is None:
        return None

    system_prompt = (
        f"You are the {agent_role} agent inside LegacyIQ, an enterprise legacy "
        "modernization platform. You reason strictly over the JSON evidence given "
        "to you and never invent facts that are not present in it."
    )
    try:
        completion = client.chat.completions.create(
            model=LLMAAS_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": _build_prompt(agent_role, instructions, data)},
            ],
            temperature=0.3,
            stream=False,
        )
        content = completion.choices[0].message.content
        return content.strip() if content else None
    except Exception as exc:
        logger.warning("LLMaaS chat completion failed for agent=%s: %s", agent_role, exc)
        return None


def _generate_via_ollama(agent_role: str, instructions: str, data: Dict[str, Any]) -> Optional[str]:
    prompt = (
        f"You are the {agent_role} agent in an enterprise legacy modernization platform.\n"
        f"{_build_prompt(agent_role, instructions, data)}"
    )
    try:
        resp = httpx.post(
            f"{OLLAMA_HOST}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        resp.raise_for_status()
        return resp.json().get("response", "").strip() or None
    except Exception:
        return None


def generate_narrative(agent_role: str, instructions: str, data: Dict[str, Any]) -> Optional[str]:
    """
    Ask the configured LLM (VW LLMaaS if credentials are set, else local
    Ollama) to narrate over already-verified findings.

    Returns the generated text, or None if no provider is available or the
    call fails — callers must fall back to their existing templated text.
    """
    if is_llmaas_configured():
        result = _generate_via_llmaas(agent_role, instructions, data)
        if result:
            return result
        # LLMaaS configured but the call failed (transient error) - try local as a backstop
        return _generate_via_ollama(agent_role, instructions, data) if is_ollama_available() else None

    if is_ollama_available():
        return _generate_via_ollama(agent_role, instructions, data)

    return None


def _build_structured_prompt(instructions: str, data: Dict[str, Any], schema_hint: str, facts_char_limit: int) -> str:
    return (
        f"{instructions}\n\n"
        "The JSON object under FACTS below is the ONLY source of truth — every id, count, "
        "name, and number in your response must come from it exactly as given (never "
        "invent new ones). Keep your response as SHORT as possible: only include the fields "
        "the schema asks for, and keep any free-text field brief (one short sentence unless "
        "told otherwise) — brevity matters more than completeness here.\n\n"
        f"REQUIRED JSON SCHEMA:\n{schema_hint}\n\n"
        "Respond with ONLY a single valid JSON object matching that schema — no markdown "
        "fences, no commentary before or after it.\n\n"
        f"FACTS:\n{json.dumps(data, default=str)[:facts_char_limit]}"
    )


def _extract_json(text: str) -> Optional[Dict[str, Any]]:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        return json.loads(text[start:end + 1])
    except Exception:
        return None


def _generate_structured_via_llmaas(agent_role: str, instructions: str, data: Dict[str, Any], schema_hint: str, max_tokens: int, facts_char_limit: int) -> Optional[Dict[str, Any]]:
    client = _get_llmaas_client()
    if client is None:
        return None

    system_prompt = (
        f"You are the {agent_role} agent inside LegacyIQ, an enterprise legacy "
        "modernization platform. You produce the full UI-facing output as strict, "
        "CONCISE JSON, grounded only in the facts you are given."
    )
    try:
        completion = client.chat.completions.create(
            model=LLMAAS_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": _build_structured_prompt(instructions, data, schema_hint, facts_char_limit)},
            ],
            temperature=0.3,
            stream=False,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )
        content = completion.choices[0].message.content
        return _extract_json(content) if content else None
    except Exception as exc:
        logger.warning("LLMaaS structured completion failed for agent=%s: %s", agent_role, exc)
        return None


def _generate_structured_via_ollama(agent_role: str, instructions: str, data: Dict[str, Any], schema_hint: str, max_tokens: int, facts_char_limit: int) -> Optional[Dict[str, Any]]:
    prompt = (
        f"You are the {agent_role} agent in an enterprise legacy modernization platform.\n"
        f"{_build_structured_prompt(instructions, data, schema_hint, facts_char_limit)}"
    )
    try:
        resp = httpx.post(
            f"{OLLAMA_HOST}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False, "format": "json", "options": {"num_predict": max_tokens}},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        resp.raise_for_status()
        text = resp.json().get("response", "")
        return _extract_json(text) if text else None
    except Exception:
        return None


def generate_structured(agent_role: str, instructions: str, data: Dict[str, Any], schema_hint: str, max_tokens: int = 900, facts_char_limit: int = 20000) -> Optional[Dict[str, Any]]:
    """
    Ask the LLM to author the UI-facing output as a JSON object matching
    schema_hint, grounded strictly in `data`. Used so agent responses are
    genuinely AI-generated rather than Python f-string templates.

    Callers should prefer small, id-keyed "notes" schemas (e.g. a list of
    {"id": ..., "text": ...}) over asking the model to echo full records —
    output size is the dominant factor in response latency, so keeping the
    schema compact is what keeps this fast. `max_tokens` bounds the reply
    size (raise it only for prose-heavy schemas like document sections).

    Returns the parsed dict, or None if no provider is reachable or the
    response could not be parsed as valid JSON — callers must fall back to
    their deterministic template AND flag the response as non-AI-generated
    so the UI can tell the user clearly.
    """
    if is_llmaas_configured():
        result = _generate_structured_via_llmaas(agent_role, instructions, data, schema_hint, max_tokens, facts_char_limit)
        if result:
            return result
        return _generate_structured_via_ollama(agent_role, instructions, data, schema_hint, max_tokens, facts_char_limit) if is_ollama_available() else None

    if is_ollama_available():
        return _generate_structured_via_ollama(agent_role, instructions, data, schema_hint, max_tokens, facts_char_limit)

    return None


def embed_texts(texts: List[str]) -> Optional[List[List[float]]]:
    """
    Embed a batch of texts via VW LLMaaS's OpenAI-compatible embeddings
    endpoint (the "Retrieval" half of vector-embedding RAG). Returns a list
    of float vectors (same order as `texts`), or None if no embedding
    provider is reachable — callers must treat semantic search as
    unavailable in that case, never fabricate vectors.
    """
    if not texts:
        return []
    if is_llmaas_configured():
        client = _get_llmaas_client()
        if client is not None:
            try:
                resp = client.embeddings.create(model=LLMAAS_EMBEDDING_MODEL, input=texts)
                return [item.embedding for item in resp.data]
            except Exception as exc:
                logger.warning("LLMaaS embeddings failed: %s", exc)
                return None
    return None

