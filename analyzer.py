"""
analyzer.py
-----------
Orchestrates all phishing checks and produces a final risk score.

Risk Score Formula
------------------
Score = (ML Confidence × 0.40) + (Keyword Score × 0.25)
      + (URL Score × 0.20)     + (Blacklist Score × 0.15)

All sub-scores are normalised to [0, 100] before weighting.

Risk Levels
-----------
 0-25  → Low
26-50  → Medium
51-75  → High
76-100 → Critical
"""

import re
import email
import os
from ml_model import PhishingModel

# ── NLTK keyword list (loaded lazily) ────────────────────────────────────────
PHISHING_KEYWORDS = [
    # ── Urgency / pressure tactics ────────────────────────────────────────────
    "urgent", "immediately", "act now", "act fast", "limited time",
    "expires", "expiring soon", "expires today", "last chance",
    "respond immediately", "reply asap", "within 24 hours", "within 48 hours",
    "action required", "response required", "time sensitive", "don't delay",
    "failure to respond", "failure to verify",

    # ── Account / identity threats ────────────────────────────────────────────
    "account suspended", "account disabled", "account terminated",
    "account locked", "account on hold", "account will be closed",
    "verify your account", "verify your identity", "confirm your identity",
    "confirm your account", "confirm your email", "reactivate your account",
    "unusual activity", "suspicious login", "suspicious activity",
    "unauthorized access", "unauthorized transaction", "unrecognized login",
    "we noticed", "we detected", "multiple failed attempts",

    # ── Password / security alerts ────────────────────────────────────────────
    "password reset", "reset your password", "change your password",
    "security alert", "security warning", "security update required",
    "security verification", "two-factor authentication", "2fa code",
    "one-time password", "otp", "pin number",

    # ── Credential harvesting ─────────────────────────────────────────────────
    "click here", "click below", "click the link", "click this link",
    "click the button", "follow the link", "login", "log in", "sign in",
    "update your", "confirm your", "validate your", "provide your",
    "enter your", "submit your", "fill in", "complete the form",
    "re-enter", "re-confirm", "re-validate",

    # ── Reward / prize scams ──────────────────────────────────────────────────
    "congratulations", "you have won", "you've been selected",
    "you are the winner", "prize", "lottery", "reward", "bonus",
    "gift card", "free gift", "unclaimed package", "unclaimed funds",
    "claim your prize", "claim your reward", "claim now",

    # ── Financial / payment ───────────────────────────────────────────────────
    "bank account", "credit card", "debit card", "wire transfer",
    "bank transfer", "paypal", "bitcoin", "cryptocurrency", "wallet",
    "refund", "invoice", "payment required", "payment overdue", "overdue",
    "past due", "outstanding balance", "amount due", "pay now",
    "transaction declined", "payment failed", "failed payment",
    "irs", "tax refund", "tax return", "stimulus check",

    # ── Social engineering / authority impersonation ──────────────────────────
    "dear customer", "dear user", "dear account holder", "dear valued",
    "hello dear", "dear friend", "kindly", "please be informed",
    "this is to inform you", "official notice", "legal action",
    "we regret to inform", "your account has been", "your information",
    "your details", "your records",

    # ── Malware / link bait ───────────────────────────────────────────────────
    "download now", "download attachment", "open attachment",
    "see attached", "see the attachment", "view document", "view invoice",
    "shared file", "shared document", "google drive", "dropbox",
    "onedrive link", "docusign", "adobe sign",

    # ── Privacy / data collection ─────────────────────────────────────────────
    "social security", "ssn", "date of birth", "mother's maiden",
    "security question", "full name", "home address", "phone number",
]

# ── PhishTank blacklist (optional CSV) ───────────────────────────────────────
BLACKLIST_PATH = os.path.join(os.path.dirname(__file__), "data", "verified_online.csv")

# Singleton model — loaded once, reused across calls
_model = None


def get_model():
    """Return (and lazily init) the singleton PhishingModel."""
    global _model
    if _model is None:
        _model = PhishingModel()
    return _model


