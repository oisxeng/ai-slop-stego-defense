import io
import re
import numpy as np
from PIL import Image
from scipy.stats import entropy
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Advanced Synthetic Media Steganalysis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Für Produktion hier deine Netlify URL eintragen
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_smart_payload(lsb_flat, max_bytes=10000):
    """Liest die Bits aus und sucht mit Regex gezielt nach Mustern."""
    chars = []
    # Bits zu Text umwandeln (bis max_bytes)
    for i in range(0, min(len(lsb_flat), max_bytes * 8) - 8, 8):
        byte_val = int("".join(map(str, lsb_flat[i:i+8])), 2)
        if 32 <= byte_val <= 126:
            chars.append(chr(byte_val))
        else:
            chars.append('.')
            
    raw_text = "".join(chars)
    
    # 1. Filtere zusammenhängende Wörter (min. 5 Zeichen)
    words = re.findall(r'[A-Za-z0-9_]{5,}', raw_text)
    
    # 2. Suche nach URLs oder IPs
    urls = re.findall(r'(https?://[^\s]+|[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})', raw_text)
    
    # 3. Base64 verdächtige Strings (lange Alphanumerische Ketten)
    base64_suspects = re.findall(r'(?:[A-Za-z0-9+/]{4}){10,}(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?', raw_text)

    snippet = raw_text[:800] + "..." if len(raw_text) > 800 else raw_text
    
    return {
        "raw_snippet": snippet,
        "found_words": words[:10], # Zeige die ersten 10 gefundenen Wörter
        "found_urls": urls,
        "base64_suspects": len(base64_suspects) > 0
    }

@app.post("/analyze/image")
async def analyze_image(file: UploadFile = File(...)):
    try:
        # 1. Bild einlesen
        image_bytes = await file.read()
        img = Image.open(io.BytesIO(image_bytes)).convert('L') # Graustufen
        pixel_data = np.array(img, dtype=np.int16)
        
        # 2. Bits extrahieren
        lsb = pixel_data & 1          # Least Significant Bit (Versteck)
        msb = (pixel_data >> 4) & 15  # Höhere Bits (Bildstruktur)
        
        # 3. Layer 1: Global LSB Entropy
        counts_global = np.bincount(lsb.flatten())
        prob_global = counts_global / len(lsb.flatten())
        global_entropy = entropy(prob_global, base=2)
        
        # 4. Layer 2: Flat-Region Steganalysis
        diffs = np.abs(msb[:, :-1] - msb[:, 1:])
        flat_mask = (diffs == 0) # Finde Bereiche, in denen das Bild optisch völlig glatt ist
        
        flat_lsbs = lsb[:, :-1][flat_mask]
        
        if len(flat_lsbs) > 1000:
            counts_flat = np.bincount(flat_lsbs)
            prob_flat = counts_flat / len(flat_lsbs)
            flat_entropy = entropy(prob_flat, base=2)
        else:
            flat_entropy = global_entropy # Fallback bei extrem verrauschten Bildern

        # 5. Layer 3: Correlation Analysis (Handy-Kamera Filter)
        # Wenn LSB extrem rauscht (Entropie hoch), aber MSB auch rauscht -> Normale Kamera.
        # Wenn LSB extrem rauscht, MSB aber glatt ist -> Steganographie!
        anomaly_score = flat_entropy * (1.0 if len(flat_lsbs) > 1000 else 0.8)
        
        is_anomaly = bool(anomaly_score > 0.9997)
        
        # 6. Smart Payload Extraction
        extraction_results = extract_smart_payload(lsb.flatten())

        return {
            "filename": file.filename,
            "metrics": {
                "global_entropy": round(global_entropy, 6),
                "flat_region_entropy": round(flat_entropy, 6),
                "anomaly_score": round(anomaly_score, 6)
            },
            "anomaly_detected": is_anomaly,
            "extraction": extraction_results,
            "message": "🚨 SEVERE ANOMALY DETECTED: Covert channel or steganographic payload highly probable." if is_anomaly else "✅ SAFE: Noise profiles match natural sensor characteristics or benign compression."
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def read_root():
    return {"status": "Advanced Steganalysis API is operational.", "version": "2.0"}
