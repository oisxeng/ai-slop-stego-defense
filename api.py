import io
import re
import base64
import numpy as np
from scipy.ndimage import convolve
from PIL import Image
from scipy.stats import entropy
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SOTA Synthetic Media Steganalysis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

def calculate_transition_rate(bit_array):
    if len(bit_array) < 2: return 0.0
    transitions = np.sum(bit_array[:-1] != bit_array[1:])
    return transitions / (len(bit_array) - 1)

def extract_smart_payload(lsb_flat, max_bytes=10000):
    chars = []
    for i in range(0, min(len(lsb_flat), max_bytes * 8) - 8, 8):
        byte_val = int("".join(map(str, lsb_flat[i:i+8])), 2)
        if 32 <= byte_val <= 126:
            chars.append(chr(byte_val))
        else:
            chars.append('.')
            
    raw_text = "".join(chars)
    words = re.findall(r'[A-Za-z0-9_]{5,}', raw_text)
    urls = re.findall(r'(https?://[^\s]+|[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})', raw_text)
    base64_suspects = re.findall(r'(?:[A-Za-z0-9+/]{4}){10,}(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?', raw_text)

    return {
        "raw_snippet": raw_text[:800] + "..." if len(raw_text) > 800 else raw_text,
        "found_words": words[:10],
        "found_urls": urls,
        "base64_suspects": len(base64_suspects) > 0
    }

def encode_image_to_base64(img_array):
    """Wandelt ein Numpy-Array (Noise Map) in ein Base64-Bild für das Frontend um."""
    img = Image.fromarray(img_array.astype(np.uint8))
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{img_str}"

@app.post("/analyze/image")
async def analyze_image(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        img_pil = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        pixel_data = np.array(img_pil, dtype=np.int16)
        
        # 1. Den Blau-Kanal isolieren (hier verstecken KIs bevorzugt Daten)
        blue_channel = pixel_data[:, :, 2]
        lsb_blue = blue_channel & 1
        
        # 2. STATE-OF-THE-ART: High-Pass Residual Filtering (Laplace Filter)
        # Wir löschen das Fotomotiv aus und isolieren nur harte Kanten/Rauschen
        laplace_kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
        msb_blue = (blue_channel >> 4) & 15
        residual = convolve(msb_blue.astype(float), laplace_kernel)
        
        # Flat Regions sind dort, wo das Residual (Kantenfilter) fast Null ist
        flat_mask = np.abs(residual) <= 1
        flat_lsb_blue = lsb_blue[flat_mask]
        
        # 3. Metriken berechnen
        lsb_blue_flat_all = lsb_blue.flatten()
        
        # Fallback, falls das Bild purer Zufall/Rauschen ohne glatte Flächen ist
        if len(flat_lsb_blue) < 2000:
            flat_lsb_blue = lsb_blue_flat_all

        counts_flat = np.bincount(flat_lsb_blue)
        prob_flat = counts_flat / len(flat_lsb_blue) if len(counts_flat) == 2 else [1.0]
        flat_entropy_blue = entropy(prob_flat, base=2) if len(counts_flat) == 2 else 0.0
        
        flat_trans_blue = calculate_transition_rate(flat_lsb_blue)
        
        # 4. Anomalie erkennen (Smartphone-Rauschen vs. KI-Code)
        trans_deviation = abs(0.5 - flat_trans_blue)
        is_anomaly = False
        if flat_entropy_blue > 0.99985 and trans_deviation < 0.003:
            is_anomaly = True

        # 5. Noise Map Visualisierung generieren
        # Wir machen die LSBs sichtbar (0 wird schwarz, 1 wird weiß: 255)
        noise_map_visual = (lsb_blue * 255).astype(np.uint8)
        base64_image = encode_image_to_base64(noise_map_visual)

        # 6. Payload Extraktion
        extraction_results = extract_smart_payload(lsb_blue_flat_all)

        return {
            "filename": file.filename,
            "metrics": {
                "flat_region_entropy": round(flat_entropy_blue, 6),
                "anomaly_score": round(flat_entropy_blue, 6),
                "blue_channel_transition_rate": round(flat_trans_blue, 6)
            },
            "anomaly_detected": is_anomaly,
            "noise_map_base64": base64_image,
            "extraction": extraction_results,
            "message": "🚨 SEVERE ANOMALY: Steganographic cryptographic payload detected in High-Pass residual." if is_anomaly else "✅ SAFE: Natural sensor photon noise detected. No steganography."
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def read_root():
    return {"status": "SOTA Steganalysis API is operational.", "version": "4.0"}
