"""
train.py
--------
Standalone script to download the phishing email dataset and train the ML model.
Run this once from terminal:

    venv\Scripts\python train.py

You can tune the parameters in the SETTINGS block below.
After training, the model is saved to models/*.pkl and the app uses it automatically.
"""

import os
import time
import joblib
import io
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix
)

# ╔══════════════════════════════════════════════════════════╗
# ║                  SETTINGS — tune these                  ║
# ╠══════════════════════════════════════════════════════════╣
# ║  TF-IDF vectorizer                                      ║
MAX_FEATURES = 20_000   # vocabulary size — more = slower but richer
NGRAM_MIN    = 1        # 1 = unigrams only
NGRAM_MAX    = 2        # 2 = unigrams + bigrams  (3 adds trigrams, slow)
SUBLINEAR_TF = True     # dampen very frequent words (almost always helps)
# ║  Random Forest classifier                               ║
N_TREES      = 200      # number of trees — more = slower but more stable
MAX_DEPTH    = None     # None = unlimited;  try 30, 50 to speed up
MIN_SAMPLES  = 2        # minimum samples to split a node
# ║  Train / test split                                     ║
TEST_SIZE    = 0.20     # 20 % held out for evaluation
RANDOM_SEED  = 42
# ╚══════════════════════════════════════════════════════════╝

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODELS_DIR, "phishing_model.pkl")
TFIDF_PATH = os.path.join(MODELS_DIR, "tfidf_vectorizer.pkl")


# ── Dataset download ───────────────────────────────────────────────────────────

def download_dataset():
    print("\n[1/4] Downloading dataset…")

    # Method A: cybersectony phishing email dataset (~18 k real emails)
    print("  Trying cybersectony/phishing-email-detection-v2.4.1…")
    try:
        from datasets import load_dataset
        ds = load_dataset("cybersectony/phishing-email-detection-v2.4.1", split="train")
        texts  = [str(x) for x in ds["Email Text"]]
        labels = [1 if str(v).lower().startswith("phishing") else 0 for v in ds["Email Type"]]
        print(f"  ✓ Loaded {len(texts)} emails  "
              f"(phishing: {sum(labels)}, safe: {len(labels)-sum(labels)})")
        return texts, labels
    except Exception as e:
        print(f"  ✗ {e}")

    # Method B: ealvaradob/phishing-dataset — texts.json (emails subset)
    print("  Trying ealvaradob/phishing-dataset via texts.json…")
    try:
        hf_token = os.getenv("HF_TOKEN", "")
        headers = {"Authorization": f"Bearer {hf_token}"} if hf_token else {}
        url = ("https://huggingface.co/datasets/ealvaradob/phishing-dataset"
               "/resolve/main/texts.json")
        r = requests.get(url, headers=headers, timeout=120)
        r.raise_for_status()
        data = r.json()
        # data is a list of {"text": "...", "label": 0/1}
        texts  = [str(item["text"]) for item in data]
        labels = [int(bool(item["label"])) for item in data]
        print(f"  ✓ Loaded {len(texts)} samples.")
        return texts, labels
    except Exception as e:
        print(f"  ✗ {e}")

    # Method C: sms_spam last resort (small, but always works)
    print("  Trying sms_spam (small fallback)…")
    try:
        from datasets import load_dataset
        ds = load_dataset("sms_spam", split="train")
        texts  = [str(x) for x in ds["sms"]]
        labels = [1 if v == "spam" else 0 for v in ds["label"]]
        print(f"  ✓ Loaded {len(texts)} SMS messages (fallback — not ideal for emails)")
        return texts, labels
    except Exception as e:
        print(f"  ✗ {e}")

    raise SystemExit(
        "\n✗ All download methods failed. Check your internet connection.\n"
        "  Or place a CSV at  data/emails.csv  with columns: text, label (0/1)"
    )


# ── Training ───────────────────────────────────────────────────────────────────

