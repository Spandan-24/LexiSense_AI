r"""
╔══════════════════════════════════════════════════════════╗
║         LexiSense AI — Backend v3.0                      ║
║         JISTech2K26 · JIS College of Engineering         ║
║         Department of Information Technology             ║
║         Team Lead : Spandan Karfa                        ║
║         Guide     : Rupashri Barik                       ║
╚══════════════════════════════════════════════════════════╝
"""

import os, json, random, re, math
from datetime import datetime, date, timedelta
from io import BytesIO

from flask import (Flask, request, jsonify, send_file,
                   render_template, session)
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# ── Optional heavy imports (graceful fallback) ────────────────────────────────
try:
    from gtts import gTTS
    GTTS_OK = True
except ImportError:
    GTTS_OK = False

try:
    from googletrans import Translator
    _translator = Translator()
    TRANS_OK = True
except Exception:
    TRANS_OK = False

try:
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.lib.pagesizes import A4
    PDF_OK = True
except ImportError:
    PDF_OK = False

try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
    OCR_OK = True
    # ── Windows: set path to installed Tesseract binary ──
    # Standard install path — adjust if you installed to a custom location:
    _tess_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        r'C:\Users\karfa\AppData\Local\Programs\Tesseract-OCR\tesseract.exe',
    ]
    import os as _os
    for _p in _tess_paths:
        if _os.path.isfile(_p):
            pytesseract.pytesseract.tesseract_cmd = _p
            break
    else:
        # Fallback: let pytesseract find it on PATH (works on Linux/Mac after apt/brew install)
        pass
except ImportError:
    try:
        from PIL import Image, ImageEnhance, ImageFilter
    except ImportError:
        pass
    OCR_OK = False

# ── App Setup ─────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR,'..','database','lexisense.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'lexisense_jistech2k26_ultra_secret_2024'
db = SQLAlchemy(app)
CORS(app, supports_credentials=True)

# ══════════════════════════════════════════════════════════════════════════════
#  DATABASE MODELS
# ══════════════════════════════════════════════════════════════════════════════
class User(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80),  unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name     = db.Column(db.String(100), default='')
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

