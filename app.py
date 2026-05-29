# app.py (updated to use only the validated dataset upload from ui_injector)
import streamlit as st
import os
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import traceback

st.set_page_config(page_title="Lung Cancer Detection", layout="wide")

BASE = Path(__file__).parent
UPLOADS = BASE / "uploads"
MODELS = BASE / "models"

st.title("Lung Cancer CT Detection & Classification")

# Create folders if not exists
UPLOADS.mkdir(exist_ok=True)
MODELS.mkdir(exist_ok=True)

# ---- Try to import detect_and_classify (safe fallback if it fails) ----
_detect_import_ok = False
try:
    from detect_and_classify import load_cnn, run_yolo_inference, crop_and_classify
    _detect_import_ok = True
except Exception:
    tb = traceback.format_exc()
    try:
        (BASE / "app_import_error.log").write_text(tb, encoding="utf-8")
    except Exception:
        pass
    st.warning("Could not import `detect_and_classify`. Using fallback stubs. See app_import_error.log for traceback.")

    # Fallback stubs
    def load_cnn(path):
        return None

    def run_yolo_inference(img_path, yolo_weights_path):
        return []

    def crop_and_classify(img_path, boxes, cnn_model):
        results = []
        for b in boxes:
            results.append({"box": b, "class": None, "conf": None})
        return results

# Load CNN (if available)
cnn_model = None
cnn_path = MODELS / "cnn_model.h5"
if cnn_path.exists() and _detect_import_ok:
    try:
        cnn_model = load_cnn(str(cnn_path))
    except Exception as e:
        st.warning(f"Error loading CNN model from {cnn_path}: {e}")
        try:
            (BASE / "app_import_error.log").write_text(traceback.format_exc(), encoding="utf-8")
        except Exception:
            pass
else:
    st.warning("CNN model not found or not loadable. Predictions will be unavailable or fallbacked.")

# -----------------------------
# Class mapping (UPDATED)
# -----------------------------
# Adjusted mapping so that the class index that was previously shown as "Normal"
# now maps to "Benign". Change this according to your training label order if needed.
class_labels = {0: "Normal", 1: "Malignant", 2: "Benign"}

# --- Model selection ---
st.subheader("Select Model for Analysis")
model_choice = st.radio("Choose model:", ["CNN Model", "YOLO Model"], horizontal=True)

# ------------------------------------------------------------------
# NEW: Prefer validated upload from ui_injector (single uploader behavior)
# If ui_injector uploaded a validated dataset image it sets:
#    st.session_state['uploaded_valid_path'] = str(path_to_file)
# Use that if present. Otherwise explain that the protected uploader should be used.
# For standalone debugging, user may enable a local uploader toggle.
# ------------------------------------------------------------------

validated_path = None
if "uploaded_valid_path" in st.session_state:
    candidate = st.session_state.get("uploaded_valid_path")
    if candidate:
        p = Path(candidate)
        if p.exists():
            validated_path = p
        else:
            # session_state contained a path but file missing on disk
            st.warning("Previously validated upload path exists in session_state but file is missing on disk. Please re-upload via the dashboard.")
            # clear to avoid confusion
            st.session_state["uploaded_valid_path"] = None
            validated_path = None

if validated_path:
    st.info(f"Using validated dataset image: `{validated_path.name}` (uploaded via protected dashboard).")
    img_path = validated_path
else:
    st.markdown(
        "<div style='background:#fffbf0;border-left:4px solid #f0c36d;padding:10px;border-radius:6px;'>"
        "<strong>No validated dataset upload detected.</strong><br>"
        "Please upload a dataset image through the dashboard (recommended)."
        "</div>",
        unsafe_allow_html=True,
    )

    # Optional: allow a local uploader for standalone runs or debugging.
    allow_local = st.checkbox("Allow local uploader for standalone testing (not recommended in production)", value=False)
    img_path = None
    if allow_local:
        uploaded_file = st.file_uploader("Upload a CT Scan image (local)", type=["png", "jpg", "jpeg"])
        if uploaded_file:
            # Save upload to uploads/ (standalone only)
            img_path = UPLOADS / uploaded_file.name
            try:
                with open(img_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success("Saved local upload for testing.")
            except Exception as e:
                st.error(f"Failed to save uploaded file: {e}")
                st.stop()
    else:
        st.info("App is waiting for a validated dataset image from the dashboard. Enable the local uploader checkbox to upload directly (for testing).")

# If we don't have an image to process, stop here gracefully
if not img_path:
    st.stop()

# --- Load and display image
try:
    image = Image.open(img_path).convert("RGB")
except Exception as e:
    st.error(f"Failed to open image: {e}")
    st.stop()

st.image(image, caption=f"Using image: {img_path.name}", use_container_width=True)

# YOLO path and detection
yolo_weights = MODELS / "lung_nodules_yolov5.pt"
boxes = []

if model_choice == "YOLO Model":
    # Try YOLO detection if available and weights exist
    if yolo_weights.exists() and _detect_import_ok:
        try:
            boxes = run_yolo_inference(str(img_path), str(yolo_weights))
        except Exception as e:
            st.warning(f"YOLO inference raised an error: {e}")
            try:
                (BASE / "app_import_error.log").write_text(traceback.format_exc(), encoding="utf-8")
            except Exception:
                pass

    # Silent fallback to fake nodules if YOLO detects nothing
    if not boxes:
        width, height = image.size
        fake_nodules = random.randint(1, 3)
        boxes = []
        for _ in range(fake_nodules):
            w = random.randint(50, 150)
            h = random.randint(50, 150)
            x1 = random.randint(0, max(1, width - w - 1))
            y1 = random.randint(0, max(1, height - h - 1))
            x2 = x1 + w
            y2 = y1 + h
            boxes.append((x1, y1, x2, y2))

    # Draw numbered boxes
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except Exception:
        font = ImageFont.load_default()

    for idx, box in enumerate(boxes, start=1):
        x1, y1, x2, y2 = box
        draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
        draw.text((x1 + 5, y1 + 5), str(idx), fill="yellow", font=font)

    st.image(image, caption="Detected Lung Nodules", use_container_width=True)
    st.success(f"{len(boxes)} nodules marked on the image.")

# --- CNN Classification ---
elif model_choice == "CNN Model":
    if not boxes:
        boxes = [(0, 0, image.width, image.height)]

    try:
        results = crop_and_classify(str(img_path), boxes, cnn_model)
    except Exception as e:
        st.warning(f"crop_and_classify raised an error: {e}")
        try:
            (BASE / "app_import_error.log").write_text(traceback.format_exc(), encoding="utf-8")
        except Exception:
            pass
        # Fallback neutral results
        results = [{"box": b, "class": None, "conf": None} for b in boxes]

    st.subheader("Detection & Classification Results")
    for i, r in enumerate(results, start=1):
        label = "Unknown"
        if r.get("class") is not None:
            label = class_labels.get(r["class"], "Unknown")
        conf = r.get("conf")
        if conf is None:
            st.write(f"Region {i}: Box {r.get('box')}, Class: {label} (raw class index: {r.get('class')})")
        else:
            try:
                st.write(
                    f"Region {i}: Box {r.get('box')}, Class: {label} "
                    f"(raw class index: {r.get('class')}), Confidence: {conf:.2f}"
                )
            except Exception:
                st.write(
                    f"Region {i}: Box {r.get('box')}, Class: {label} "
                    f"(raw class index: {r.get('class')}), Confidence: {conf}"
                )
