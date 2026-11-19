"""
╔══════════════════════════════════════════════════════════╗
║      LexiSense AI v3.0 — One-Click Startup               ║
║      JISTech2K26 · JIS College of Engineering            ║
║      Team Lead : Spandan Karfa                           ║
║      Guide     : Rupashri Barik                          ║
╚══════════════════════════════════════════════════════════╝

USAGE:
    python run.py
"""
import subprocess, sys, os, webbrowser, time, threading

BANNER = r"""
 _              _ ____
| |   _____  _(_) ___|  ___ _ __  ___  ___   /\  |
| |  / _ \ \/ / \___ \ / _ \ '_ \/ __|/ _ \ /  \ |
| |_|  __/>  <| |___) |  __/ | | \__ \  __// /\ \|
|____\___/_/\_\_|____/ \___|_| |_|___/\___/_/  \_|

          🧠 Intelligent Dyslexia Reading Assistant
          JISTech2K26 · JIS College of Engineering
          Department of Information Technology
"""

REQUIRED = [
    ("flask",          "flask"),
    ("flask_cors",     "flask-cors"),
    ("flask_sqlalchemy","flask-sqlalchemy"),
    ("werkzeug",       "werkzeug"),
    # ("dotenv",          "python-dotenv"),
]
OPTIONAL = [
    ("gtts",           "gtts",                    "Bengali/multilingual TTS audio"),
    ("googletrans",    "googletrans==4.0.0-rc1",   "Universal translation"),
    ("reportlab",      "reportlab",                "PDF export"),
    ("PIL",            "Pillow",                   "Image processing for OCR"),
    ("pytesseract",    "pytesseract",              "Real OCR (also needs Tesseract installed)"),
]

def pip(pkg):
    subprocess.check_call([sys.executable,"-m","pip","install",pkg,"--quiet"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def install():
    print("\n📦 Installing required packages…\n")
    for imp, pkg in REQUIRED:
        try:
            __import__(imp.replace("-","_"))
            print(f"  ✅  {pkg} (already installed)")
        except ImportError:
            try:
                print(f"  ⏳  Installing {pkg}…", end="", flush=True)
                pip(pkg)
                print(f"\r  ✅  {pkg}")
            except Exception:
                print(f"\r  ❌  {pkg} FAILED — try: pip install {pkg}")

    print("\n📦 Installing optional packages…\n")
    for imp, pkg, desc in OPTIONAL:
        try:
            __import__(imp)
            print(f"  ✅  {pkg:30s}  ({desc})")
        except ImportError:
            try:
                print(f"  ⏳  {pkg}…", end="", flush=True)
                pip(pkg)
                print(f"\r  ✅  {pkg:30s}  ({desc})")
            except Exception:
                print(f"\r  ⚠️   {pkg:30s}  (optional — {desc})")

def ocr_guide():
    print("""
┌─────────────────────────────────────────────────────┐
│  📷  OCR SETUP  (for real Bengali+English image OCR) │
├─────────────────────────────────────────────────────┤
│  Windows : Download installer from                   │
│   https://github.com/UB-Mannheim/tesseract/wiki      │
│   Select "Bengali" language during install           │
│   Then uncomment tesseract_cmd line in app.py        │
│                                                      │
│  Linux   : sudo apt install tesseract-ocr            │
│            sudo apt install tesseract-ocr-ben        │
│                                                      │
│  Mac     : brew install tesseract                    │
│            brew install tesseract-lang               │
│                                                      │
│  Without Tesseract → use "Demo Text" button in OCR   │
└─────────────────────────────────────────────────────┘""")

def open_browser():
    time.sleep(2.8)
    webbrowser.open("http://localhost:5000")
    print("  🌐  Browser opened → http://localhost:5000\n")

def main():
    print(BANNER)
    install()
    ocr_guide()

    # Go to backend dir
    backend = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
    os.chdir(backend)
    sys.path.insert(0, backend)

    threading.Thread(target=open_browser, daemon=True).start()

    try:
        from backend.app import app, init_db
        init_db()
        print("""
╔══════════════════════════════════════════════════════╗
║  🚀  LexiSense AI v3.0 — SERVER STARTED              ║
║  📍  http://localhost:5000                            ║
║  🛑  Press Ctrl+C to stop                            ║
╠══════════════════════════════════════════════════════╣
║  ✅  Login & Sign Up          ✅  Bengali OCR         ║
║  ✅  AI Text Simplification   ✅  Universal Translator ║
║  ✅  Bengali Voice (TTS)      ✅  Smart Search        ║
║  ✅  Real-time Analytics      ✅  Speech Assessment   ║
║  ✅  Dyslexia AI Checker      ✅  Word Dictionary     ║
╚══════════════════════════════════════════════════════╝
""")
        app.run(debug=False, port=5000, host="0.0.0.0")
    except ImportError as e:
        print(f"\n❌  Import failed: {e}")
        print("    Run this from the LexiSenseAI folder: python run.py\n")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋  LexiSense AI stopped. Goodbye!\n")

if __name__ == "__main__":
    main()
