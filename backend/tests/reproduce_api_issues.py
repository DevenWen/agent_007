import os
import asyncio
from unittest.mock import MagicMock, patch
import json

# Mocking the imports that would fail outside the app environment
import sys
from dotenv import load_dotenv

load_dotenv(override=True)

sys.modules["app"] = MagicMock()
sys.modules["app.database"] = MagicMock()
sys.modules["app.models"] = MagicMock()
sys.modules["app.models.agent"] = MagicMock()
sys.modules["app.models.ticket"] = MagicMock()
sys.modules["app.models.session"] = MagicMock()
sys.modules["app.models.message"] = MagicMock()
sys.modules["app.models.step"] = MagicMock()
sys.modules["app.tools"] = MagicMock()
sys.modules["app.scheduler.base_executor"] = MagicMock()

# Import the class we want to test
# We need to be careful about relative imports in the real executor.py
# For reproduction, let's just simulate the logic.


async def simulate_api_call(model_name, api_key, base_url=None):
    import anthropic

    print(f"\nTesting model: {model_name}")
    try:
        # Initialize client
        if base_url:
            client = anthropic.Anthropic(api_key=api_key, base_url=base_url)
        else:
            client = anthropic.Anthropic(api_key=api_key)

        # Build conversation messages
        messages = []

        # Turn 1: User says hello
        print("Turn 1: User says '你好'")
        messages.append({"role": "user", "content": "你好"})

        response1 = client.messages.create(
            model=model_name,
            max_tokens=1024,
            messages=messages,
        )

        # Extract assistant response and add to messages
        assistant_content = ""
        for block in response1.content:
            if hasattr(block, "text"):
                assistant_content += block.text
            elif hasattr(block, "thinking"):
                print(f"  [Thinking]: {block.thinking[:100]}...")
        print(f"Assistant: {assistant_content}")
        messages.append({"role": "assistant", "content": assistant_content})

        # Turn 2: User asks what model
        print("\nTurn 2: User asks '你是什么模型？'")
        messages.append({"role": "user", "content": "你是什么模型？"})

        response2 = client.messages.create(
            model=model_name,
            max_tokens=1024,
            messages=messages,
        )

        assistant_content2 = ""
        for block in response2.content:
            if hasattr(block, "text"):
                assistant_content2 += block.text
            elif hasattr(block, "thinking"):
                print(f"  [Thinking]: {block.thinking[:100]}...")
        print(f"Assistant: {assistant_content2}")

        print("\nMulti-turn conversation completed successfully!")

    except Exception as e:
        print(f"Caught error: {type(e).__name__}: {e}")


if __name__ == "__main__":
    # Simulate Minimax (assuming user set ANTHROPIC_MODEL to a minimax model)
    api_key = os.environ["ANTHROPIC_API_KEY"]

    print("Scenario 1: Default Anthropic Client with Minimax model name")
    asyncio.run(
        simulate_api_call("MiniMax-M2.1", api_key, "https://api.minimax.chat/anthropic")
    )
