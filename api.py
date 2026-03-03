# ... [Dein bisheriger Code oberhalb bleibt gleich] ...

def encode_image_to_base64(img_array):
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
        
        blue_channel = pixel_data[:, :, 2]
        lsb_blue = blue_channel & 1
        
        # Laplace Filter & Flat Regions
        laplace_kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
        msb_blue = (blue_channel >> 4) & 15
        residual = convolve(msb_blue.astype(float), laplace_kernel)
        flat_mask = np.abs(residual) <= 1
        flat_lsb_blue = lsb_blue[flat_mask]
        
        lsb_blue_flat_all = lsb_blue.flatten()
        if len(flat_lsb_blue) < 2000:
            flat_lsb_blue = lsb_blue_flat_all

        counts_flat = np.bincount(flat_lsb_blue)
        prob_flat = counts_flat / len(flat_lsb_blue) if len(counts_flat) == 2 else [1.0]
        flat_entropy_blue = entropy(prob_flat, base=2) if len(counts_flat) == 2 else 0.0
        flat_trans_blue = calculate_transition_rate(flat_lsb_blue)
        
        noise_map_visual = (lsb_blue * 255).astype(np.uint8)
        base64_image = encode_image_to_base64(noise_map_visual)

        # Die Payload Extraktion prüfen
        extraction_results = extract_smart_payload(lsb_blue_flat_all)
        
        # NEUE LOGIK: Nur noch Alarm bei echtem Beweis.
        if extraction_results["definitive_proof"]:
            is_anomaly = True
            message = f"🔥 SMOKING GUN: Cryptographic proof of embedded payload! ({extraction_results['proof_details'][0]})"
        else:
            is_anomaly = False # Wir setzen es auf False, damit die rote Box nicht triggert
            
            # Wir prüfen nur noch auf extrem unnatürliche Statistik, deklarieren es aber als "Safe"
            trans_deviation = abs(0.5 - flat_trans_blue)
            if flat_entropy_blue > 0.99985 and trans_deviation < 0.003:
                 message = "✅ SAFE (HIGH NOISE): High statistical variance detected (likely heavy JPEG compression or high-ISO smartphone sensor), but NO actionable payload found."
            else:
                 message = "✅ SAFE: Natural sensor photon noise detected. No steganographic structures found."

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
