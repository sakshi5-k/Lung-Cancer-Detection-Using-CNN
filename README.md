# 🫁 Lung Cancer Detection System
### Deep Learning-Based Medical Image Classification using CNN

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-FF6F00?style=flat&logo=tensorflow&logoColor=white)
![Keras](https://img.shields.io/badge/Keras-D00000?style=flat&logo=keras&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=flat&logo=opencv&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

---

## 📌 Overview

A deep learning system that classifies lung CT scan images to detect signs of cancer using **Convolutional Neural Networks (CNN)**. This project applies computer vision and medical imaging techniques to assist in early-stage lung cancer diagnosis.

> **Domain:** Healthcare AI · Medical Imaging · Computer Vision  
> **Tech Stack:** Python · TensorFlow · Keras · OpenCV · NumPy · Pandas · Matplotlib

---

## 🎯 Problem Statement

Lung cancer is one of the leading causes of cancer-related deaths worldwide. Early detection significantly improves survival rates, but manual analysis of CT scans is time-consuming and prone to human error. This system automates the classification process using deep learning.

---

## 🧠 Model Architecture

```
Input Image (CT Scan)
        │
        ▼
┌─────────────────────┐
│  Convolutional Layer │  ← Feature extraction
│  + ReLU Activation  │
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│    MaxPooling Layer  │  ← Dimensionality reduction
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│   Dropout Layer      │  ← Prevent overfitting
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│   Fully Connected    │  ← Classification
│   + Softmax Output   │
└─────────────────────┘
        │
        ▼
  Output: Cancerous / Non-Cancerous
```

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| **Python** | Core programming language |
| **TensorFlow / Keras** | Model building & training |
| **OpenCV** | Image preprocessing & augmentation |
| **NumPy** | Array operations & data handling |
| **Pandas** | Dataset management & analysis |
| **Matplotlib** | Training visualization & result plots |

---

## 📁 Project Structure

```
lung-cancer-detection/
│
├── dataset/
│   ├── train/
│   │   ├── cancerous/
│   │   └── non_cancerous/
│   └── test/
│       ├── cancerous/
│       └── non_cancerous/
│
├── notebooks/
│   └── exploration.ipynb       # EDA and visualization
│
├── src/
│   ├── preprocess.py           # Image preprocessing with OpenCV
│   ├── model.py                # CNN architecture (Keras)
│   ├── train.py                # Model training script
│   └── predict.py              # Run predictions on new images
│
├── outputs/
│   ├── model.h5                # Saved trained model
│   └── plots/                  # Training accuracy/loss graphs
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/lung-cancer-detection.git
cd lung-cancer-detection
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run training
```bash
python src/train.py
```

### 4. Run prediction on a new image
```bash
python src/predict.py --image path/to/ct_scan.jpg
```

---

## 📊 Results

| Metric | Score |
|--------|-------|
| Training Accuracy | __%  |
| Validation Accuracy | __%  |
| Test Accuracy | __%  |
| Loss | __ |

> 📌 _Fill in your actual scores after training. Even 70%+ is worth showing — explain what you learned from the results._

---

## 📈 Training Visualization

> _(Add your Matplotlib accuracy/loss plot images here)_

```python
# Sample plot code used
import matplotlib.pyplot as plt

plt.plot(history.history['accuracy'], label='Train Accuracy')
plt.plot(history.history['val_accuracy'], label='Val Accuracy')
plt.title('Model Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()
plt.savefig('outputs/plots/accuracy_plot.png')
```

---

## 🔍 Key Learnings

- Applied **image augmentation** (rotation, flipping, zoom) using OpenCV to handle limited medical datasets
- Understood the importance of **dropout layers** in reducing overfitting on small datasets
- Learned how **class imbalance** affects medical AI models and techniques to handle it
- Gained hands-on experience translating a real-world healthcare problem into a deep learning pipeline

---

## 🚀 Future Improvements

- [ ] Integrate with a web interface using Streamlit or Flask
- [ ] Experiment with transfer learning (ResNet, VGG16) for higher accuracy
- [ ] Add Grad-CAM visualization to highlight cancer regions in CT scans
- [ ] Deploy as an API for real-time predictions

---

## 👩‍💻 Author

**Sakshi K**  
BE Computer Science, VCET Puttur (2027)  
📧 sakshikekunnaya5@gmail.com  
🔗 [LinkedIn](https://www.linkedin.com/in/sakshik-8b30442b7)

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

> ⭐ If you found this project useful or interesting, consider giving it a star!