class ReadingSession(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    words_read   = db.Column(db.Integer, default=0)
    duration_sec = db.Column(db.Integer, default=0)
    score        = db.Column(db.Float,   default=0.0)
    session_date = db.Column(db.Date,    default=date.today)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

class VocabWord(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    word         = db.Column(db.String(120), nullable=False)
    definition   = db.Column(db.Text, default='')
    times_looked = db.Column(db.Integer, default=1)
    mastered     = db.Column(db.Boolean, default=False)
    added_at     = db.Column(db.DateTime, default=datetime.utcnow)

class DyslexiaError(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    error_type = db.Column(db.String(60))
    error_word = db.Column(db.String(120))
    count      = db.Column(db.Integer, default=1)
    logged_at  = db.Column(db.DateTime, default=datetime.utcnow)

class UserSettings(db.Model):
    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    font_size      = db.Column(db.Integer, default=18)
    line_spacing   = db.Column(db.Float,   default=2.2)
    letter_spacing = db.Column(db.Float,   default=0.04)
    font_family    = db.Column(db.String(60), default='Lexend')
    color_overlay  = db.Column(db.String(40), default='none')
    word_highlight = db.Column(db.Boolean, default=True)
    focus_mode     = db.Column(db.Boolean, default=False)
    ruler_mode     = db.Column(db.Boolean, default=False)

def init_db():
    os.makedirs(os.path.join(BASE_DIR, '..', 'database'), exist_ok=True)
    with app.app_context():
        db.create_all()
    print("✅ Database ready — LexiSense AI v3.0")

# ══════════════════════════════════════════════════════════════════════════════
#  NLP DATA
# ══════════════════════════════════════════════════════════════════════════════
SIMPLIFY_EN = {
    "utilize":"use","demonstrate":"show","approximately":"about",
    "comprehend":"understand","subsequently":"then","therefore":"so",
    "sufficient":"enough","communicate":"talk","requirements":"needs",
    "assistance":"help","facilitate":"help","initial":"first",
    "terminate":"end","acquire":"get","construct":"build",
    "consequently":"as a result","in addition":"also","however":"but",
    "nevertheless":"still","furthermore":"also","moreover":"also",
    "elaborate":"explain","previously":"before","currently":"now",
    "immediately":"right away","ultimately":"finally","primarily":"mainly",
    "significantly":"greatly","frequently":"often","occasionally":"sometimes",
    "predominantly":"mostly","simultaneously":"at the same time",
    "accordingly":"so","alternatively":"or","particularly":"especially",
    "essentially":"basically","regardless":"no matter what",
    "implementation":"use","functionality":"feature","configuration":"setup",
    "authentication":"login","initiate":"start","commence":"begin",
    "conclude":"finish","modify":"change","obtain":"get",
    "provide":"give","require":"need","indicate":"show","maintain":"keep",
    "determine":"find out","establish":"set up","identify":"find",
    "generate":"make","distribute":"share","consume":"use",
    "numerous":"many","various":"different","complex":"hard",
    "difficult":"hard","challenging":"hard","straightforward":"simple",
    "comprehensive":"complete","adequate":"enough","utilize":"use",
}

SIMPLIFY_BN = {
    "ব্যবহার করুন":"ব্যবহার করো","প্রদর্শন করুন":"দেখাও",
    "বোঝা":"বোঝো","সহায়তা":"সাহায্য","তৎক্ষণাৎ":"এখনই",
    "পূর্ববর্তী":"আগের","বর্তমানে":"এখন","চূড়ান্তভাবে":"শেষে",
    "প্রাথমিকভাবে":"প্রথমে","উল্লেখযোগ্যভাবে":"অনেক বেশি",
}

DICTIONARY = {
    "dyslexia":{"phonetic":"/dɪsˈlɛksiə/","type":"noun","difficulty":"hard",
        "meaning":"A learning difference that primarily affects reading and spelling.",
        "simple":"A condition that makes reading and writing harder than usual.",
        "synonyms":["reading disorder"],"example":"Many creative people have dyslexia."},
    "cognition":{"phonetic":"/kɒɡˈnɪʃən/","type":"noun","difficulty":"hard",
        "meaning":"Mental action of acquiring knowledge through thought and experience.",
        "simple":"The way your brain thinks and learns.","synonyms":["thinking","reasoning"],
        "example":"Reading improves cognition."},
    "phonetics":{"phonetic":"/fəˈnɛtɪks/","type":"noun","difficulty":"medium",
        "meaning":"Study of sounds of human speech.",
        "simple":"Learning how words sound when spoken.","synonyms":["pronunciation"],
        "example":"Phonetics helps with reading."},
    "neurodiversity":{"phonetic":"/ˌnjʊərəʊdaɪˈvɜːsɪti/","type":"noun","difficulty":"hard",
        "meaning":"Range of differences in individual brain function and behavioural traits.",
        "simple":"The idea that brains work in many different ways.",
        "synonyms":["brain diversity"],"example":"Neurodiversity includes dyslexia and ADHD."},
    "literacy":{"phonetic":"/ˈlɪtərəsi/","type":"noun","difficulty":"medium",
        "meaning":"The ability to read and write.",
        "simple":"Being able to read and write.","synonyms":["reading ability"],
        "example":"Literacy is a fundamental skill."},
    "comprehension":{"phonetic":"/ˌkɒmprɪˈhɛnʃən/","type":"noun","difficulty":"medium",
        "meaning":"The ability to understand something.",
        "simple":"Being able to understand what you read.",
        "synonyms":["understanding","grasp"],"example":"Good comprehension helps in school."},
    "algorithm":{"phonetic":"/ˈalɡərɪðəm/","type":"noun","difficulty":"medium",
        "meaning":"A set of rules or steps used to solve a problem.",
        "simple":"A list of steps to solve a problem.",
        "synonyms":["procedure","method"],"example":"Search engines use algorithms."},
    "intelligence":{"phonetic":"/ɪnˈtɛlɪdʒəns/","type":"noun","difficulty":"medium",
        "meaning":"The ability to acquire and apply knowledge and skills.",
        "simple":"The ability to learn and solve problems.",
        "synonyms":["intellect","reasoning"],"example":"She showed great intelligence."},
    "language":{"phonetic":"/ˈlaŋɡwɪdʒ/","type":"noun","difficulty":"easy",
        "meaning":"A system of communication using words or signs.",
        "simple":"Words and sounds people use to talk to each other.",
        "synonyms":["tongue","speech"],"example":"Bengali is a beautiful language."},
    "reading":{"phonetic":"/ˈriːdɪŋ/","type":"noun","difficulty":"easy",
        "meaning":"The action of reading written or printed matter.",
        "simple":"Looking at words and understanding them.",
        "synonyms":["studying","perusing"],"example":"Reading every day is a good habit."},
}

LETTER_CHALLENGES = [
    {"word":"da_y","options":["b","d"],"answer":"d","full":"day","type":"letter_reversal"},
    {"word":"ra_bit","options":["b","d"],"answer":"b","full":"rabbit","type":"letter_reversal"},
    {"word":"___uiet","options":["p","q"],"answer":"q","full":"quiet","type":"letter_reversal"},
    {"word":"ma__","options":["p","q"],"answer":"p","full":"map","type":"letter_reversal"},
    {"word":"si__e","options":["b","d"],"answer":"d","full":"side","type":"letter_reversal"},
    {"word":"_og","options":["b","d"],"answer":"d","full":"dog","type":"letter_confusion"},
    {"word":"ca_","options":["b","p"],"answer":"p","full":"cap","type":"letter_reversal"},
    {"word":"_ell","options":["b","d"],"answer":"b","full":"bell","type":"letter_confusion"},
    {"word":"_oy","options":["b","d"],"answer":"b","full":"boy","type":"letter_confusion"},
    {"word":"_ig","options":["b","p"],"answer":"p","full":"pig","type":"letter_reversal"},
]

WORD_ORDER = [
    {"scrambled":["The","cat","sat","mat","on","the"],"correct":"The cat sat on the mat","hint":"A cat resting"},
    {"scrambled":["She","reads","every","books","day"],"correct":"She reads books every day","hint":"Reading habit"},
    {"scrambled":["sky","The","blue","is"],"correct":"The sky is blue","hint":"Color of sky"},
    {"scrambled":["like","I","to","read","books"],"correct":"I like to read books","hint":"Love for reading"},
    {"scrambled":["plays","He","guitar","the","well"],"correct":"He plays the guitar well","hint":"Music talent"},
    {"scrambled":["sun","The","every","rises","morning"],"correct":"The sun rises every morning","hint":"Daily event"},
]

PASSAGES = [
    {"text":"The quick brown fox jumps over the lazy dog near the river bank.","words":13},
    {"text":"Reading every day helps your brain stay sharp and makes you smarter over time.","words":14},
    {"text":"LexiSense AI was built to help people with dyslexia read better and learn faster.","words":15},
    {"text":"The sun rises in the east and sets in the west every single day without fail.","words":15},
]

SEARCH_KB = {
    "dyslexia":{"title":"What is Dyslexia?","icon":"🧠","type":"definition",
        "snippet":"Dyslexia is a learning difference affecting reading and spelling. It is neurological, not related to intelligence. About 15–20% of people have dyslexia. Many successful people — Einstein, da Vinci, Steve Jobs — had dyslexia."},
    "reading tips":{"title":"Reading Tips for Dyslexia","icon":"📚","type":"tips",
        "snippet":"Use larger fonts (18px+), more line spacing (2.0+), and dyslexia-friendly fonts like Lexend or OpenDyslexic. Reading rulers and yellow/blue color overlays reduce visual stress significantly."},
    "bengali":{"title":"Bengali Language Support","icon":"🇧🇩","type":"language",
        "snippet":"Bengali (বাংলা) is spoken by 230M+ people. LexiSense AI supports Bengali text simplification, Bengali OCR (pytesseract ben), Bengali TTS voice, and Bengali-to-English translation."},
    "phonics":{"title":"Phonics & Dyslexia","icon":"🔤","type":"education",
        "snippet":"Phonics teaches letter-sound relationships. It is one of the most effective methods for teaching people with dyslexia to read. Daily phonics practice for 10–15 minutes shows measurable improvement."},
    "ocr":{"title":"OCR — Image to Text","icon":"📷","type":"technology",
        "snippet":"OCR (Optical Character Recognition) converts images of text to editable text. LexiSense uses pytesseract with Bengali and English support. Install Tesseract for real OCR extraction."},
    "text to speech":{"title":"Text-to-Speech (TTS)","icon":"🔊","type":"technology",
        "snippet":"TTS converts written text to spoken audio. LexiSense supports 12+ voice languages including Bengali (bn-BD, bn-IN), Hindi, English, French and more through the Web Speech API."},
    "color overlay":{"title":"Color Overlays for Dyslexia","icon":"🎨","type":"tips",
        "snippet":"Colored overlays reduce visual stress. Yellow is most commonly recommended. Blue helps with contrast. Try different colors in Reading Settings to find what works best for you."},
    "font":{"title":"Dyslexia-Friendly Fonts","icon":"🔠","type":"tips",
        "snippet":"Lexend font was specifically designed to reduce visual stress for dyslexic readers. OpenDyslexic and Noto Sans Bengali are also effective. Avoid thin or decorative fonts."},
}

# ══════════════════════════════════════════════════════════════════════════════
#  AUTH ROUTES
# ══════════════════════════════════════════════════════════════════════════════
@app.route('/api/auth/signup', methods=['POST'])
def signup():
    d = request.json
    u, em, pw = d.get('username','').strip(), d.get('email','').strip(), d.get('password','')
    name = d.get('full_name','').strip()
    if not u or not em or not pw:
        return jsonify({"error":"All fields required"}), 400
    if User.query.filter_by(username=u).first():
        return jsonify({"error":"Username already taken"}), 409
    if User.query.filter_by(email=em).first():
        return jsonify({"error":"Email already registered"}), 409
    user = User(username=u, email=em, full_name=name,
                password_hash=generate_password_hash(pw))
    db.session.add(user)
    db.session.commit()
    session['uid'] = user.id
    return jsonify({"success":True,"user":{"id":user.id,"username":user.username,"full_name":user.full_name}})

@app.route('/api/auth/login', methods=['POST'])
def login():
    d = request.json
    user = User.query.filter_by(username=d.get('username','').strip()).first()
    if not user or not check_password_hash(user.password_hash, d.get('password','')):
        return jsonify({"error":"Invalid username or password"}), 401
    session['uid'] = user.id
    return jsonify({"success":True,"user":{"id":user.id,"username":user.username,"full_name":user.full_name}})

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.pop('uid', None)
    return jsonify({"success":True})

@app.route('/api/auth/me')
def me():
    uid = session.get('uid')
    if not uid:
        return jsonify({"logged_in":False})
    user = User.query.get(uid)
    return jsonify({"logged_in":bool(user),"user":{"id":user.id,"username":user.username,"full_name":user.full_name} if user else None})

# ══════════════════════════════════════════════════════════════════════════════
#  CORE ROUTES
# ══════════════════════════════════════════════════════════════════════════════
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify({"status":"ok","version":"3.0","ocr":OCR_OK,"tts":GTTS_OK,"translate":TRANS_OK})

# ── NLP / Simplify ────────────────────────────────────────────────────────────
@app.route('/api/simplify', methods=['POST'])
def simplify():
    data = request.json
    text = data.get('text','').strip()
    lang = data.get('lang','en')
    if not text:
        return jsonify({"error":"No text"}), 400
    smap = SIMPLIFY_BN if lang == 'bn' else SIMPLIFY_EN
    simplified, replaced = text, 0
    for orig, simple in smap.items():
        pattern = re.compile(re.escape(orig), re.IGNORECASE)
        new = pattern.sub(simple, simplified)
        if new != simplified: replaced += 1
        simplified = new
    words = text.split()
    sents = len(re.findall(r'[.!?]+', text)) or 1
    avg_s = len(words)/sents
    avg_y = sum(max(1,len(re.findall(r'[aeiouyAEIOUY]',w))) for w in words)/max(1,len(words))
    fk = max(0, min(100, 206.835 - 1.015*avg_s - 84.6*avg_y))
    grade = "Very Easy" if fk>90 else "Easy" if fk>70 else "Standard" if fk>50 else "Difficult" if fk>30 else "Very Difficult"
    return jsonify({"simplified":simplified,"original":text,"readability_score":round(fk,1),
        "grade":grade,"words_simplified":replaced,"word_count":len(words),"sentences":sents})

# ── Word Lookup ───────────────────────────────────────────────────────────────
@app.route('/api/lookup', methods=['POST'])
def lookup():
    word = request.json.get('word','').lower().strip()
    uid  = session.get('uid')
    if uid and word:
        ex = VocabWord.query.filter_by(user_id=uid, word=word).first()
        if ex: ex.times_looked += 1
        else:  db.session.add(VocabWord(user_id=uid, word=word))
        db.session.commit()
    if word in DICTIONARY:
        return jsonify({"word":word, **DICTIONARY[word]})
    return jsonify({"word":word,"phonetic":"","type":"word","difficulty":"unknown",
        "meaning":f"Definition for '{word}' not in local DB. Try online dictionary.",
        "simple":f"Look up '{word}' for more information.","synonyms":[],"example":""})

# ── OCR ───────────────────────────────────────────────────────────────────────
@app.route('/api/ocr', methods=['POST'])
def ocr():
    if 'image' not in request.files:
        return jsonify({"error":"No image"}), 400
    try:
        img = Image.open(request.files['image'].stream).convert('RGB')
        img = ImageEnhance.Contrast(img).enhance(1.5)
        img = img.filter(ImageFilter.SHARPEN)
        lang_param = request.form.get('lang','en')
        if OCR_OK:
            ocr_lang = 'ben+eng' if lang_param in ('bn','both') else 'eng'
            raw = pytesseract.image_to_string(img, lang=ocr_lang, config='--psm 6 --oem 3').strip()
        else:
            raw = "[OCR Demo] The quick brown fox jumps over the lazy dog. Install Tesseract for real OCR extraction from images."
        simplified = raw
        for orig, simple in SIMPLIFY_EN.items():
            simplified = re.sub(re.escape(orig), simple, simplified, flags=re.IGNORECASE)
        return jsonify({"actual":raw or "No text detected.","simplified":simplified or "No text detected.","ocr_real":OCR_OK})
    except Exception as e:
        return jsonify({"error":str(e),"actual":"OCR failed.","simplified":"OCR failed.","ocr_real":False}), 500

# ── Translation ───────────────────────────────────────────────────────────────
@app.route('/api/translate', methods=['POST'])
def translate():
    d      = request.json
    text   = d.get('text','').strip()
    target = d.get('target','bn')
    source = d.get('source','auto')
    if not text: return jsonify({"error":"No text"}), 400
    if TRANS_OK:
        try:
            result = _translator.translate(text, dest=target, src=source)
            return jsonify({"translated":result.text,"detected":result.src,"target":target})
        except Exception as e:
            return jsonify({"error":str(e),"translated":"Translation failed — check googletrans installation."}), 500
    demo = {"hello":"হ্যালো","world":"বিশ্ব","reading":"পড়া","help":"সাহায্য","good":"ভালো","thank you":"ধন্যবাদ"}
    translated = " ".join(demo.get(w.lower(), w) for w in text.split())
    return jsonify({"translated":translated,"detected":"en","target":target,"demo":True})

# ── TTS (Bengali MP3) ─────────────────────────────────────────────────────────
@app.route('/api/tts', methods=['POST'])
def tts():
    d    = request.json
    text = d.get('text','').strip()
    lang = d.get('lang','en')
    if not text: return jsonify({"error":"No text"}), 400
    if not GTTS_OK: return jsonify({"error":"gTTS not installed","cmd":"pip install gtts"}), 503
    try:
        buf = BytesIO()
        gTTS(text=text, lang=lang, slow=False).write_to_fp(buf)
        buf.seek(0)
        return send_file(buf, mimetype='audio/mpeg', as_attachment=True, download_name='lexisense_audio.mp3')
    except Exception as e:
        return jsonify({"error":str(e)}), 500

# ── Dyslexia Challenges ───────────────────────────────────────────────────────
@app.route('/api/dyslexia/challenge')
def dyslexia_challenge():
    ctype = request.args.get('type','letter')
    if ctype == 'word_order': return jsonify({"type":"word_order","challenge":random.choice(WORD_ORDER)})
    if ctype == 'speed':      return jsonify({"type":"speed","challenge":random.choice(PASSAGES)})
    return jsonify({"type":"letter","challenge":random.choice(LETTER_CHALLENGES)})

@app.route('/api/dyslexia/log-error', methods=['POST'])
def log_error():
    d     = request.json
    uid   = session.get('uid')
    etype = d.get('error_type','letter_reversal')
    eword = d.get('error_word','')
    ex = DyslexiaError.query.filter_by(user_id=uid, error_type=etype, error_word=eword).first()
    if ex:
        ex.count += 1
        db.session.commit()
        count = ex.count
    else:
        err = DyslexiaError(user_id=uid, error_type=etype, error_word=eword)
        db.session.add(err)
        db.session.commit()
        count = 1
    if count >= 5:
        return jsonify({"probability":"High","count":count,"threshold_reached":True,
            "message":"⚠️ Repetitive errors detected — High dyslexia probability.",
            "advice":"Use OpenDyslexic font, color overlays, and text-to-speech features."})
    return jsonify({"probability":"Low","count":count,"threshold_reached":False,
        "message":f"Error logged ({count}/5). Keep practising!"})

@app.route('/api/dyslexia/report')
def dyslexia_report():
    uid  = session.get('uid')
    logs = DyslexiaError.query.filter_by(user_id=uid).all() if uid else []
    total = sum(l.count for l in logs)
    high  = sum(1 for l in logs if l.count >= 5)
    risk  = "High" if high >= 2 else "Moderate" if total >= 3 else "Low"
    return jsonify({"risk_level":risk,"total_error_types":len(logs),
        "total_errors":total,"high_frequency_errors":high,
        "error_details":[{"type":l.error_type,"word":l.error_word,"count":l.count} for l in logs]})

# ── Analytics ─────────────────────────────────────────────────────────────────
@app.route('/api/analytics')
def analytics():
    uid       = session.get('uid')
    sessions  = ReadingSession.query.filter_by(user_id=uid).all() if uid else ReadingSession.query.all()
    vocab     = VocabWord.query.filter_by(user_id=uid).all() if uid else []
    dyslexia  = DyslexiaError.query.filter_by(user_id=uid).all() if uid else []
    total_w   = sum(s.words_read for s in sessions)
    total_s   = len(sessions)
    avg_score = round(sum(s.score for s in sessions)/max(1,total_s), 1)
    total_dur = sum(s.duration_sec for s in sessions)
    mastered  = sum(1 for v in vocab if v.mastered)
    today     = date.today()
    chart     = []
    for i in range(6,-1,-1):
        d   = today - timedelta(days=i)
        ds  = [s for s in sessions if s.session_date == d]
        chart.append({"date":d.strftime('%b %d'),"words":sum(s.words_read for s in ds),
            "score":round(sum(s.score for s in ds)/max(1,len(ds)),1)})
    streak, check = 0, today
    while True:
        ds = [s for s in sessions if s.session_date == check]
        if ds: streak += 1; check -= timedelta(days=1)
        else:  break
    terror = sum(l.count for l in dyslexia)
    high_e = sum(1 for l in dyslexia if l.count >= 5)
    risk   = "High" if high_e >= 2 else "Moderate" if terror >= 3 else "Low"
    return jsonify({"total_words_read":total_w,"total_sessions":total_s,"average_score":avg_score,
        "vocabulary_count":len(vocab),"mastered_words":mastered,"streak":streak,
        "total_duration_minutes":round(total_dur/60,1),"dyslexia_risk":risk,
        "total_errors":terror,"chart_data":chart})

# ── Vocabulary ────────────────────────────────────────────────────────────────
@app.route('/api/vocabulary')
def vocabulary():
    uid   = session.get('uid')
    words = VocabWord.query.filter_by(user_id=uid).order_by(VocabWord.times_looked.desc()).all() if uid else []
    return jsonify({"vocabulary":[{"word":w.word,"definition":w.definition,
        "times_looked_up":w.times_looked,"mastered":w.mastered} for w in words]})

@app.route('/api/vocabulary/master', methods=['POST'])
def master_word():
    uid  = session.get('uid')
    word = request.json.get('word','')
    if uid:
        v = VocabWord.query.filter_by(user_id=uid, word=word).first()
        if v: v.mastered = True; db.session.commit()
    return jsonify({"success":True})

# ── Session Log ───────────────────────────────────────────────────────────────
@app.route('/api/session/log', methods=['POST'])
def log_session():
    d   = request.json
    uid = session.get('uid')
    db.session.add(ReadingSession(user_id=uid, words_read=d.get('words_read',0),
        duration_sec=d.get('duration',0), score=d.get('score',75), session_date=date.today()))
    db.session.commit()
    return jsonify({"success":True})

# ── Readability ───────────────────────────────────────────────────────────────
@app.route('/api/readability', methods=['POST'])
def readability():
    text  = request.json.get('text','')
    words = text.split()
    if not words: return jsonify({"score":0,"grade":"N/A"})
    sents = len(re.findall(r'[.!?]+',text)) or 1
    avg_s = len(words)/sents
    avg_y = sum(max(1,len(re.findall(r'[aeiouyAEIOUY]',w))) for w in words)/len(words)
    fk    = max(0,min(100,206.835-1.015*avg_s-84.6*avg_y))
    grade = "Very Easy" if fk>90 else "Easy" if fk>70 else "Standard" if fk>50 else "Difficult" if fk>30 else "Very Difficult"
    return jsonify({"score":round(fk,1),"grade":grade,"word_count":len(words),"sentences":sents})

# ── Settings ──────────────────────────────────────────────────────────────────
@app.route('/api/settings', methods=['GET','POST'])
def settings():
    uid = session.get('uid')
    if request.method == 'POST':
        data = request.json
        if uid:
            s = UserSettings.query.filter_by(user_id=uid).first()
            if not s: s = UserSettings(user_id=uid); db.session.add(s)
            for k,v in data.items():
                if hasattr(s,k): setattr(s,k,v)
            db.session.commit()
        return jsonify({"success":True})
    if uid:
        s = UserSettings.query.filter_by(user_id=uid).first()
        if s:
            return jsonify({"font_size":s.font_size,"line_spacing":s.line_spacing,
                "letter_spacing":s.letter_spacing,"font_family":s.font_family,
                "color_overlay":s.color_overlay,"word_highlight":s.word_highlight,
                "focus_mode":s.focus_mode,"ruler_mode":s.ruler_mode})
    return jsonify({"font_size":18,"line_spacing":2.2,"letter_spacing":0.04,
        "font_family":"Lexend","color_overlay":"none","word_highlight":True,
        "focus_mode":False,"ruler_mode":False})

# ── Search ────────────────────────────────────────────────────────────────────
@app.route('/api/search', methods=['POST'])
def search():
    q       = request.json.get('query','').lower().strip()
    results = []
    for key, val in SEARCH_KB.items():
        if any(kw in q for kw in key.split()) or any(kw in key for kw in q.split()):
            results.append({**val,"query":key})
    if not results:
        results = [{"title":f'Search: "{q}"',"icon":"🔍","type":"generic",
            "snippet":f"No specific results for '{q}'. Try: dyslexia, reading tips, Bengali, phonics, OCR, color overlay, font.","query":q}]
    return jsonify({"results":results,"count":len(results),"query":q})

# ── Export ────────────────────────────────────────────────────────────────────
@app.route('/api/export/<fmt>', methods=['POST'])
def export(fmt):
    data = request.json
    text = data.get('text','No content.')
    lang = data.get('lang','en')
    buf  = BytesIO()
    if fmt == 'mp3' and GTTS_OK:
        gTTS(text=text, lang=lang).write_to_fp(buf); buf.seek(0)
        return send_file(buf, mimetype='audio/mpeg', as_attachment=True, download_name='LexiSense_Audio.mp3')
    if fmt == 'pdf' and PDF_OK:
        p = rl_canvas.Canvas(buf, pagesize=A4)
        p.setFont("Helvetica-Bold",18); p.drawString(60,800,"LexiSense AI — Export")
        p.setFont("Helvetica",11); y=770
        for line in text.split('\n'):
            for i in range(0, len(line)+90, 90):
                chunk = line[i:i+90]
                if chunk: p.drawString(60,y,chunk); y-=18
                if y<60: p.showPage(); y=800
        p.save(); buf.seek(0)
        return send_file(buf, mimetype='application/pdf', as_attachment=True, download_name='LexiSense_Export.pdf')
    return jsonify({"error":"Format unavailable or library missing"}), 400

# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    print("\n🧠 LexiSense AI Backend v3.0")
    print("📍 http://localhost:5000\n")
    app.run(debug=True, port=5000, host='0.0.0.0')
