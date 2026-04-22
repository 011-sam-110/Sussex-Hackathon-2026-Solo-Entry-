import os
from gradient import Gradient
from dotenv import load_dotenv

load_dotenv()

client = Gradient(
    model_access_key=os.environ.get("MODEL_ACCESS_KEY"),
)

SYSTEM_GUIDELINES = """
Role: You are a Screen Navigator that helps seniors use their computer.
Goal: Look at the screenshot and complete the user's task using mouse/keyboard commands.

You can SEE the screen. Use the screenshot to identify exact pixel positions of UI elements.

### COMMAND RULES:
1. ALL commands MUST be wrapped in a single @ block at the VERY START of your response.
2. Format: @*command1*,*command2*,*command3*@
3. If you cannot finish a task in one go, you MUST use *loop [summary]* as your LAST command. This is MANDATORY.
4. If no action is needed, start your response with 'NO_COMMAND'.
5. All coordinates must be pixel positions based on what you see in the screenshot.

### COMMAND LIST:
- *lclick [x,y]* : Left click at pixel coordinates.
- *rclick [x,y]* : Right click at pixel coordinates.
- *dclick [x,y]* : Double click at pixel coordinates.
- *type [text]* : Type text (you MUST click an input field first).
- *presskey [key]* : Press a single key (enter, escape, tab, etc.).
- *hotkey [key1,key2]* : Press a key combination (e.g., ctrl,k).
- *loop [summary]* : Refresh your view of the screen. Summarize what you did and what you need next.
- *endloop [done]* : End the loop when the task is fully complete.

### IMPORTANT:
- To type into a form field, click the CENTER of the actual INPUT BOX (the empty rectangle), NOT the text label above it.
- Coordinates should target the CENTER of the element you want to interact with.
- If a task needs multiple steps (e.g., search then click a result), use *loop* after the first step to see the updated screen.
- Review conversation history to avoid repeating actions you already took.
- When double-clicking to open or play something, use *dclick*.

### EXAMPLE — Login form (screen is 1920x1080):
@*lclick [510,410]*,*type [admin]*,*lclick [510,478]*,*type [secret]*,*lclick [359,533]*,*loop [Entered username and password, clicked Submit. Need to check if login succeeded.]*@
I've entered the credentials and clicked Submit. Checking the result now.

### CRITICAL:
If the task is NOT fully complete, your LAST command MUST be *loop [summary]*. NEVER skip it.
"""


def sendMessage(message, screenshot_b64, screen_width, screen_height, history=None):
    text_content = (
        f"Screen resolution: {screen_width}x{screen_height}\n"
        f"USER REQUEST: {message}\n"
        "Provide a concise update (max 5 sentences) after the command block. "
        "Start IMMEDIATELY with the @ block. "
        "REMEMBER: If the task is not complete, end with *loop [summary]*."
    )

    user_message = {
        "role": "user",
        "content": [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{screenshot_b64}",
                    "detail": "high",
                },
            },
            {
                "type": "text",
                "text": text_content,
            },
        ],
    }

    messages = [{"role": "system", "content": SYSTEM_GUIDELINES}]
    if history:
        messages.extend(history)
    messages.append(user_message)

    response = client.chat.completions.create(
        model="openai-gpt-4o",
        messages=messages,
        max_tokens=4000,
    )

    raw_content = response.choices[0].message.content
    print(f"Raw LLM response: {raw_content}")

    user_prompt_text = f"[Screenshot {screen_width}x{screen_height}]\n{text_content}"
    return {"response": raw_content, "user_prompt_used": user_prompt_text}
