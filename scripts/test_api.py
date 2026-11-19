"""Smoke test for the Anthropic API key in .env.

Sends one short prompt to Claude Haiku 5.5 and prints the reply plus token usage.
Run from anywhere:  python scripts/test_api.py
"""

import os
import sys
from pathlib import Path

import anthropic
from dotenv import load_dotenv

MODEL = "claude-haiku-5-5"
PROMPT = "Say hello in one sentence"

# Load .env from the repo root, regardless of the current working directory.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def main() -> int:
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY is empty. Paste your key into .env and try again.")
        return 1

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            output_config={"effort": "low"},  # simple task: keep thinking minimal
            messages=[{"role": "user", "content": PROMPT}],
        )
    except anthropic.AuthenticationError:
        print("Authentication failed: the API key in .env is invalid.")
        return 1
    except anthropic.PermissionDeniedError:
        print("Permission denied: the API key cannot use this model.")
        return 1
    except anthropic.NotFoundError:
        print(f"Model not found: {MODEL}")
        return 1
    except anthropic.RateLimitError:
        print("Rate limited or out of credits. Check your Anthropic Console billing.")
        return 1
    except anthropic.APIStatusError as e:
        print(f"API error {e.status_code}: {e.message}")
        return 1
    except anthropic.APIConnectionError:
        print("Network error: could not reach the Anthropic API.")
        return 1

    if response.stop_reason == "refusal":
        print("The model declined the request.")
        return 1

    reply = "".join(block.text for block in response.content if block.type == "text")

    print(f"Model:         {response.model}")
    print(f"Reply:         {reply.strip()}")
    print(f"Input tokens:  {response.usage.input_tokens}")
    print(f"Output tokens: {response.usage.output_tokens}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
