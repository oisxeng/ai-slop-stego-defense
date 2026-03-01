import math
import random
from collections import Counter
# Hinweis für Nutzer: pip install nltk
import nltk
from nltk.corpus import wordnet

# NLTK Ressourcen herunterladen (beim ersten Start)
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')
    nltk.download('averaged_perceptron_tagger')

def calculate_shannon_entropy(text):
    """
    Berechnet die Shannon-Entropie eines Textes auf Zeichenebene.
    (Repräsentiert die 'Entropy Analysis' aus Abschnitt 4 des Papers).
    Eine ungewöhnlich hohe Entropie in scheinbar banalem Text ('Slop') 
    kann auf versteckte steganographische Payloads hinweisen.
    """
    if not text:
        return 0
    
    probabilities = [n_x / len(text) for x, n_x in Counter(text).items()]
    entropy = -sum(p * math.log2(p) for p in probabilities)
    return round(entropy, 4)

def apply_semantic_perturbation(text, perturbation_rate=0.2):
    """
    Wendet semantische Perturbation an (Synonym-Tausch), um fragile 
    steganographische Signale zu zerstören (Data Perturbation aus Abschnitt 6.1).
    """
    words = text.split()
    perturbed_words = []
    
    for word in words:
        # Mit einer bestimmten Wahrscheinlichkeit (perturbation_rate) ein Synonym suchen
        if random.random() < perturbation_rate and word.isalpha():
            synonyms = wordnet.synsets(word)
            if synonyms:
                # Nimm das erste Lemma (Synonym) des ersten Synsets, das nicht das Ursprungswort ist
                lemmas = synonyms[0].lemma_names()
                valid_lemmas = [lemma for lemma in lemmas if lemma.lower() != word.lower()]
                if valid_lemmas:
                    # Ersetze Unterstriche durch Leerzeichen (WordNet-Formatierung)
                    chosen_synonym = random.choice(valid_lemmas).replace('_', ' ')
                    perturbed_words.append(chosen_synonym)
                    continue
        
        # Wenn kein Synonym gefunden wurde oder die Wahrscheinlichkeit nicht griff
        perturbed_words.append(word)
        
    return " ".join(perturbed_words)

if __name__ == "__main__":
    print("=== AI Slop Steganography Defense Toolkit ===")
    
    # Simulierter AI Slop Text (könnte eine versteckte Payload enthalten)
    suspicious_slop = (
        "The quick implementation of advanced neural networks completely transforms "
        "digital landscapes. Technology rapidly evolves."
    )
    
    print("\n[1] Original AI Slop:")
    print(suspicious_slop)
    
    # 1. Entropie-Analyse
    entropy_score = calculate_shannon_entropy(suspicious_slop)
    print(f"\n[2] Entropy Analysis Score: {entropy_score} bits/char")
    print("    (Note: Baseline comparisons would flag anomalies here.)")
    
    # 2. Data Perturbation anwenden
    print("\n[3] Applying Semantic Perturbation (breaking covert channels)...")
    sanitized_text = apply_semantic_perturbation(suspicious_slop, perturbation_rate=0.4)
    
    print("\n[4] Sanitized Training Data (Safe for Open-Source ingestion):")
    print(sanitized_text)
    print("\nConclusion: Fragile steganographic token-distributions have been disrupted.")
