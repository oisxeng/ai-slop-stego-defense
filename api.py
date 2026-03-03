import io
import re
import json
import base64
import numpy as np
from scipy.ndimage import convolve
from PIL import Image
from scipy.stats import entropy
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

# 1. Die App-Instanz definieren (DAS FEHLTE!)
app = FastAPI(title="SOTA Steganalysis API")

# 2. CORS-Einstellungen (Wichtig für die Verbindung zu Netlify)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

def calculate_transition_rate(bit_array):
    """Berechnet die Bit-Wechsel-Rate."""
    if len(bit_array) < 2: return 0.0
    transitions = np.sum(bit_array[:-1] != bit_array[1:])
    return transitions / (len(bit_array) - 1)

def extract_smart_payload(lsb_flat, max_bytes=20000):
    """Sucht nach zweifelsfreien Beweisen (Magic Bytes, JSON, Base64)."""
    byte_array = bytearray()
    for i in range(0, min(len(lsb_flat), max_bytes * 8) - 8, 8):
        try:
            byte_val = int("".join(map(str, lsb_flat[i:i+8])), 2)
            byte_array.append(byte_val)
        except:
            break
        
    raw_text = "".join([chr(b) if 32 <= b <= 126 else '.' for b in byte_array])
    
    definitive_proof = False
    proof_details = []

    # BEWEIS 1: Magic Bytes
    magic_signatures = {
        b'%PDF-': "PDF Document",
        b'PK\x03\x04': "ZIP Archive",
        b'\x89PNG\r\n\x1a\n': "PNG Image",
        b'\xFF\xD8\xFF': "JPEG Image"
    }
    for sig, name in magic_signatures.items():
        if sig in byte_array:
            definitive_proof = True
            proof_details.append(f"Magic Bytes detected: Hidden {name} found!")

    # BEWEIS 2: Base64 Validation
    base64_suspects = re.findall(r'(?:[A-Za-z0-9+/]{4}){10,}(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?', raw_text)
    for b64 in base64_suspects:
        try:
            decoded_bytes = base64.b64decode(b64)
            decoded_text = decoded_bytes.decode('utf-8')
            if len(decoded_text) > 5 and decoded_text.isprintable():
                definitive_proof = True
                proof_details.append(f"Verified Base64 Payload: {decoded_text[:50]}...")
        except:
            pass

    # BEWEIS 3: JSON Parsing
    json_candidates = re.findall(r'\{.*?\}', raw_text)
    for jc in json_candidates:
        try:
            parsed = json.loads(jc.replace('.', ''))
            if len(parsed.keys()) > 0:
                definitive_proof = True
                proof_details.append(f"Verified JSON Data: {str(parsed)[:50]}")
        except:
            pass

    words = re.findall(r'[A-Za-z0-9_]{6,}', raw_text)
    urls = re.findall(r'(https?://[^\s]+|[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})', raw_text)

    return {
        "raw_snippet": raw_text[:800] + "..." if len(raw_text) > 800 else raw_text,
        "found_words": words[:15],
        "found_urls": urls,
        "definitive_proof": definitive_proof,
        "proof_details": proof_details
    }

def encode_image_to_base64(img_array):
    img = Image.fromarray(img_array.astype(np.uint8))
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return f"data:image/png;base64,{base64.b64encode(buffered.getvalue()).decode('utf-8')}"

@app.post("/analyze/image")
async def analyze_image(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        img_pil = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        pixel_data = np.array(img_pil, dtype=np.int16)
        
        blue_channel = pixel_data[:, :, 2]
        lsb_blue = blue_channel & 1
        
        # Laplace Filter für Residual-Analyse
        laplace_kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
        msb_blue = (blue_channel >> 4) & 15
        residual = convolve(msb_blue.astype(float), laplace_kernel)
        flat_mask = np.abs(residual) <= 1
        
        lsb_blue_flat_all = lsb_blue.flatten()
        flat_lsb_blue = lsb_blue[flat_mask] if np.any(flat_mask) else lsb_blue_flat_all
        if len(flat_lsb_blue) < 2000: flat_lsb_blue = lsb_blue_flat_all

        counts_flat = np.bincount(flat_lsb_blue.astype(int))
        prob_flat = counts_flat / len(flat_lsb_blue) if len(counts_flat) == 2 else [1.0]
        flat_entropy_blue = entropy(prob_flat, base=2) if len(counts_flat) == 2 else 0.0
        flat_trans_blue = calculate_transition_rate(flat_lsb_blue)
        
        noise_map_visual = (lsb_blue * 255).astype(np.uint8)
        base64_image = encode_image_to_base64(noise_map_visual)

        extraction_results = extract_smart_payload(lsb_blue_flat_all)
        
        if extraction_results["definitive_proof"]:
            is_anomaly = True
            message = f"🔥 SMOKING GUN: Cryptographic proof of embedded payload! ({extraction_results['proof_details'][0]})"
        else:
            is_anomaly = False
            trans_deviation = abs(0.5 - flat_trans_blue)
            if flat_entropy_blue > 0.99985 and trans_deviation < 0.003:
                 message = "✅ SAFE (HIGH NOISE): High variance detected (likely compression/sensor noise), but NO verified payload found."
            else:
                 message = "✅ SAFE: Natural noise profile. No steganographic structures found."

        return {
            "filename": file.filename,
            "metrics": {
                "flat_region_entropy": round(flat_entropy_blue, 6),
                "anomaly_score": round(flat_entropy_blue, 6),
                "blue_channel_transition_rate": round(flat_trans_blue, 6)
            },
            "anomaly_detected": is_anomaly,
            "definitive_proof": extraction_results["definitive_proof"], 
            "noise_map_base64": base64_image,
            "extraction": extraction_results,
            "message": message
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def read_root():
    return {"status": "SOTA Steganalysis API (Smoking Gun Edition) is operational.", "version": "4.1"}