# ── Main entry point ──────────────────────────────────────────────────────────

def analyze(email_text, api_key="", progress_callback=None):
    """
    Auto-detect input type and run the appropriate check.
    - Single IPv4 address  → VirusTotal IP lookup
    - Single domain / URL  → VirusTotal domain lookup
    - Everything else      → phishing email analysis
    Returns a result dict (see each handler for keys).
    """
    from virustotal import is_ip_address, is_domain

    ip = is_ip_address(email_text)
    if ip:
        return _analyze_ip(ip, api_key, progress_callback)

    domain = is_domain(email_text)
    if domain:
        return _analyze_domain(domain, api_key, progress_callback)

    return _analyze_email(email_text, progress_callback)


def _analyze_ip(ip, api_key, progress_callback=None):
    """Route to VirusTotal and return its result dict (type='ip')."""
    def log(msg, pct=-1):
        if progress_callback:
            progress_callback(msg, pct)

    from virustotal import lookup_ip
    log(f"Querying VirusTotal for IP: {ip}", 20)
    result = lookup_ip(ip, api_key)
    log("VirusTotal lookup complete.", 100)
    return result


def _analyze_domain(domain, api_key, progress_callback=None):
    """Route to VirusTotal domain endpoint (type='domain')."""
    def log(msg, pct=-1):
        if progress_callback:
            progress_callback(msg, pct)

    from virustotal import lookup_domain
    log(f"Querying VirusTotal for domain: {domain}", 20)
    result = lookup_domain(domain, api_key)
    log("VirusTotal lookup complete.", 100)
    return result


