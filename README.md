# 📡 Covert Channel & Synthetic Media Detector

**An open-source forensic toolkit to detect hidden steganographic payloads and AI-to-AI communication in synthetic media.**

## 🌐 Live Demo
You can test the detector live here: [https://covert-channel-detector.netlify.app/](https://covert-channel-detector.netlify.app/)

## 🧠 The Mission
As AI systems become increasingly multimodal, the risk of "Covert Infrastructure" grows. This project explores how synthetic media can be used for decentralized data poisoning or unauthorized communication between autonomous agents. We provide a pragmatic, systems-level tool to detect these systemic risks before they cascade into cyber-physical domains.

## 🔬 Technical Features
- **RGB Channel Isolation:** Focused analysis on the Blue channel (the most common hiding spot).
- **Laplacian Residual Filtering:** Removing visual "motives" to isolate pure pixel noise.
- **Statistical Heuristics:** Measuring Shannon Entropy and Spatial Transition Rates (Bit-flips).
- **Semantic Extraction:** Real-time parsing for verified JSON, Base64 strings, and Magic Bytes (File Carving).

## 🛠️ Installation & Deployment
This backend is built with **FastAPI** and designed for lightweight deployment (e.g., Render.com).

1. Clone the repo.
2. Install dependencies: `pip install -r requirements.txt`
3. Run the API: `uvicorn api:app --host 0.0.0.0 --port 8000`

## 🤝 Collaborative Research (Call for Contribution)
We are in the early stages of this research and actively seeking:
- **Feedback on Heuristics:** Are there better ways to filter smartphone sensor noise?
- **New Extraction Patterns:** Help us expand the "Smoking Gun" detection (e.g., new file signatures).
- **Dataset Samples:** If you find confirmed cases of AI-generated steganography, please share them!

**Please use the [Issues](https://github.com/oisxeng/covert-channel-defense/issues) section for suggestions, ideas, or to report anomalies!**

---
*Developed by Michael Hackl – Entrepreneur, Inventor, and AI Safety Researcher.*
