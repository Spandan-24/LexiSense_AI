# 🧠 LexiSense AI v3.0 — Complete VS Code Setup Guide

**JISTech2K26 · JIS College of Engineering · Information Technology**
Team Lead: Spandan Karfa | Guide: Rupashri Barik

---

## 📁 Final Project Folder Structure

```
LexiSenseAI/
├── run.py                        ← ONE-CLICK START (run this!)
├── README_SETUP.md               ← This file
├── backend/
│   ├── app.py                    ← Flask backend (all APIs)
│   ├── requirements.txt          ← Python packages list
│   └── templates/
│       └── index.html            ← Complete UI (10 pages)
└── database/
    └── lexisense.db              ← Auto-created on first run
```

---

## 🖥️ STEP-BY-STEP VS CODE SETUP

---

### STEP 1 — Install Python 3.10 or higher

1. Go to https://python.org/downloads
2. Download **Python 3.10+** for your OS
3. During installation on Windows:
   - ✅ Check **"Add Python to PATH"** (VERY IMPORTANT)
   - Click "Install Now"
4. Verify install — open Terminal / CMD and type:
   ```
   python --version
   ```
   You should see: `Python 3.10.x` or higher

---

### STEP 2 — Install Visual Studio Code

1. Go to https://code.visualstudio.com
2. Download and install for your OS
3. Open VS Code

---

### STEP 3 — Install VS Code Extensions

Open VS Code → Press `Ctrl+Shift+X` → Search and install:

| Extension | Publisher | Purpose |
|---|---|---|
| **Python** | Microsoft | Python language support |
| **Pylance** | Microsoft | Python intellisense |

---

### STEP 4 — Open Project in VS Code

**Option A — Drag & Drop:**
- Drag the `LexiSenseAI` folder onto VS Code

**Option B — File menu:**
- VS Code → File → Open Folder → Select `LexiSenseAI`

**Option C — Terminal:**
```bash
cd path/to/LexiSenseAI
code .
```

---

### STEP 5 — Open Integrated Terminal

In VS Code: Press `` Ctrl+` `` (backtick)

Or go to: **Terminal → New Terminal**

Make sure you are in the `LexiSenseAI` folder:
```bash
# You should see something like:
# C:\Users\YourName\LexiSenseAI>
# or
# /home/username/LexiSenseAI$
```

If not, navigate there:
```bash
cd LexiSenseAI
```

---

### STEP 6 — Create Virtual Environment (Recommended)

```bash
python -m venv venv
```

**Activate it:**

Windows:
```bash
venv\Scripts\activate
```

Mac / Linux:
```bash
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal line.

---

### STEP 7 — Install Required Packages

```bash
pip install flask flask-cors flask-sqlalchemy werkzeug
pip install gtts googletrans==4.0.0-rc1
pip install reportlab Pillow
```

Or install everything at once:
```bash
pip install -r backend/requirements.txt
```

**Verify installation:**
```bash
pip list
```
You should see flask, flask-cors, flask-sqlalchemy, gtts, etc.

---

### STEP 8 — Run the Project

**Easiest way — one command from LexiSenseAI folder:**
```bash
python run.py
```

This will:
1. ✅ Auto-install any missing packages
2. ✅ Create the SQLite database automatically
3. ✅ Start Flask server on http://localhost:5000
4. ✅ Open your browser automatically

**Alternative — run backend directly:**
```bash
cd backend
python app.py
```

---

### STEP 9 — Open in Browser

If browser didn't open automatically:
- Open Chrome or Edge
- Go to: **http://localhost:5000**

You will see the LexiSense AI login screen.

---

### STEP 10 — Create Your Account

1. Click **"Create Account"**
2. Enter your Full Name, Username, Email, Password
3. Click **"Create Account →"**
4. You are now logged in!

Or click **"Continue as Guest"** to use without saving progress.

---

## 📷 OCR SETUP (for Real Image Text Extraction)

Without this, OCR works in demo mode only.

### Windows:
1. Download Tesseract installer:
   https://github.com/UB-Mannheim/tesseract/wiki
2. Run installer → Select **"Bengali"** language pack during install
3. Default install path: `C:\Program Files\Tesseract-OCR\`
4. Open `backend/app.py` in VS Code
5. Find this line and **uncomment it** (remove the `#`):
   ```python
   # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```
6. Save the file and restart the server

### Linux (Ubuntu/Debian):
```bash
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-ben
pip install pytesseract
```

### Mac:
```bash
brew install tesseract
pip install pytesseract
```

---

## 🌐 Bengali Voice (TTS) Setup

Bengali voice works through the browser's Web Speech API.