def _analyze_email(email_text, progress_callback=None):
    """
    Run all checks on email_text.
    Returns a dict with score, risk level, and detailed findings.
    progress_callback(msg: str, pct: int)  — pct=-1 means no bar change
    """
    def log(msg, pct=-1):
        if progress_callback:
            progress_callback(msg, pct)

    result = {
        "score": 0,
        "risk_level": "Low",
        "ml_label": 0,
        "ml_confidence": 0.0,
        "ml_model_name": "Random Forest + TF-IDF (scikit-learn)",
        "keyword_score": 0.0,
        "keyword_hits": [],
        "url_score": 0.0,
        "blacklist_score": 0.0,
        "findings": [],
        "urls_found": [],
        "headers": {},
    }

    # ── Step 1: Parse headers (5%) ────────────────────────────────────────────
    log("Step 1/5 — Parsing email headers…", 5)
    result["headers"] = _parse_headers(email_text)
    h = result["headers"]
    if h.get("From"):
        log(f"  From:    {h['From'][:70]}")
    if h.get("Subject"):
        log(f"  Subject: {h['Subject'][:70]}")
    if h.get("Reply-To"):
        log(f"  Reply-To: {h['Reply-To'][:70]}")

    # ── Step 2: Extract URLs (15%) ────────────────────────────────────────────
    log("Step 2/5 — Extracting URLs…", 15)
    urls = _extract_urls(email_text)
    result["urls_found"] = urls
    if urls:
        log(f"  Found {len(urls)} URL(s):")
        for u in urls[:6]:
            log(f"    • {u[:80]}")
        if len(urls) > 6:
            log(f"    … and {len(urls) - 6} more")
    else:
        log("  No URLs found in email body.")

    # ── Step 3: Keyword scan (25-40%) ─────────────────────────────────────────
    log(f"Step 3/5 — Scanning {len(PHISHING_KEYWORDS)} phishing keywords…", 25)
    text_lower = email_text.lower()
    hits, clean = [], []
    for kw in PHISHING_KEYWORDS:
        if kw in text_lower:
            hits.append(kw)
            log(f"  ⚠  hit:   '{kw}'")
        else:
            clean.append(kw)

    kw_score = min(len(hits) * 8, 100)
    result["keyword_score"] = float(kw_score)
    result["keyword_hits"]  = hits

    if hits:
        log(f"  {len(hits)} suspicious keyword(s) — score: {kw_score}/100", 40)
        result["findings"].append(f"Suspicious keywords detected: {', '.join(hits)}")
    else:
        log(f"  All {len(PHISHING_KEYWORDS)} keywords clean — score: 0/100", 40)

    # ── Step 4: URL heuristics (45-60%) ───────────────────────────────────────
    log(f"Step 4/5 — URL heuristic analysis ({len(urls)} URL(s))…", 45)
    url_score, url_findings = _check_urls(urls)
    result["url_score"] = url_score
    result["findings"].extend(url_findings)

    if url_findings:
        for f in url_findings:
            log(f"  ⚠  {f[:90]}")
        log(f"  {len(url_findings)} suspicious URL(s) — score: {url_score:.0f}/100", 60)
    else:
        log(f"  All URLs appear clean — score: 0/100", 60)

    # ── Step 5: Blacklist check (65-75%) ──────────────────────────────────────
    log("Step 5/5 — Checking PhishTank URL blacklist…", 65)
    bl_score, bl_findings = _check_blacklist(urls)
    result["blacklist_score"] = bl_score
    result["findings"].extend(bl_findings)

    if bl_findings:
        for f in bl_findings:
            log(f"  ⚠  {f[:90]}")
        log(f"  Blacklisted URL(s) detected — score: {bl_score:.0f}/100", 75)
    else:
        log(f"  No blacklist matches — score: 0/100", 75)

    # ── ML classifier (80-90%) ────────────────────────────────────────────────
    log("Running ML classifier (Random Forest + TF-IDF)…", 80)
    model = get_model()
    if model.is_ready():
        label, confidence = model.predict(email_text)
        result["ml_label"]      = label
        result["ml_confidence"] = confidence
        verdict = "PHISHING" if label == 1 else "SAFE"
        log(f"  Verdict: {verdict}  —  {confidence * 100:.1f}% confidence", 90)
        if label == 1:
            result["findings"].append(
                f"ML classifier flagged as phishing ({confidence * 100:.0f}% confidence)"
            )
    else:
        log("  ML model not ready — skipping ML check.", 90)

    # ── Final score (100%) ────────────────────────────────────────────────────
    result["score"] = _calculate_score(
        result["ml_confidence"] if result["ml_label"] == 1 else 0.0,
        result["keyword_score"],
        result["url_score"],
        result["blacklist_score"],
    )
    result["risk_level"] = _risk_level(result["score"])

    if not result["findings"]:
        result["findings"].append("No obvious phishing indicators found.")

    log(f"Final score: {result['score']}/100 — {result['risk_level']} risk", 100)
    return result


# ── Sub-checks ────────────────────────────────────────────────────────────────

def _parse_headers(raw_text):
    """Extract common email headers into a dict."""
    msg = email.message_from_string(raw_text)
    headers = {}
    for key in ("From", "To", "Subject", "Date", "Reply-To", "Return-Path"):
        value = msg.get(key)
        if value:
            headers[key] = value
    return headers


def _extract_urls(text):
    """
    Return all unique URLs / domains found in the text.
    Matches both:
      - Full URLs with protocol: https://example.com/path
      - Bare hostnames per line: example.com  (must have a dot + known TLD)
    """
    seen = set()
    unique = []

    def _add(u):
        u = u.rstrip(".,;)")
        if u and u not in seen:
            seen.add(u)
            unique.append(u)

    # 1. Full URLs with protocol prefix
    for u in re.findall(r'https?://[^\s\'"<>]+', text, re.IGNORECASE):
        _add(u)

    # 2. Bare hostnames / domains (no protocol) — one per line or space-separated
    #    Must contain a dot and end with a real TLD (2-6 chars).
    #    Avoid matching plain words like "example" or single labels.
    bare_pattern = re.compile(
        r'(?<![/@])(?:^|(?<=\s))'          # start of line or after whitespace, not after / or @
        r'((?:[\w-]+\.)+[a-zA-Z]{2,6})'    # hostname.tld  (e.g. evil.pl-login.info)
        r'(?=[/\s,;"\']|$)',               # followed by path, space, punctuation, or end
        re.MULTILINE
    )
    for m in bare_pattern.finditer(text):
        candidate = m.group(1).rstrip(".,;)")
        # Skip if already captured as part of a full URL
        if not any(candidate in u for u in unique):
            _add(candidate)

    return unique


