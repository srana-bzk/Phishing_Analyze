"""
ml_model.py
-----------
Trains and loads a phishing email classifier.

Dataset : ealvaradob/phishing-dataset (emails subset) from HuggingFace
          columns: text (str), label (0=safe, 1=phishing)
Model   : TF-IDF vectorizer  +  Random Forest classifier
Saved to: models/phishing_model.pkl
          models/tfidf_vectorizer.pkl
"""

import os
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Where trained model files live
MODELS_DIR   = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH   = os.path.join(MODELS_DIR, "phishing_model.pkl")
TFIDF_PATH   = os.path.join(MODELS_DIR, "tfidf_vectorizer.pkl")


class PhishingModel:
    def __init__(self):
        self.vectorizer = None
        self.classifier = None
        self._ready = False

    # ── Public API ────────────────────────────────────────────────────────────

    def is_ready(self):
        """Return True if a trained model is loaded."""
        return self._ready

    def load_or_train(self, progress_callback=None):
        """
        Load saved model from disk.
        If no saved model exists, download dataset and train from scratch.
        progress_callback(message: str, pct: int) — pct=-1 means no bar change.
        """
        def log(msg, pct=-1):
            if progress_callback:
                progress_callback(msg, pct)

        if self._load_from_disk(log):
            log("✓ Model ready.", 100)
            return

        log("No saved model found — downloading dataset and training...", 0)
        texts, labels = self._download_dataset(log)
        self._train(texts, labels, log)
        log("Saving model to disk...", 95)
        self._save_to_disk()
        log("✓ Model ready.", 100)

    def predict(self, text):
        """
        Predict whether text is phishing.
        Returns (label: int, confidence: float)
          label 1 = phishing, 0 = safe
          confidence in [0.0, 1.0]
        """
        if not self._ready:
            return 0, 0.0

        vec = self.vectorizer.transform([text])
        label = int(self.classifier.predict(vec)[0])
        proba = self.classifier.predict_proba(vec)[0]
        # confidence = probability of the predicted class
        confidence = float(proba[label])
        return label, confidence

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _load_from_disk(self, log=None):
        def _log(msg, pct=-1):
            if log:
                log(msg, pct)
        if os.path.exists(MODEL_PATH) and os.path.exists(TFIDF_PATH):
            _log("Loading TF-IDF vectorizer from disk...", 30)
            self.vectorizer = joblib.load(TFIDF_PATH)
            _log("Loading Random Forest classifier from disk...", 70)
            self.classifier = joblib.load(MODEL_PATH)
            self._ready = True
            return True
        return False

    def _save_to_disk(self):
        os.makedirs(MODELS_DIR, exist_ok=True)
        joblib.dump(self.vectorizer, TFIDF_PATH)
        joblib.dump(self.classifier, MODEL_PATH)

    def _download_dataset(self, log):
        """
        Download the phishing email dataset from HuggingFace.
        Tries four methods in order so that if one path is unavailable the
        next one takes over automatically.
        log(msg, pct) — pct in [0, 30] range used for download phase.
        """
        import io
        import requests
        import pandas as pd

        # ── Method 1: datasets-server parquet index (no config filter) ────────
        log("Method 1: HuggingFace datasets-server parquet index…", 2)
        try:
            resp = requests.get(
                "https://datasets-server.huggingface.co/parquet"
                "?dataset=ealvaradob%2Fphishing-dataset",
                timeout=30,
            )
            if resp.ok:
                all_files = resp.json().get("parquet_files", [])
                # Prefer emails config, fall back to all configs
                email_files = [f for f in all_files if f.get("config") == "emails"]
                to_use = email_files or all_files
                if to_use:
                    frames = []
                    for i, pf in enumerate(to_use):
                        pct = 3 + int((i / len(to_use)) * 25)
                        log(f"  Downloading shard {i+1}/{len(to_use)} ({pf.get('split','?')})…", pct)
                        r = requests.get(pf["url"], timeout=120)
                        r.raise_for_status()
                        frames.append(pd.read_parquet(io.BytesIO(r.content)))
                    all_data = pd.concat(frames, ignore_index=True)
                    texts, labels = self._extract_columns(all_data)
                    log(f"  ✓ Dataset loaded: {len(texts)} samples.", 30)
                    return texts, labels
        except Exception as e:
            log(f"  Method 1 failed: {e}", -1)

        # ── Method 2: browse Hub repo tree and grab parquet files directly ────
        log("Method 2: HuggingFace Hub raw file access…", 5)
        try:
            tree = requests.get(
                "https://huggingface.co/api/datasets/ealvaradob/phishing-dataset/tree/main",
                timeout=30,
            )
            if tree.ok:
                entries = tree.json()
                # Prefer files in an "email" subfolder, then any parquet file
                parquets = [
                    e for e in entries
                    if e.get("path", "").endswith(".parquet")
                    and "email" in e.get("path", "").lower()
                ]
                if not parquets:
                    parquets = [e for e in entries if e.get("path", "").endswith(".parquet")]
                if parquets:
                    frames = []
                    for i, entry in enumerate(parquets):
                        path = entry["path"]
                        pct = 6 + int((i / len(parquets)) * 22)
                        log(f"  Downloading {i+1}/{len(parquets)}: {path}…", pct)
                        url = (
                            "https://huggingface.co/datasets/ealvaradob/phishing-dataset"
                            f"/resolve/main/{path}"
                        )
                        r = requests.get(url, timeout=120)
                        r.raise_for_status()
                        frames.append(pd.read_parquet(io.BytesIO(r.content)))
                    all_data = pd.concat(frames, ignore_index=True)
                    texts, labels = self._extract_columns(all_data)
                    log(f"  ✓ Dataset loaded: {len(texts)} samples.", 30)
                    return texts, labels
        except Exception as e:
            log(f"  Method 2 failed: {e}", -1)

        # ── Method 3: cybersectony phishing email detection dataset ──────────
        log("Method 3: cybersectony/phishing-email-detection-v2.4.1…", 10)
        try:
            from datasets import load_dataset
            ds = load_dataset("cybersectony/phishing-email-detection-v2.4.1", split="train")
            texts  = [str(x) for x in ds["Email Text"]]
            labels = [1 if str(v).lower().startswith("phishing") else 0
                      for v in ds["Email Type"]]
            log(f"  ✓ Dataset loaded: {len(texts)} samples.", 30)
            return texts, labels
        except Exception as e:
            log(f"  Method 3 failed: {e}", -1)

        # ── Method 4: sms_spam (small but always available) ───────────────────
        log("Method 4: sms_spam fallback (small dataset)…", 15)
        try:
            from datasets import load_dataset
            ds = load_dataset("sms_spam", split="train")
            texts  = [str(x) for x in ds["sms"]]
            labels = [1 if v == "spam" else 0 for v in ds["label"]]
            log(f"  ✓ Dataset loaded: {len(texts)} samples (fallback).", 30)
            return texts, labels
        except Exception as e:
            log(f"  Method 4 failed: {e}", -1)

        raise RuntimeError(
            "All four dataset download methods failed.\n\n"
            "Please check your internet connection and try again.\n"
            "If the problem persists, you can manually place a CSV file at\n"
            "  data/emails.csv\nwith columns: text (str), label (0=safe, 1=phishing)"
        )

    @staticmethod
    def _extract_columns(df):
        """Pick text and label columns from a DataFrame by common names."""
        text_col  = next(
            (c for c in df.columns if c.lower() in ("text", "email", "content", "body", "message")),
            df.columns[0],
        )
        label_col = next(
            (c for c in df.columns if c.lower() in ("label", "spam", "phishing", "is_phishing")),
            df.columns[-1],
        )
        texts  = df[text_col].astype(str).tolist()
        raw    = df[label_col].tolist()
        if raw and isinstance(raw[0], str):
            labels = [1 if str(v).lower() in ("1", "phishing", "spam", "true") else 0 for v in raw]
        else:
            labels = [int(bool(v)) for v in raw]
        return texts, labels

    def _train(self, texts, labels, log):
        """Vectorize text and train Random Forest (pct range: 31-94)."""
        log(f"Vectorizing {len(texts):,} samples with TF-IDF (20k features, bigrams)…", 35)
        self.vectorizer = TfidfVectorizer(
            max_features=20_000,
            ngram_range=(1, 2),   # unigrams + bigrams
            sublinear_tf=True,
            stop_words="english"
        )
        X = self.vectorizer.fit_transform(texts)
        log(f"  Feature matrix: {X.shape[0]:,} × {X.shape[1]:,}", 50)

        log("Splitting 80% train / 20% test…", 55)
        X_train, X_test, y_train, y_test = train_test_split(
            X, labels, test_size=0.2, random_state=42
        )
        log(f"  Train: {X_train.shape[0]:,}  |  Test: {X_test.shape[0]:,}", 60)

        log("Training Random Forest (200 trees, all CPU cores) — this takes ~1 min…", 65)
        self.classifier = RandomForestClassifier(
            n_estimators=200,
            n_jobs=-1,           # use all CPU cores
            random_state=42
        )
        self.classifier.fit(X_train, y_train)

        acc = accuracy_score(y_test, self.classifier.predict(X_test))
        log(f"✓ Training complete.  Accuracy: {acc * 100:.1f}%", 90)
        self._ready = True
