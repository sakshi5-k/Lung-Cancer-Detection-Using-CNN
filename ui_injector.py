# ui_injector.py (NO REMINDERS VERSION — minimal uploader, login, quiz, dashboard)

import streamlit as st
from pathlib import Path
import json
import time
import importlib
import sys
import random
import base64
import hashlib
import os

# -----------------------
# Config
# -----------------------
BASE = Path(__file__).parent
STATIC = BASE / "static"
DATA_DIRS = [BASE / "data", STATIC, BASE]

CREDENTIALS = {"username": "admin", "password": "1234"}
QUIZ_QUESTION_COUNT = 10

BACKGROUND_URL = (
    "https://images.unsplash.com/photo-1526256262350-7da7584cf5eb"
    "?ixlib=rb-4.0.0&auto=format&fit=crop&w=1470&q=60"
)

DATASET_HASH_INDEX = BASE / "data" / "dataset_hashes.json"

(BASE / "uploads").mkdir(parents=True, exist_ok=True)

# -----------------------
# Safe rerun
# -----------------------
def safe_rerun():
    try:
        st.rerun()
    except Exception:
        try:
            st.experimental_rerun()
        except Exception:
            pass

# -----------------------
# CSS
# -----------------------
def inline_custom_css():
    css = f"""
    <style>
    .stApp {{
      background-image: url('{BACKGROUND_URL}');
      background-size: cover;
      background-position: center;
      background-attachment: fixed;
      background-color: rgba(3, 20, 25, 0.65);
      background-blend-mode: multiply;
    }}
    .dashboard-card {{
      background: rgba(12, 20, 25, 0.78);
      border-radius: 12px;
      padding: 18px;
      color: #e6f7f8;
      box-shadow: 0 6px 30px rgba(0,0,0,0.5);
    }}
    .card {{
      background: rgba(8,14,16,0.85);
      border-radius: 10px;
      padding: 12px;
      margin-bottom: 12px;
      color: #e6f7f8;
    }}
    .brand {{ color:#8ff0d8; font-weight:700; font-size:20px; }}
    img.quiz-img {{
      border-radius:8px; 
      max-width: 380px;
    }}
    </style>
    """
    # append static CSS
    static_css = ""
    if STATIC.exists():
        for p in sorted(STATIC.rglob("*.css")):
            try:
                static_css += "\n" + p.read_text(encoding="utf-8")
            except:
                pass

    st.markdown(css + static_css, unsafe_allow_html=True)

# -----------------------
# Image utilities
# -----------------------
def collect_images(limit=10):
    imgs = []
    for base in DATA_DIRS:
        if base.exists():
            for p in base.rglob("*"):
                if p.suffix.lower() in [".png",".jpg",".jpeg",".gif",".webp"]:
                    imgs.append(p)
                    if len(imgs) >= limit:
                        return imgs
    return imgs

def img_to_data_uri(path: Path):
    try:
        b = path.read_bytes()
        ext = path.suffix.lower().replace(".", "")
        return f"data:image/{ext};base64," + base64.b64encode(b).decode()
    except:
        return None

# -----------------------
# Dataset hashing
# -----------------------
def sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256()
    h.update(b)
    return h.hexdigest()

def build_dataset_hash_index(rebuild=False):
    if DATASET_HASH_INDEX.exists() and not rebuild:
        try:
            return json.loads(DATASET_HASH_INDEX.read_text())
        except:
            pass

    index = {}
    for base in DATA_DIRS:
        for p in base.rglob("*"):
            if p.suffix.lower() in [".png",".jpg",".jpeg",".gif",".webp"]:
                try:
                    index[p.name] = sha256_bytes(p.read_bytes())
                except:
                    pass
    DATASET_HASH_INDEX.parent.mkdir(parents=True, exist_ok=True)
    DATASET_HASH_INDEX.write_text(json.dumps(index, indent=2))
    return index

DATASET_HASHES = build_dataset_hash_index()
DATASET_HASH_SET = set(DATASET_HASHES.values())

def validate_upload_bytes(file_bytes: bytes) -> bool:
    return sha256_bytes(file_bytes) in DATASET_HASH_SET

# -----------------------
# QUIZ
# -----------------------
def make_quiz_questions():
    bank = [
        {"q":"Which scan is best for lung nodule detection?","options":["🩻 CT scan","🧲 MRI","🔊 Ultrasound","🦴 Knee X-ray"],"answer":0},
        {"q":"What does 'malignant' mean?","options":["Cancerous","Non-cancerous","Inflamed","Benign"],"answer":0},
        {"q":"A small round opacity in the lung is called ______.","options":["Coin lesion","Star lesion","Wave","Cube"],"answer":0},
        {"q":"Which habit increases lung cancer risk?","options":["Smoking","Salad","Exercise","Water"],"answer":0},
        {"q":"Common symptom:","options":["Persistent cough","Ear pain","Leg cramp","Sneezing"],"answer":0},
        {"q":"Next step for suspicious nodule:","options":["Biopsy/PET-CT","Ignore it","Antibiotics","Bone scan"],"answer":0},
        {"q":"CNN stands for:","options":["Convolutional Neural Network","Central Node Network","Channel Normal Node","Conditional Net"],"answer":0},
        {"q":"Which is benign?","options":["Hamartoma","Small cell carcinoma","Adenocarcinoma","Metastasis"],"answer":0},
        {"q":"Default Streamlit port:","options":["8501","5000","3000","8080"],"answer":0},
        {"q":"Purpose of crop_and_classify():","options":["Crop ROIs & classify","Run server","Zip files","Train YOLO"],"answer":0},
    ]

    imgs = collect_images(limit=4)
    if imgs:
        for i, idx in enumerate(random.sample(range(len(bank)), min(4, len(imgs)))):
            uri = img_to_data_uri(imgs[i])
            if uri:
                bank[idx]["image"] = uri

    return bank[:QUIZ_QUESTION_COUNT]