def _check_keywords(text):
    """
    Score email text based on phishing keyword matches.
    Returns (score 0-100, list of matched keywords).
    """
    text_lower = text.lower()
    hits = [kw for kw in PHISHING_KEYWORDS if kw in text_lower]
    # Each keyword hit adds to score; cap at 100
    score = min(len(hits) * 8, 100)
    return float(score), hits


def _check_urls(urls):
    """
    Heuristic analysis of URLs (no external request needed).
    Returns (score 0-100, list of findings).
    """
    if not urls:
        return 0.0, []

    findings = []
    suspicious_count = 0

    for url in urls:
        flags = []

        # Strip protocol so checks work for both full URLs and bare domains
        stripped = re.sub(r'^https?://', '', url, flags=re.IGNORECASE)
        domain_part = re.split(r'[/?#]', stripped)[0]

        # IP address instead of domain name
        if re.match(r'^\d{1,3}(?:\.\d{1,3}){3}', domain_part):
            flags.append("IP address URL")

        # Misleading @ in URL
        if '@' in url:
            flags.append("@ symbol in URL")

        # Excessive subdomains (>3 dots is a phishing signal)
        if domain_part.count('.') > 3:
            flags.append("excessive subdomains")

        # URL shorteners
        shorteners = ["bit.ly", "tinyurl", "goo.gl", "t.co", "ow.ly",
                      "short.link", "rb.gy", "is.gd"]
        if any(s in url.lower() for s in shorteners):
            flags.append("URL shortener")

        # Typosquatting of common brands
        brands = ["paypa1", "arnazon", "micosoft", "g00gle", "faceb00k",
                  "appleid-", "netfl1x", "linkedln"]
        if any(b in url.lower() for b in brands):
            flags.append("possible typosquatting")

        if flags:
            suspicious_count += 1
            findings.append(f"Suspicious URL ({', '.join(flags)}): {url[:60]}")

    score = min(suspicious_count * 30, 100)
    return float(score), findings


def _check_blacklist(urls):
    """
    Check URLs against PhishTank CSV blacklist.
    Returns (score 0-100, findings).
    If no blacklist file exists, silently skips.
    """
    if not urls or not os.path.exists(BLACKLIST_PATH):
        return 0.0, []

    import pandas as pd

    try:
        # PhishTank CSV has a 'url' column
        df = pd.read_csv(BLACKLIST_PATH, usecols=["url"])
        blacklisted = set(df["url"].str.strip().str.lower())
    except Exception:
        return 0.0, []

    findings = []
    hits = 0
    for url in urls:
        if url.lower() in blacklisted:
            findings.append(f"URL on PhishTank blacklist: {url[:60]}")
            hits += 1

    score = 100.0 if hits > 0 else 0.0
    return score, findings


# ── Score formula ─────────────────────────────────────────────────────────────

def _calculate_score(ml_conf_phishing, kw_score, url_score, bl_score):
    """
    Apply weighted formula and return integer score 0-100.
    ml_conf_phishing: ML confidence that email IS phishing (0-1 → scaled to 0-100)
    """
    score = (
        (ml_conf_phishing * 100 * 0.40) +
        (kw_score               * 0.25) +
        (url_score              * 0.20) +
        (bl_score               * 0.15)
    )
    return round(min(score, 100))


def _risk_level(score):
    if score <= 25:
        return "Low"
    elif score <= 50:
        return "Medium"
    elif score <= 75:
        return "High"
    else:
        return "Critical"
