"""Test vision model in isolation"""
import cv2
import requests
import json
import base64
from config import OLLAMA_BASE_URL, OLLAMA_MODEL

# Capture a frame
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
cap.release()

if not ret:
    print("❌ Could not capture frame")
    exit(1)

# Save temp image
cv2.imwrite("test_frame.jpg", frame)

# Encode image
with open("test_frame.jpg", "rb") as f:
    img_bytes = f.read()
    img_b64 = base64.b64encode(img_bytes).decode('utf-8')

# Test vision model
print(f"🧪 Testing {OLLAMA_MODEL}...")
print(f"📡 Using {OLLAMA_BASE_URL}")

system_prompt = "Describe what you see. Be direct and natural. No poetry."
user_prompt = "What do I see right now?"

payload = {
    "model": OLLAMA_MODEL,
    "messages": [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_prompt,
            "images": [img_b64]
        }
    ],
    "stream": False,
    "options": {
        "temperature": 0.7,
        "num_predict": 100
    }
}

try:
    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/chat",
        json=payload,
        timeout=60
    )
    
    if response.status_code == 200:
        result = response.json()
        vision_output = result['message']['content'].strip()
        print(f"\n✅ Vision model output:\n{vision_output}\n")
    else:
        print(f"❌ Error {response.status_code}: {response.text}")
        
except Exception as e:
    print(f"❌ Exception: {e}")
