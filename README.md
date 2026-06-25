<h1 align="center">The Navigator</h1>
<p align="center">An AI desktop co-pilot that reads the screen and drives the mouse and keyboard for people who find computers hard.</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi&logoColor=white">
  <img src="https://img.shields.io/badge/Vision-GPT--4o-412991?logo=openai&logoColor=white">
  <img src="https://img.shields.io/badge/built%20in-~15h%20hackathon-orange">
</p>

The Navigator is a full-stack AI agent built to help older and less-confident users operate their
computers independently. It acts as a sighted co-pilot: it looks at whatever is on screen, finds the
elements the user cannot, and completes the task for them, all from a plain-English request like
"find my photos from last Christmas" or "help me reply to this email". A solo build, shipped in
~15 hours during a 24-hour hackathon (Feb 28 – Mar 1, 2026).

## ✨ Features
- **Plain-English control** — type a request; the agent works out the clicks and keystrokes and carries them out.
- **Vision-first targeting** — GPT-4o Vision reads the raw screenshot at native resolution and returns pixel coordinates, so it works on any app, including native desktop UIs with no DOM to scrape.
- **Structured command DSL** — the model must reply in a strict mini-language (`*lclick [x,y]*`, `*type [text]*`, `*loop [...]*`), which makes its output predictable to parse and safe to execute.
- **Agentic loop with memory** — after each action it re-screenshots and continues, carrying the full history of what it already did, so it recovers from failures without repeating steps. A 5-continuation cap stops runaways.
- **Off-device inference** — the FastAPI backend runs on a remote VPS reached over an ngrok tunnel, keeping heavy LLM work off the low-end hardware the tool targets.

## 🛠 Stack
| Layer | Tech |
|---|---|
| Backend API | FastAPI + Uvicorn |
| LLM | GPT-4o (vision) via Gradient API |
| Desktop app | pywebview (Python ↔ HTML bridge) |
| UI | HTML + Tailwind CSS |
| Screen capture | mss + OpenCV (BGRA → JPEG, base64) |
| Automation | pyautogui |
| Tunnel | ngrok |

## 🚀 Run
**Backend** (the machine doing inference):
```bash
cd Backend
pip install fastapi uvicorn python-dotenv gradient-ai
# add MODEL_ACCESS_KEY to .env
python -m fastapi dev routes.py
```
**Frontend** (the desktop app on the user's machine):
```bash
cd Frontend
pip install pywebview requests python-dotenv mss opencv-python pyautogui numpy
# add NGROK_URL to .env (points at the backend tunnel)
python front.py
```

## 🧠 How it works
```
User types a request
        ↓
Frontend captures a screenshot (full-res, JPEG-compressed)
        ↓
screenshot + request → FastAPI backend (via ngrok tunnel)
        ↓
GPT-4o Vision reads the screen and emits a command block
        ↓
Frontend parses and executes it (mouse clicks, keystrokes)
        ↓
if incomplete → loop: re-screenshot and continue
```

The core is the command language. Instead of free prose, the model replies in a strict DSL that the
frontend parses on `@` then `*` delimiters and dispatches to `pyautogui`:

| Command | Syntax | Does |
|---|---|---|
| `lclick` / `rclick` / `dclick` | `*lclick [x,y]*` | click at pixel coordinates |
| `type` | `*type [text]*` | type into the focused input |
| `presskey` / `hotkey` | `*presskey [enter]*` | press a key / combo |
| `loop` | `*loop [summary]*` | re-capture the screen and continue |
| `endloop` | `*endloop [done]*` | signal completion |

Frontend and backend are intentionally decoupled (`Backend/routes.py` exposes `POST /upload-text`;
`Frontend/front.py` runs the executor + loop engine). The system prompt acts like a type contract:
it defines the grammar, gives worked examples, and lists explicit failure modes (`NO_COMMAND`,
mandatory `*loop*` on incomplete tasks). That constraint engineering was the most iterated-on part
of the build.

## 🗺 Roadmap
Working hackathon prototype; runs locally with the backend reachable over ngrok.
- [ ] Voice input (Whisper) for users who struggle to type
- [ ] Action-confirmation UI: preview the planned commands before they run
- [ ] Lightweight YOLO UI-element detector to reduce reliance on LLM pixel estimates
- [ ] PyInstaller package so non-technical users can run it without Python
- Known limitation: it executes clicks and keystrokes autonomously, so run it on a screen you are supervising.
