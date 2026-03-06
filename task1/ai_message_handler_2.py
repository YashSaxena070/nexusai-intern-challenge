"""
Task 1: AI Message Handler
--------------------------
"""

import asyncio
import os
import re
from dataclasses import dataclass
from typing import Optional

import aiohttp
from dotenv import load_dotenv

# ──────────────────────────────────────────────
# Load environment variables from .env file
# Add GROQ_API_KEY=your_key_here to .env
# ──────────────────────────────────────────────
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL   = "llama-3.3-70b-versatile"      # fast, capable Groq-hosted model
GROQ_URL     = "https://api.groq.com/openai/v1/chat/completions"


# ══════════════════════════════════════════════
# STEP 1 — Define the response dataclass
# ══════════════════════════════════════════════
@dataclass
class MessageResponse:
    """
    Structured object returned by handle_message().

    Fields
    ------
    response_text             : Raw answer from the LLM (no channel formatting).
    confidence                : Float 0.0–1.0 — how confident the agent is.
    suggested_action          : Short next-step hint, e.g. "escalate_to_human".
    channel_formatted_response: The version the customer actually receives,
                                shaped to the channel's constraints.
    error                     : Populated only when something goes wrong; None on success.
    """
    response_text: str = ""
    confidence: float = 0.0
    suggested_action: str = ""
    channel_formatted_response: str = ""
    error: Optional[str] = None


# ══════════════════════════════════════════════
# STEP 2 — The async handler function
# ══════════════════════════════════════════════
async def handle_message(
    customer_message: str,
    customer_id: str,
    channel: str,           # "voice" | "chat" | "whatsapp"
) -> MessageResponse:
    """
    Async AI support agent entry point.

    Parameters
    ----------
    customer_message : The raw text the customer sent.
    customer_id      : Unique identifier for the customer (used for logging/context).
    channel          : Delivery channel — controls response formatting.

    Returns
    -------
    MessageResponse  : Always returns this object; never raises.
    """

    # ── Guard: reject empty messages immediately ──────────────────────────
    if not customer_message or not customer_message.strip():
        return MessageResponse(
            error="Message cannot be empty.",
            suggested_action="prompt_user_to_retry",
        )

    # ── Normalise channel name ────────────────────────────────────────────
    channel = channel.lower().strip()
    if channel not in ("voice", "chat", "whatsapp"):
        return MessageResponse(
            error=f"Unsupported channel '{channel}'. Use voice, chat, or whatsapp.",
            suggested_action="check_channel_configuration",
        )

    # ── Build the system prompt (telecom support persona) ─────────────────
    system_instruction = (
        "You are a helpful telecom customer support agent for NexusAI Telecom. "
        "You assist customers with billing questions, network issues, plan upgrades, "
        "SIM card problems, and general account management. "
        "Always be polite, concise, and solution-focused. "
        "At the end of your reply, on a NEW LINE, output exactly:\n"
        "CONFIDENCE: <float between 0.0 and 1.0>\n"
        "ACTION: <one short snake_case action, e.g. resolve_billing, escalate_to_human, "
        "send_technician, no_action_required>"
    )

    # ══════════════════════════════════════════════
    # STEP 3 — Call Groq API with error handling
    # ══════════════════════════════════════════════
    raw_llm_text = await _call_groq_with_retry(
        system_instruction=system_instruction,
        user_message=customer_message,
    )

    # If helper returned an error string (prefixed "ERROR:")
    if raw_llm_text.startswith("ERROR:"):
        return MessageResponse(
            error=raw_llm_text[len("ERROR:"):].strip(),
            suggested_action="retry_later",
        )

    # ── Parse LLM output: separate answer from metadata lines ────────────
    response_text, confidence, suggested_action = _parse_llm_output(raw_llm_text)

    # ── Format for the target channel ────────────────────────────────────
    channel_formatted_response = _format_for_channel(response_text, channel)

    return MessageResponse(
        response_text=response_text,
        confidence=confidence,
        suggested_action=suggested_action,
        channel_formatted_response=channel_formatted_response,
        error=None,
    )


# ══════════════════════════════════════════════
# Internal helpers
# ══════════════════════════════════════════════