# -----------------------
# LOGIN
# -----------------------
def show_login():
    st.markdown("<div class='dashboard-card' style='max-width:600px;margin:auto;'>", unsafe_allow_html=True)
    st.markdown("## 🔐 Login", unsafe_allow_html=True)

    with st.form("login"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if u == CREDENTIALS["username"] and p == CREDENTIALS["password"]:
                st.session_state.logged_in = True
                safe_rerun()
            else:
                st.error("Invalid credentials")

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------
# Minimal protected uploader
# -----------------------
def show_protected_uploader():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    uploaded = st.file_uploader("", type=["png","jpg","jpeg","webp","gif"], label_visibility="collapsed")

    if uploaded:
        data = uploaded.read()
        if validate_upload_bytes(data):
            save_valid_upload(uploaded, data)
            st.session_state["upload_valid"] = True
        else:
            st.session_state["upload_valid"] = False

    st.session_state.setdefault("upload_valid", True)
    st.markdown("</div>", unsafe_allow_html=True)

def save_valid_upload(uploaded_file, data_bytes):
    outp = (BASE / "uploads" / uploaded_file.name)
    try:
        outp.write_bytes(data_bytes)
        st.session_state["uploaded_valid_path"] = str(outp)
    except:
        st.session_state["uploaded_valid_path"] = None

# -----------------------
# QUIZ UI
# -----------------------
def show_quiz():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 🧠 Knowledge Quiz")

    if "quiz_state" not in st.session_state:
        st.session_state.quiz_state = {
            "questions": make_quiz_questions(),
            "current": 0,
            "answers": {},
            "finished": False,
            "score": None
        }

    qs = st.session_state.quiz_state["questions"]
    cur = st.session_state.quiz_state["current"]
    q = qs[cur]

    st.write(f"**Question {cur+1}/{len(qs)}**")
    st.write("### " + q["q"])

    if "image" in q:
        st.markdown(f"<img class='quiz-img' src='{q['image']}'>", unsafe_allow_html=True)

    prev = st.session_state.quiz_state["answers"].get(cur, 0)
    choice = st.radio(" ", q["options"], index=prev, key=f"q{cur}", label_visibility="collapsed")
    st.session_state.quiz_state["answers"][cur] = q["options"].index(choice)

    col1, col2, col3 = st.columns([1,1,3])
    if col1.button("Prev") and cur > 0:
        st.session_state.quiz_state["current"] -= 1
        safe_rerun()

    if col2.button("Next") and cur < len(qs)-1:
        st.session_state.quiz_state["current"] += 1
        safe_rerun()

    if col3.button("Finish Quiz"):
        ans = st.session_state.quiz_state["answers"]
        score = sum(1 for i, qq in enumerate(qs) if ans.get(i) == qq["answer"])
        st.session_state.quiz_state["finished"] = True
        st.session_state.quiz_state["score"] = score
        safe_rerun()

    if st.session_state.quiz_state["finished"]:
        sc = st.session_state.quiz_state["score"]
        st.write(f"### 🏆 Score: {sc}/{len(qs)} ({int(sc/len(qs)*100)}%)")
        if st.button("Retake Quiz"):
            st.session_state.quiz_state = {
                "questions": make_quiz_questions(),
                "current": 0,
                "answers": {},
                "finished": False,
                "score": None
            }
            safe_rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------
# Dashboard (NO REMINDERS)
# -----------------------
def run_dashboard():
    st.set_page_config(page_title="Lung Dashboard", layout="wide")
    inline_custom_css()

    st.markdown(
        "<div class='dashboard-card'><span class='brand'>🫁 LUNG AI</span> — CT Detection</div>",
        unsafe_allow_html=True,
    )

    left, _ = st.columns([3,1])  # sidebar removed (no reminders)

    with left:
        st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)

        show_protected_uploader()

        if not st.session_state.get("upload_valid", True):
            st.error("⚠️ Upload invalid — prediction UI disabled.")
        else:
            try:
                if "app" in sys.modules:
                    importlib.reload(sys.modules["app"])
                else:
                    import app
            except Exception as e:
                st.error("Failed to load prediction app.")
                st.exception(e)

        st.markdown("</div>", unsafe_allow_html=True)

        show_quiz()

# -----------------------
# MAIN
# -----------------------
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        show_login()
    else:
        run_dashboard()

if __name__ == "__main__":
    main()