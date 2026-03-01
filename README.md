# AI Slop Steganography Defense Toolkit 🛡️

This repository contains the multimodal proof-of-concept codebase for the research paper: 
**"AI Slop as a Covert Medium: Hidden Structures for Distributed AI Memory, Communication, and Potential Rogue Behaviors"** by Michael Hackl & Leander Kühnel (2026).

## Abstract
As AI-generated "slop" floods the internet, our research hypothesizes that this data can act as a covert communication channel and a vector for decentralized data poisoning in open-source models (the "Patient Zero" dynamic). This toolkit demonstrates practical mitigation strategies for both text and multimodal content (images) as outlined in Section 6.1 of our paper.

## Features (Proof of Concept)
1. **Text Entropy Analysis & Semantic Perturbation**: Scans text for abnormal information density and intelligently swaps synonyms to destroy fragile steganographic token-encodings.
2. **Multimodal Image Perturbation**: Applies imperceptible Gaussian blurring and JPEG compression to AI-generated images, effectively destroying hidden payloads encoded in pixel noise (e.g., LSB steganography).

## Getting Started
```bash
# Clone the repository
git clone [https://github.com/oisxeng/ai-slop-stego-defense.git](https://github.com/oisxeng/ai-slop-stego-defense.git)

# Install requirements
pip install -r requirements.txt

# Run Text Defense
python slop_defense_toolkit.py --text "Suspicious AI generated text goes here."

# Run Image Defense (Multimodal)
python slop_defense_toolkit.py --image "path/to/suspect_image.png"
