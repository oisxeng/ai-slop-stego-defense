# 📡 Covert Channel & Synthetic Media Detector (API)

This repository contains the backend API for the **Advanced Synthetic Media Steganalysis** tool. It is designed to detect hidden structures, decentralized data poisoning payloads, and covert channels within AI-generated content (synthetic media).

## 🧠 How it Works (Multi-Layer Steganalysis)
Unlike naive entropy detectors that trigger false positives on noisy smartphone photos, this engine uses a multi-layered approach relying on Python, NumPy, and SciPy:

1. **Global LSB Entropy:** Analyzes the Least Significant Bit (LSB) distribution across the entire image.
2. **Flat-Region Steganalysis:** Isolates areas where the image structure (MSB) is perfectly flat. Calculating entropy *only* in these regions drastically reduces false positives from natural sensor noise.
3. **Smart Payload Extraction:** Uses Regular Expressions (Regex) to scan the extracted LSB noise for readable ASCII structures, URLs, IP addresses, and Base64-encoded payloads.

## 🚀 Deployment
This API is built with **FastAPI** and is designed to be deployed as a microservice (e.g., on Render.com or Heroku). 

### Run Locally
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Start the server: `uvicorn api:app --reload`
4. The API will be available at `http://localhost:8000`.

## 🛡️ Frontend Interface
This backend is designed to be consumed by a lightweight, client-side frontend. You can find the live interface connecting to this API here: 
**(Insert your Netlify URL here!)**

---
*Developed as part of research into AI alignment, systemic risks, and cyber-physical security.*