def train(texts, labels):
    print(f"\n[2/4] Vectorizing with TF-IDF…")
    print(f"      max_features={MAX_FEATURES}, ngram=({NGRAM_MIN},{NGRAM_MAX}), sublinear={SUBLINEAR_TF}")
    t0 = time.time()
    vectorizer = TfidfVectorizer(
        max_features=MAX_FEATURES,
        ngram_range=(NGRAM_MIN, NGRAM_MAX),
        sublinear_tf=SUBLINEAR_TF,
        stop_words="english",
    )
    X = vectorizer.fit_transform(texts)
    print(f"      Feature matrix: {X.shape[0]} samples × {X.shape[1]} features  ({time.time()-t0:.1f}s)")

    print(f"\n[3/4] Splitting {int((1-TEST_SIZE)*100)}% train / {int(TEST_SIZE*100)}% test…")
    X_train, X_test, y_train, y_test = train_test_split(
        X, labels, test_size=TEST_SIZE, random_state=RANDOM_SEED, stratify=labels
    )
    print(f"      Train: {X_train.shape[0]} samples  |  Test: {X_test.shape[0]} samples")

    print(f"\n[4/4] Training Random Forest…")
    print(f"      n_estimators={N_TREES}, max_depth={MAX_DEPTH}, min_samples_split={MIN_SAMPLES}")
    t0 = time.time()
    clf = RandomForestClassifier(
        n_estimators=N_TREES,
        max_depth=MAX_DEPTH,
        min_samples_split=MIN_SAMPLES,
        n_jobs=-1,
        random_state=RANDOM_SEED,
    )
    clf.fit(X_train, y_train)
    elapsed = time.time() - t0
    print(f"      Done in {elapsed:.1f}s")

    return vectorizer, clf, X_test, y_test


# ── Evaluation ─────────────────────────────────────────────────────────────────

def evaluate(clf, vectorizer, X_test, y_test):
    y_pred = clf.predict(X_test)
    acc    = accuracy_score(y_test, y_pred)

    print("\n" + "═"*52)
    print("  RESULTS")
    print("═"*52)
    print(f"  Accuracy:  {acc*100:.2f}%")
    print()
    print(classification_report(y_test, y_pred, target_names=["Safe", "Phishing"]))

    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()
    print(f"  Confusion matrix:")
    print(f"    True Negative  (safe  → safe)     {tn:>6}")
    print(f"    False Positive (safe  → phishing) {fp:>6}  ← false alarms")
    print(f"    False Negative (phish → safe)     {fn:>6}  ← missed threats")
    print(f"    True Positive  (phish → phishing) {tp:>6}")
    print("═"*52)

    return acc


# ── Save ───────────────────────────────────────────────────────────────────────

def save(vectorizer, clf):
    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(vectorizer, TFIDF_PATH)
    joblib.dump(clf, MODEL_PATH)
    vec_kb = os.path.getsize(TFIDF_PATH) // 1024
    clf_kb = os.path.getsize(MODEL_PATH) // 1024
    print(f"\n  Saved:  tfidf_vectorizer.pkl  ({vec_kb} KB)")
    print(f"          phishing_model.pkl     ({clf_kb} KB)")
    print("  The app will load these automatically on next launch.\n")


# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 52)
    print("  Phishing Email Classifier — Training Script")
    print("=" * 52)
    t_total = time.time()

    texts, labels = download_dataset()
    vectorizer, clf, X_test, y_test = train(texts, labels)
    acc = evaluate(clf, vectorizer, X_test, y_test)
    save(vectorizer, clf)

    print(f"  Total time: {time.time()-t_total:.0f}s")
    print(f"  Model accuracy: {acc*100:.1f}%")
    if acc < 0.85:
        print("\n  TIP: Accuracy below 85%. Try:")
        print("    • N_TREES = 300 or 400")
        print("    • MAX_FEATURES = 30_000")
        print("    • NGRAM_MAX = 3  (adds trigrams)")
    else:
        print("\n  ✓ Model meets the 85%+ accuracy target.")
