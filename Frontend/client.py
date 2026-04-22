import requests
import os
from dotenv import load_dotenv
from utils.buttonLocations import capture_screenshot_b64

load_dotenv()
NGROK_URL = os.getenv("NGROK_URL")


def sendQuery(userPrompt, history=None):
    screenshot_b64, width, height = capture_screenshot_b64()
    payload = {
        "user_prompt": userPrompt,
        "screenshot_b64": screenshot_b64,
        "screen_width": width,
        "screen_height": height,
        "history": history,
    }
    print("-" * 50)
    response = requests.post(
        f"{NGROK_URL}/upload-text",
        json=payload,
        timeout=120,
    )
    print(response)
    try:
        data = response.json()
        return {
            "response": data.get("response", response.text),
            "user_prompt_used": data.get("user_prompt_used", ""),
        }
    except Exception:
        return {"response": response.text, "user_prompt_used": ""}


if __name__ == "__main__":
    result = sendQuery("What is on my screen?")
    print(result["response"])