**For best Bengali voice support:**
- Use **Google Chrome** on Windows/Mac/Android
- Go to: Chrome Settings → Languages → Add **Bengali (Bangladesh)**
- Restart Chrome

On Windows, you can also install Bengali TTS voices:
- Settings → Time & Language → Language → Add Bengali → Download voice pack

---

## 🔧 Troubleshooting

**Problem: `ModuleNotFoundError: No module named 'flask'`**
```bash
pip install flask flask-cors flask-sqlalchemy
```

**Problem: Port 5000 already in use**
- Change port in `backend/app.py`:
  ```python
  app.run(debug=True, port=5001)
  ```
- Then open: http://localhost:5001

**Problem: "Backend Offline" in browser**
- Make sure `python run.py` is running in terminal
- Check terminal for error messages
- Make sure you activated venv

**Problem: Translation not working**
- Install exact version: `pip install googletrans==4.0.0-rc1`
- Do NOT install googletrans 3.x

**Problem: `ModuleNotFoundError: No module named 'PIL'`**
```bash
pip install Pillow
```

**Problem: Speech recognition not working**
- Must use **Chrome** or **Edge** browser
- Allow microphone permission when the browser asks
- HTTPS or localhost only

**Problem: Bengali text not showing correctly**
- Make sure Noto Sans Bengali font is loading (requires internet)
- Or set font to "Noto Sans Bengali" in Reading Settings

---
## 🔧 Techstack

Frontend

Pure HTML5, CSS3, and vanilla JavaScript (single index.html file — no framework)
Google Fonts: Lexend, Noto Sans Bengali, Playfair Display, DM Mono, Outfit
Web Speech API (browser-native TTS and speech recognition)

Backend

Python 3 with Flask (web framework)
Flask-CORS (cross-origin support)
Flask-SQLAlchemy (ORM)
Werkzeug (password hashing / security)

Database

SQLite (via SQLAlchemy) — stored as lexisense.db

AI / NLP

pytesseract + Tesseract-OCR engine (image-to-text OCR, Bengali + English)
Pillow / PIL (image preprocessing for OCR)
gTTS — Google Text-to-Speech (Bengali MP3 generation)
googletrans 4.0.0-rc1 (translation, 20+ languages)
Custom rule-based NLP (80+ word simplification mappings for English and Bengali)
Flesch-Kincaid readability scoring (custom implementation)

Export

ReportLab (PDF generation)
gTTS (MP3 audio export)


## 🎯 Demo Script for JISTech2K26

Run in this order for maximum impact:

1. **Dashboard** — show live analytics metrics
2. **Sign Up** — create account, show authentication
3. **Smart Reader** → paste text → AI Simplify → click words for definitions
4. **Bengali Sample** → shows Bengali text processing
5. **OCR Scanner** → upload image OR click Demo Text → show Actual vs Simplified tabs
6. **Text to Speech** → select Bengali voice → Play → show live word highlighting
7. **Translator** → type English → live translate to Bengali
8. **Dyslexia Check** → Letter test → show error tracking
9. **Word Order** → drag tiles into correct order
10. **Speech Test** → New Passage → Mic → Analyse Reading
11. **Progress** → show live charts from real session data
12. **Smart Search** → search "dyslexia" → show knowledge base
13. **Reading Settings** → change font, spacing, overlay → live preview

---

## 🌟 All Features Summary

| Feature | Technology |
|---|---|
| Login / Sign Up | Flask + SQLite + Werkzeug |
| AI Text Simplification | Python NLP (80+ replacements) |
| Readability Score | Flesch-Kincaid Formula |
| Bengali Text Support | Noto Sans Bengali font |
| Bengali Voice (TTS) | Web Speech API (bn-BD/bn-IN) |
| Bengali OCR | pytesseract (ben+eng) |
| Actual + Simplified OCR | Two-tab display |
| Universal Translator | googletrans (20+ languages) |
| Smart Search | Flask knowledge base API |
| Letter Challenge | Custom challenge engine |
| Word Order Challenge | Drag & drop + click |
| Speech Assessment | Web Speech API + Levenshtein |
| Dyslexia Risk Report | Error pattern analysis |
| Real-time Analytics | SQLite live queries |
| 7-day Activity Chart | Session database |
| Word Dictionary | Flask API + Bengali TTS |
| Personal Vocabulary | Per-user SQLite storage |
| Reading Ruler | Mouse-following CSS overlay |
| Color Overlays | CSS rgba filter |
| Focus Mode | Reading aid toggle |
| Font Cycling | CSS variable injection |
| Export PDF | ReportLab |
| Export MP3 | gTTS |
| Settings to DB | SQLite UserSettings model |

---

*LexiSense AI v3.0 — Production Ready · Flask + SQLite + NLP + OCR + TTS + Bengali*
