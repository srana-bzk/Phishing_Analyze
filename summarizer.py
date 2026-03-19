"""
summarizer.py
-------------
Generates a plain-English summary of an analysis result using
a locally-running Qwen model via Ollama.

Requires:
  1. Ollama installed: https://ollama.com/download
  2. Qwen model pulled: ollama pull qwen2.5:3b

Ollama exposes an OpenAI-compatible API at http://localhost:11434/v1
so we reuse the openai library — no API key needed.
"""

from openai import OpenAI

# ── Local Ollama settings ─────────────────────────────────────────────────────
OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_API_KEY  = "ollama"          # Ollama ignores the key; any string works
QWEN_MODEL      = "qwen2.5:3b"     # change to qwen2.5:7b for better quality


def generate_summary(result: dict, chunk_callback=None) -> str:
    """
    Build a context-aware prompt from the analysis result and ask
    the local Qwen model to explain it in plain English.

    chunk_callback(str) — if provided, the function streams tokens one by one
    and calls chunk_callback with each piece.  The full text is still returned
    when the stream ends.

    Returns the summary string.
    Raises RuntimeError if Ollama is not running or the model is missing.
    """
    result_type = result.get("type", "email")

    if result_type == "ip":
        prompt_body = (
            f"VirusTotal IP reputation check for {result.get('ip', '?')}:\n"
            f"- Risk level: {result.get('risk_level', '?')}\n"
            f"- Malicious detections: {result.get('malicious', 0)} / {result.get('total_engines', 0)} engines\n"
            f"- Suspicious detections: {result.get('suspicious', 0)}\n"
            f"- Country: {result.get('country', '?')}, Owner: {result.get('as_owner', '?')}\n"
            f"- Reputation score: {result.get('reputation', 0)}\n"
            f"- Flagged by: {', '.join(result.get('flagged_engines', [])[:10]) or 'none'}"
        )

    elif result_type == "domain":
        prompt_body = (
            f"VirusTotal domain reputation check for {result.get('domain', '?')}:\n"
            f"- Risk level: {result.get('risk_level', '?')}\n"
            f"- Malicious detections: {result.get('malicious', 0)} / {result.get('total_engines', 0)} engines\n"
            f"- Suspicious detections: {result.get('suspicious', 0)}\n"
            f"- Registrar: {result.get('registrar', '?')}, Created: {result.get('creation_date', '?')}\n"
            f"- Categories: {', '.join(result.get('categories', [])[:5]) or 'none'}\n"
            f"- Reputation score: {result.get('reputation', 0)}\n"
            f"- Flagged by: {', '.join(result.get('flagged_engines', [])[:10]) or 'none'}"
        )

    else:  # email analysis
        findings_text = "\n".join(f"  - {f}" for f in result.get("findings", []))
        prompt_body = (
            f"Phishing email analysis result:\n"
            f"- Risk score: {result.get('score', 0)} / 100  ({result.get('risk_level', '?')} risk)\n"
            f"- ML classifier verdict: {'Phishing' if result.get('ml_label', 0) == 1 else 'Safe'} "
            f"({round(result.get('ml_confidence', 0) * 100, 1)}% confidence)\n"
            f"- Keyword score: {result.get('keyword_score', 0):.0f}/100 "
            f"(hits: {', '.join(result.get('keyword_hits', [])[:8]) or 'none'})\n"
            f"- URL heuristics score: {result.get('url_score', 0):.0f}/100\n"
            f"- Blacklist score: {result.get('blacklist_score', 0):.0f}/100\n"
            f"- Findings:\n{findings_text or '  No specific findings.'}"
        )

    system_msg = (
        "You are a cybersecurity analyst investigating a potential threat. "
        "Think through the evidence out loud before reaching a conclusion — "
        "show your reasoning step by step:\n"
        "  Step 1 — What do the scores/numbers tell you?\n"
        "  Step 2 — What specific red flags or patterns stand out?\n"
        "  Step 3 — How confident are you in your assessment and why?\n"
        "  Step 4 — What is your final verdict and what should the user do?\n\n"
        "Write in plain English. Avoid jargon. Be thorough in your reasoning."
    )
    user_msg = (
        f"Here are the analysis results:\n\n{prompt_body}\n\n"
        "Walk through your analysis step by step, then give a clear final verdict."
    )

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user",   "content": user_msg},
    ]

    try:
        client = OpenAI(api_key=OLLAMA_API_KEY, base_url=OLLAMA_BASE_URL)

        if chunk_callback:
            # ── Streaming mode: emit each token via callback ────────────────
            stream = client.chat.completions.create(
                model=QWEN_MODEL,
                messages=messages,
                max_tokens=800,
                temperature=0.4,
                stream=True,
            )
            full_text = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                if delta:
                    full_text += delta
                    chunk_callback(delta)
            return full_text.strip()

        else:
            # ── Non-streaming mode (fallback) ───────────────────────────────
            response = client.chat.completions.create(
                model=QWEN_MODEL,
                messages=messages,
                max_tokens=800,
                temperature=0.4,
            )
            return response.choices[0].message.content.strip()

    except Exception as e:
        err = str(e).lower()
        if "connection" in err or "refused" in err:
            raise RuntimeError(
                "Cannot connect to Ollama.\n\n"
                "Make sure Ollama is running:\n"
                "  1. Install from https://ollama.com/download\n"
                f"  2. Run:  ollama pull {QWEN_MODEL}\n"
                "  3. Ollama starts automatically — try again."
            )
        raise RuntimeError(str(e))
