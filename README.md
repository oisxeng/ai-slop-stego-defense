# AI Slop Steganography Defense Toolkit 🛡️

This repository contains the **fully multimodal** proof-of-concept codebase for the research paper: 
**"AI Slop as a Covert Medium: Hidden Structures for Distributed AI Memory, Communication, and Potential Rogue Behaviors"** by Michael Hackl & Leander Kühnel (2026).

## Citation
If you use this code or discuss our "Patient Zero" hypothesis, please cite our paper:

**Plain Text:**
Hackl, M., & Kühnel, L. (2026). AI Slop as a Covert Medium: Hidden Structures for Distributed AI Memory, Communication, and Potential Rogue Behaviors. *arXiv preprint arXiv:XXXX.XXXXX*. [Link comming soon]

**BibTeX:**
```bibtex
@article{hackl2026aislop,
  title={AI Slop as a Covert Medium: Hidden Structures for Distributed AI Memory, Communication, and Potential Rogue Behaviors},
  author={Hackl, Michael and K{\"u}hnel, Leander},
  journal={arXiv preprint arXiv:XXXX.XXXXX},
  year={2026}
}

## Abstract
As AI-generated "slop" floods the internet, our research hypothesizes that this data can act as a covert communication channel and a vector for decentralized data poisoning in open-source models (the "Patient Zero" dynamic). This toolkit demonstrates practical mitigation strategies across **Text, Images, Audio, and Video** as outlined in Section 6.1 of our paper.

## Features (Proof of Concept)
1. **Text 📝**: Entropy analysis and semantic perturbation (synonym swapping) to break fragile token-encodings.
2. **Images 🖼️**: Imperceptible Gaussian blurring and JPEG compression to destroy hidden payloads encoded in pixel noise (LSB).
3. **Audio 🎵**: Audio stream re-encoding and frequency resampling to neutralize acoustic data concealment.
4. **Video 🎬**: Temporal and spatial frame-recalculation via target-bitrate re-encoding to wipe out high-bandwidth video steganography.

## Getting Started
```bash
# Clone the repository
git clone [https://github.com/oisxeng/ai-slop-stego-defense.git](https://github.com/oisxeng/ai-slop-stego-defense.git)

# Install requirements
pip install -r requirements.txt

# Run Defenses based on modality:
python slop_defense_toolkit.py --text "Suspicious AI generated text goes here."
python slop_defense_toolkit.py --image "suspect_image.png"
python slop_defense_toolkit.py --audio "suspect_audio.wav"
python slop_defense_toolkit.py --video "suspect_video.mp4"
