import os
from PIL import Image
import numpy as np

def load_cnn(model_path):
    from tensorflow.keras.models import load_model
    if os.path.exists(model_path):
        return load_model(model_path)
    else:
        print("CNN model not found at", model_path)
        return None

def run_yolo_inference(image_path, yolo_weights):
    try:
        from ultralytics import YOLO
        model = YOLO(yolo_weights)
        results = model(image_path)
        boxes = []
        if len(results) > 0:
            for box in results[0].boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                boxes.append((int(x1), int(y1), int(x2), int(y2)))
        return boxes
    except:
        print("YOLO inference failed. Check ultralytics installation and weights.")
        return []

def crop_and_classify(image_path, boxes, cnn_model):
    img = Image.open(image_path).convert('RGB')
    results = []
    for box in boxes:
        x1,y1,x2,y2 = box
        crop = img.crop((x1,y1,x2,y2)).resize((224,224))
        arr = np.array(crop)/255.0
        arr = np.expand_dims(arr,0)
        if cnn_model:
            pred = cnn_model.predict(arr)
            cls = int(np.argmax(pred))
            conf = float(np.max(pred))
        else:
            cls, conf = None, None
        results.append({'box':box,'class':cls,'conf':conf})
    return results
