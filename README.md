# AI Slop Steganography Defense Toolkit 🛡️

This repository contains the proof-of-concept codebase for the research paper: 
**"AI Slop as a Covert Medium: Hidden Structures for Distributed AI Memory, Communication, and Potential Rogue Behaviors"** by Michael Hackl & Leander Kühnel (2026).

## Abstract
As AI-generated "slop" floods the internet, our research hypothesizes that this data can act as a covert communication channel (steganography) and a vector for decentralized data poisoning in open-source models (the "Patient Zero" dynamic). This toolkit demonstrates practical mitigation strategies outlined in Section 6.1 of our paper.

## Features (Proof of Concept)
1. **Entropy Analysis (`calculate_shannon_entropy`)**: Scans text for abnormal information density to flag potential hidden payloads.
2. **Semantic Perturbation (`apply_semantic_perturbation`)**: Acts as a defensive filter. By intelligently swapping synonyms at a set perturbation rate, fragile steganographic token-encodings are destroyed before the "slop" is ingested into a training pipeline.

## Getting Started
```bash
# Clone the repository
git clone [https://github.com/yourusername/ai-slop-stego-defense.git](https://github.com/yourusername/ai-slop-stego-defense.git)

# Install requirements
pip install nltk

# Run the mitigation toolkit
python slop_defense_toolkit.py

## Citation

If you use this code or discuss our "Patient Zero" hypothesis, please cite our paper: coming soon
