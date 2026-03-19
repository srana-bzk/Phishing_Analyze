"""
image_reader.py
---------------
Extracts text from an image (e.g. a screenshot of a phishing email) using
a locally-running vision model via Ollama.

Uses gemma3:4b by default — it is already installed and supports vision.
Ollama exposes an OpenAI-compatible API, so we reuse the openai library.
"""

import base64
import os
from openai import OpenAI

OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_API_KEY  = "ollama"
VISION_MODEL    = "gemma3:4b"   # change to llava, qwen2-vl, etc. if preferred

# File extensions we consider images
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}

# Maps file extension → MIME type for the API call
MIME_MAP = {
    ".jpg":  "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png":  "image/png",
    ".gif":  "image/gif",
    ".webp": "image/webp",
    ".bmp":  "image/bmp",
}


def is_image(path: str) -> bool:
    """Return True if the file extension looks like an image."""
    return os.path.splitext(path)[1].lower() in IMAGE_EXTENSIONS


def extract_text_from_image(image_path: str, chunk_callback=None) -> str:
    """
    Send the image to the local Ollama vision model and extract all visible text.

    chunk_callback(str) — optional; called with each streaming token so the
    caller can display live progress.

    Returns the extracted text as a plain string.
    Raises RuntimeError if Ollama is not running or the model is missing.
    """
    ext       = os.path.splitext(image_path)[1].lower()
    mime_type = MIME_MAP.get(ext, "image/jpeg")

    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")

    system_prompt = (
        "You are an OCR assistant. Extract ALL text visible in the image exactly "
        "as it appears. The image is likely a screenshot of an email or webpage. "
        "Include: sender address, recipient, subject line, body text, and any URLs "
        "or links you can see. Output only the extracted text — no commentary, "
        "no explanations."
    )

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{image_b64}"
                    },
                },
                {
                    "type": "text",
                    "text": system_prompt,
                },
            ],
        }
    ]

    try:
        client = OpenAI(api_key=OLLAMA_API_KEY, base_url=OLLAMA_BASE_URL)

        if chunk_callback:
            stream = client.chat.completions.create(
                model=VISION_MODEL,
                messages=messages,
                max_tokens=1000,
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
            response = client.chat.completions.create(
                model=VISION_MODEL,
                messages=messages,
                max_tokens=1000,
            )
            return response.choices[0].message.content.strip()

    except Exception as e:
        err = str(e).lower()
        if "connection" in err or "refused" in err:
            raise RuntimeError(
                "Cannot connect to Ollama.\n\n"
                "Make sure Ollama is running:\n"
                "  1. Install from https://ollama.com/download\n"
                f"  2. Run:  ollama pull {VISION_MODEL}\n"
                "  3. Ollama starts automatically — try again."
            )
        if "not found" in err or "model" in err:
            raise RuntimeError(
                f"Vision model '{VISION_MODEL}' not found in Ollama.\n\n"
                f"Pull it with:\n  ollama pull {VISION_MODEL}"
            )
        raise RuntimeError(str(e))