async def _call_groq_with_retry(
    system_instruction: str,
    user_message: str,
) -> str:
    """
    Calls the Groq Chat Completions API (OpenAI-compatible) with:
      • a 10-second timeout   (asyncio.wait_for)
      • one automatic retry after 2 s on rate-limit (HTTP 429)

    Returns the model's text, or a string starting with "ERROR:" on failure.

    Groq uses the OpenAI-compatible format:
      POST https://api.groq.com/openai/v1/chat/completions
      Authorization: Bearer <GROQ_API_KEY>
      Body: { model, messages: [{role, content}, ...], max_tokens, temperature }
    """
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": GROQ_MODEL,
        "max_tokens": 512,
        "temperature": 0.4,
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user",   "content": user_message},
        ],
    }

    async def _attempt(session: aiohttp.ClientSession) -> str:
        """Single HTTP POST to Groq, wrapped in a 10-second timeout."""
        resp = await asyncio.wait_for(
            session.post(GROQ_URL, headers=headers, json=payload),
            timeout=10.0,       # ← 10 s hard timeout
        )

        if resp.status == 429:
            raise _RateLimitError("Groq rate limit hit (HTTP 429)")

        if resp.status != 200:
            body = await resp.text()
            raise _APIError(f"HTTP {resp.status}: {body[:200]}")

        data = await resp.json()

        # Groq follows OpenAI response shape:
        # data["choices"][0]["message"]["content"]
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise _APIError(f"Unexpected response shape: {exc}") from exc

    async with aiohttp.ClientSession() as session:

        # ── First attempt ─────────────────────────────────────────────────
        try:
            return await _attempt(session)

        except asyncio.TimeoutError:
            # Timeout → no retry, fail immediately
            return "ERROR: Request timed out after 10 seconds."

        except _RateLimitError:
            # Rate-limited → wait 2 s, retry once
            await asyncio.sleep(2)
            try:
                return await _attempt(session)
            except asyncio.TimeoutError:
                return "ERROR: Request timed out on retry."
            except _RateLimitError:
                return "ERROR: Rate limit exceeded. Please try again later."
            except _APIError as exc:
                return f"ERROR: API error on retry — {exc}"

        except _APIError as exc:
            return f"ERROR: API error — {exc}"


# ── Thin custom exceptions ────────────────────────────────────────────────
class _RateLimitError(Exception):
    pass

class _APIError(Exception):
    pass


def _parse_llm_output(raw: str) -> tuple[str, float, str]:
    """
    Splits the LLM reply into (response_text, confidence, suggested_action).

    The model is prompted to append two metadata lines:
        CONFIDENCE: 0.92
        ACTION: resolve_billing
    Everything above those lines is the human-facing answer.
    """
    lines = raw.strip().splitlines()
    confidence = 0.5
    suggested_action = "no_action_required"
    body_lines = []

    for line in lines:
        stripped = line.strip()
        if stripped.upper().startswith("CONFIDENCE:"):
            try:
                value = stripped.split(":", 1)[1].strip()
                confidence = float(value)
                confidence = max(0.0, min(1.0, confidence))   # clamp to [0,1]
            except ValueError:
                pass
        elif stripped.upper().startswith("ACTION:"):
            suggested_action = stripped.split(":", 1)[1].strip()
        else:
            body_lines.append(line)

    response_text = "\n".join(body_lines).strip()
    return response_text, confidence, suggested_action


def _format_for_channel(text: str, channel: str) -> str:
    """
    Shapes the response to fit the channel's UX constraints.

    voice     → max 2 sentences (short, speakable)
    chat      → full explanation, preserve all detail
    whatsapp  → conversational tone, trimmed to ~3 sentences
    """
    if channel == "voice":
        sentences = _split_sentences(text)
        return " ".join(sentences[:2])

    elif channel == "chat":
        return text                      # no truncation

    elif channel == "whatsapp":
        sentences = _split_sentences(text)
        return " ".join(sentences[:3])

    return text   # fallback (should not be reached)


def _split_sentences(text: str) -> list[str]:
    """Naïve sentence splitter on '.', '!', '?' followed by whitespace or end."""
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    return [p for p in parts if p]


# ══════════════════════════════════════════════
# Quick manual test
# Run:  python ai_message_handler.py
# Needs GROQ_API_KEY set in .env
# ══════════════════════════════════════════════

# ══════════════════════════════════════════════
# Interactive CLI
# Run:  python ai_message_handler.py
# Needs GROQ_API_KEY set in .env
# Type 'exit' or 'quit' to stop
# ══════════════════════════════════════════════
if __name__ == "__main__":

    VALID_CHANNELS = ("voice", "chat", "whatsapp")

    def prompt_channel() -> str:
        """Ask user to pick a channel; keep asking until valid."""
        while True:
            ch = input("Channel (voice / chat / whatsapp) [default: chat]: ").strip().lower()
            if ch == "":
                return "chat"
            if ch in VALID_CHANNELS:
                return ch
            print(f"  ⚠  Invalid channel. Choose from: {', '.join(VALID_CHANNELS)}")

    async def main():
        print("=" * 60)
        print("  NexusAI Telecom — Support Agent  (powered by Groq)")
        print("  Type 'exit' or 'quit' to stop.")
        print("=" * 60)

        customer_id = input("\nEnter your Customer ID (or press Enter for GUEST): ").strip()
        if not customer_id:
            customer_id = "GUEST"

        while True:
            print()
            message = input("You: ").strip()

            # Exit conditions
            if message.lower() in ("exit", "quit", "q"):
                print("Goodbye! 👋")
                break

            # Pick channel for this message
            channel = prompt_channel()

            print("\n⏳ Thinking...\n")
            result = await handle_message(message, customer_id, channel)

            if result.error:
                print(f"❌ Error        : {result.error}")
                print(f"   Action       : {result.suggested_action}")
            else:
                print(f"🤖 Agent ({channel}):")
                print(f"   {result.channel_formatted_response}")
                print()
                print(f"   📊 Confidence      : {result.confidence:.0%}")
                print(f"   🔧 Suggested action: {result.suggested_action}")

            print("-" * 60)

    asyncio.run(main())
