# The Navigator — AI Desktop Assistant

> Built in **15 hours** during a 24-hour hackathon (Feb 28 – Mar 1, 2026).

The Navigator is a full-stack AI agent built to help older users navigate their computers independently. Modern UIs are often a barrier — harsh color schemes make buttons hard to spot, cluttered layouts are disorienting, and multi-step workflows like sending an email or finding a photo can be genuinely confusing. The Navigator solves this by acting as a sighted co-pilot: it looks at whatever is on the screen, locates elements the user can't easily find, and completes tasks on their behalf — all triggered by a plain English request.

A user types "find my photos from last Christmas" or "help me reply to this email" — and the system sees the screen exactly as they do, identifies the right buttons and inputs, and executes the clicks and keystrokes autonomously.

---

## How It Works

```
User types a request
        ↓
Frontend captures a screenshot (full resolution, JPEG compressed)
        ↓
Screenshot + request sent to FastAPI backend (via ngrok tunnel)
        ↓
GPT-4o Vision analyzes the screen and emits a command block
        ↓
Frontend parses and executes the commands (mouse clicks, keyboard input)
        ↓
If task is incomplete → loop: re-screenshot and continue
```

---

## The LLM Command Language

The core of this project is a **custom mini-language** that constrains the LLM's output into structured, executable instructions. Rather than generating freeform prose, the model is prompted to respond in a strict DSL:

```
@*lclick [510,410]*,*type [admin]*,*lclick [510,478]*,*type [secret]*,*presskey [enter]*,*loop [Entered credentials, checking result.]*@
I've entered the login details and submitted the form.
```

### Command Reference

| Command | Syntax | Description |
|---|---|---|
| `lclick` | `*lclick [x,y]*` | Left-click at pixel coordinates |
| `rclick` | `*rclick [x,y]*` | Right-click at pixel coordinates |
| `dclick` | `*dclick [x,y]*` | Double-click (open/launch) |
| `type` | `*type [text]*` | Type text into focused input |
| `presskey` | `*presskey [enter]*` | Press a single key |
| `hotkey` | `*hotkey [ctrl,c]*` | Press a key combination |
| `loop` | `*loop [summary]*` | Re-capture screen and continue the task |
| `endloop` | `*endloop [done]*` | Signal task completion |

The parser splits on `@` delimiters to extract the command block, then splits on `*` to unstack individual commands. Each command is dispatched to a `pyautogui` handler. The `loop` command triggers a full re-capture cycle, injecting updated conversation history so the model never repeats steps it already took. A safety cap of **5 loop continuations** prevents runaway agents.

This design solves a real problem: vision-language models are unreliable when allowed to output anything. By forcing a structured format, the system becomes deterministic and debuggable.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI + Uvicorn |
| LLM | GPT-4o (vision) via Gradient API |
| Desktop App | pywebview (Python ↔ HTML bridge) |
| UI | HTML + Tailwind CSS |
| Screen Capture | mss + OpenCV (BGRA → JPEG, base64 encoded) |
| Desktop Automation | pyautogui |
| Tunnel | ngrok (local dev → public HTTPS endpoint) |
| Config | python-dotenv |

---

## Architecture

```
Blank/
├── Backend/
│   ├── routes.py          # FastAPI app — POST /upload-text
│   └── utils/
│       └── llm.py         # System prompt, Gradient client, message builder
├── Frontend/
│   ├── front.py           # pywebview app, command executor, loop engine
│   ├── client.py          # HTTP client — screenshot capture + API call
│   ├── index.html         # Side-panel UI (350px, Tailwind)
│   ├── main.js            # pywebview JS bridge
│   └── utils/
│       └── buttonLocations.py  # mss + OpenCV screenshot pipeline
└── runbackend.py          # Convenience launcher for FastAPI
```

**Frontend and backend are intentionally decoupled.** The backend runs on a remote VPS; the frontend is a local desktop app that communicates over HTTPS via a ngrok URL stored in `.env`. This means the heavy LLM inference runs off-device — critical for a tool targeting low-end senior hardware.

---

## Key Engineering Details

**Agentic loop with conversation memory** — Each loop iteration appends the previous assistant response and the new screenshot-augmented prompt to `conversation_history`. The model has full context of every action it has already taken, preventing duplicate clicks and enabling recovery from failed steps.

**Vision-first coordinate targeting** — The model is shown the raw screenshot at its native resolution and asked to identify pixel coordinates of UI elements. No element labeling, DOM scraping, or accessibility tree walking — just pure visual grounding. This works across any application, including native desktop apps where DOM access is impossible.

**Prompt engineering as a type system** — The system prompt functions like a type contract: it defines the exact grammar the model must emit, provides worked examples, and includes explicit failure modes (`NO_COMMAND`, mandatory `*loop*` on incomplete tasks). This constraint engineering was the most iterated-on part of the project.

**Screenshot compression pipeline** — Raw mss captures are BGRA arrays. OpenCV converts to BGR, then JPEG-encodes at 85% quality before base64 encoding. This keeps payloads small enough for fast round-trips while preserving enough fidelity for GPT-4o to read small UI text.

---

## Setup

### Backend
```bash
cd Backend
pip install fastapi uvicorn python-dotenv gradient-ai
# Add MODEL_ACCESS_KEY to .env
python -m fastapi dev routes.py
```

### Frontend
```bash
cd Frontend
pip install pywebview requests python-dotenv mss opencv-python pyautogui numpy
# Add NGROK_URL to .env
python front.py
```

---

## What I'd Build Next

- **Voice input** — replace the textarea with whisper transcription for users who struggle to type
- **Action confirmation UI** — show the planned command list before executing, with one-click approval
- **Smarter coordinate resolution** — add a lightweight YOLO model for UI element detection to reduce reliance on LLM pixel estimation
- **Packaged installer** — bundle with PyInstaller so seniors can run it without a Python environment
