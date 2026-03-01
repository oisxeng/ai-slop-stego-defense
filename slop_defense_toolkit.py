import math
import random
import argparse
import os
from collections import Counter
import nltk
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from PIL import Image, ImageFilter

# --- SETUP ---
def setup_nltk():
    resources = ['punkt', 'wordnet', 'averaged_perceptron_tagger']
    for res in resources:
        try:
            nltk.data.find(f'tokenizers/{res}' if res == 'punkt' else f'corpora/{res}')
        except LookupError:
            nltk.download(res, quiet=True)

setup_nltk()

# --- TEXT PERTURBATION ---
def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'): return wordnet.ADJ
    elif treebank_tag.startswith('V'): return wordnet.VERB
    elif treebank_tag.startswith('N'): return wordnet.NOUN
    elif treebank_tag.startswith('R'): return wordnet.ADV
    return None

def calculate_entropy(text, level='word'):
    if not text: return 0.0
    elements = word_tokenize(text.lower()) if level == 'word' else list(text)
    probabilities = [count / len(elements) for element, count in Counter(elements).items()]
    return round(-sum(p * math.log2(p) for p in probabilities), 4)

def apply_text_perturbation(text, perturbation_rate=0.2):
    tokens = word_tokenize(text)
    tagged_tokens = pos_tag(tokens)
    perturbed_words = []
    
    for word, tag in tagged_tokens:
        if word.isalpha() and random.random() < perturbation_rate:
            wn_tag = get_wordnet_pos(tag)
            if wn_tag:
                synsets = wordnet.synsets(word, pos=wn_tag)
                if synsets:
                    lemmas = [l for s in synsets for l in s.lemma_names() if l.lower() != word.lower() and '_' not in l]
                    if lemmas:
                        chosen = random.choice(lemmas)
                        if word.istitle(): chosen = chosen.capitalize()
                        perturbed_words.append(chosen)
                        continue
        perturbed_words.append(word)
    return " ".join(perturbed_words).replace(" ,", ",").replace(" .", ".").replace(" !", "!")

# --- IMAGE PERTURBATION (MULTIMODAL) ---
def apply_image_perturbation(image_path, output_path, quality_reduction=85):
    """
    Wendet Bild-Perturbation an (Blur + JPEG Kompression), um
    steganographische Signale (z.B. LSB) im Pixelrauschen zu zerstören.
    """
    try:
        img = Image.open(image_path)
        # 1. Leichter Weichzeichner zerstört hochfrequentes Rauschen
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        # 2. Konvertiere zu RGB (falls PNG mit Transparenz)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
            
        # 3. Speichern mit leichter JPEG-Kompression
        img.save(output_path, "JPEG", quality=quality_reduction)
        return True
    except Exception as e:
        print(f"Error processing image: {e}")
        return False

# --- MAIN CLI ---
def main():
    parser = argparse.ArgumentParser(description="AI Slop Steganography Defense Toolkit (Multimodal)")
    parser.add_argument("--text", type=str, help="Text zum Analysieren und Bereinigen.")
    parser.add_argument("--image", type=str, help="Pfad zu einem Bild (z.B. slop.png) für Perturbation.")
    parser.add_argument("--rate", type=float, default=0.25, help="Synonym-Ersetzungsrate für Text.")
    args = parser.parse_args()

    print("=== 🛡️ AI Slop Steganography Defense Toolkit (Multimodal) ===\n")
    
    # BILD MODUS
    if args.image:
        if not os.path.exists(args.image):
            print(f"File not found: {args.image}")
            return
            
        out_name = f"sanitized_{os.path.basename(args.image)}.jpg"
        print(f"[1] Multimodal Mode: Processing Image '{args.image}'")
        print("[2] Applying Gaussian Blur & JPEG Compression (breaking LSB steganography)...")
        
        success = apply_image_perturbation(args.image, out_name)
        if success:
            print(f"\n[✓] Sanitized image saved as: {out_name}")
            print("    Fragile steganographic pixel-data has been disrupted.")
            
    # TEXT MODUS (Standard)
    else:
        text = args.text if args.text else (
            "The quick implementation of advanced neural networks completely transforms "
            "digital landscapes. Technology rapidly evolves."
        )
        print("[1] Text Mode: Original Text:")
        print(text)
        
        print(f"\n[2] Entropy Analysis (Word-Level): {calculate_entropy(text, 'word')} bits/word")
        print(f"\n[3] Applying Semantic Perturbation (Rate: {args.rate * 100}%)...")
        
        sanitized_text = apply_text_perturbation(text, perturbation_rate=args.rate)
        print("\n[4] Sanitized Output Data:")
        print(sanitized_text)
        print("\n[✓] Fragile steganographic text channels have been disrupted.")

if __name__ == "__main__":
    main()
