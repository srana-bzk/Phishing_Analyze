"""
virustotal.py
-------------
VirusTotal API v3 helpers.

Supports:
  - IP address reputation lookup
  - Domain reputation lookup  (new)
  - API key save/load via config.json

VT API docs: https://developers.virustotal.com/reference/ip-info
             https://developers.virustotal.com/reference/domain-info
"""

import os
import json
import re
import requests

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
VT_BASE     = "https://www.virustotal.com/api/v3"


# ── Config helpers ─────────────────────────────────────────────────────────────

def save_api_key(key: str):
    """Persist the VT API key to config.json."""
    config = _load_config()
    config["virustotal_api_key"] = key.strip()
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def load_api_key() -> str:
    """Return saved VT API key, or empty string if not set."""
    return _load_config().get("virustotal_api_key", "")


def save_qwen_key(key: str):
    """Persist the Qwen (DashScope) API key to config.json."""
    config = _load_config()
    config["qwen_api_key"] = key.strip()
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def load_qwen_key() -> str:
    """Return saved Qwen API key, or empty string if not set."""
    return _load_config().get("qwen_api_key", "")


def _load_config() -> dict:
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


# ── Input-type detectors ───────────────────────────────────────────────────────

_IP_RE = re.compile(
    r"^\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*$"
)

# Matches bare domains AND http(s):// URLs — extracts just the hostname.
# Examples: "example.com", "sub.example.co.uk", "https://evil.phish.io/path?x=1"
# Rejects anything with spaces, @-signs (emails), or no dot at all.
_DOMAIN_RE = re.compile(
    r"^\s*(?:https?://)?"                     # optional scheme
    r"("
      r"(?:[a-zA-Z0-9]"                       # label start
      r"(?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?" # label body
      r"\.)+"                                  # dot separator (1+ labels)
      r"[a-zA-Z]{2,}"                          # TLD
    r")"
    r"(?:[/?\#].*)?"                           # optional path/query/fragment
    r"\s*$"
)


def is_ip_address(text: str) -> str | None:
    """Return the IPv4 string if text is a single IP, else None."""
    m = _IP_RE.match(text.strip())
    return m.group(1) if m else None


def is_domain(text: str) -> str | None:
    """
    Return the bare hostname if text is a single domain or URL, else None.
    Rejects IPs and anything containing spaces or @ (those are emails).
    """
    t = text.strip()
    # Must not look like an IP, an email, or multi-line content
    if _IP_RE.match(t) or "@" in t or "\n" in t or " " in t:
        return None
    m = _DOMAIN_RE.match(t)
    return m.group(1).lower() if m else None


# ── IP lookup ──────────────────────────────────────────────────────────────────

def lookup_ip(ip: str, api_key: str) -> dict:
    """
    Query VirusTotal for an IP address.
    Returns a normalised result dict — same shape used by the GUI renderer.

    Raises:
        ValueError  — bad/missing API key (HTTP 401/403)
        RuntimeError — any other API/network error
    """
    url     = f"{VT_BASE}/ip_addresses/{ip}"
    headers = {"x-apikey": api_key}

    try:
        resp = requests.get(url, headers=headers, timeout=15)
    except requests.exceptions.ConnectionError:
        raise RuntimeError("No internet connection or VirusTotal unreachable.")
    except requests.exceptions.Timeout:
        raise RuntimeError("VirusTotal request timed out.")

    if resp.status_code in (401, 403):
        raise ValueError("Invalid or missing VirusTotal API key.")
    if resp.status_code == 404:
        raise RuntimeError(f"IP {ip} not found in VirusTotal database.")
    if resp.status_code != 200:
        raise RuntimeError(f"VirusTotal returned HTTP {resp.status_code}.")

    data  = resp.json().get("data", {})
    attrs = data.get("attributes", {})

    stats      = attrs.get("last_analysis_stats", {})
    malicious  = stats.get("malicious", 0)
    suspicious = stats.get("suspicious", 0)
    harmless   = stats.get("harmless", 0)
    undetected = stats.get("undetected", 0)
    total      = malicious + suspicious + harmless + undetected

    # Collect names of engines that flagged it
    flagged_engines = [
        engine
        for engine, res in attrs.get("last_analysis_results", {}).items()
        if res.get("category") in ("malicious", "suspicious")
    ]

    # Derive a simple risk level from malicious count
    if malicious >= 10:
        risk = "Critical"
    elif malicious >= 5:
        risk = "High"
    elif malicious >= 1 or suspicious >= 3:
        risk = "Medium"
    else:
        risk = "Low"

    return {
        "type":             "ip",
        "ip":               ip,
        "risk_level":       risk,
        "malicious":        malicious,
        "suspicious":       suspicious,
        "harmless":         harmless,
        "undetected":       undetected,
        "total_engines":    total,
        "flagged_engines":  flagged_engines,
        "country":          attrs.get("country", "Unknown"),
        "as_owner":         attrs.get("as_owner", "Unknown"),
        "asn":              attrs.get("asn", ""),
        "reputation":       attrs.get("reputation", 0),
        "network":          attrs.get("network", ""),
        "tags":             attrs.get("tags", []),
    }


# ── Domain lookup ──────────────────────────────────────────────────────────────

def lookup_domain(domain: str, api_key: str) -> dict:
    """
    Query VirusTotal for a domain name.
    Returns a normalised result dict (type='domain').

    Raises:
        ValueError   — bad/missing API key
        RuntimeError — any other error
    """
    url     = f"{VT_BASE}/domains/{domain}"
    headers = {"x-apikey": api_key}

    try:
        resp = requests.get(url, headers=headers, timeout=15)
    except requests.exceptions.ConnectionError:
        raise RuntimeError("No internet connection or VirusTotal unreachable.")
    except requests.exceptions.Timeout:
        raise RuntimeError("VirusTotal request timed out.")

    if resp.status_code in (401, 403):
        raise ValueError("Invalid or missing VirusTotal API key.")
    if resp.status_code == 404:
        raise RuntimeError(f"Domain '{domain}' not found in VirusTotal database.")
    if resp.status_code != 200:
        raise RuntimeError(f"VirusTotal returned HTTP {resp.status_code}.")

    data  = resp.json().get("data", {})
    attrs = data.get("attributes", {})

    stats      = attrs.get("last_analysis_stats", {})
    malicious  = stats.get("malicious", 0)
    suspicious = stats.get("suspicious", 0)
    harmless   = stats.get("harmless", 0)
    undetected = stats.get("undetected", 0)
    total      = malicious + suspicious + harmless + undetected

    flagged_engines = [
        engine
        for engine, res in attrs.get("last_analysis_results", {}).items()
        if res.get("category") in ("malicious", "suspicious")
    ]

    # Categories is a dict like {"Forcepoint ThreatSeeker": "phishing", ...}
    categories = list(attrs.get("categories", {}).values())

    # last_dns_records: list of {type, value} dicts
    dns_records = [
        f"{r.get('type','?')} → {r.get('value','?')}"
        for r in attrs.get("last_dns_records", [])[:6]   # cap at 6
    ]

    # Registrar and dates
    registrar     = attrs.get("registrar", "Unknown")
    creation_date = attrs.get("creation_date")     # unix timestamp or None
    if creation_date:
        from datetime import datetime
        creation_date = datetime.utcfromtimestamp(creation_date).strftime("%Y-%m-%d")
    else:
        creation_date = "Unknown"

    if malicious >= 10:
        risk = "Critical"
    elif malicious >= 5:
        risk = "High"
    elif malicious >= 1 or suspicious >= 3:
        risk = "Medium"
    else:
        risk = "Low"

    return {
        "type":             "domain",
        "domain":           domain,
        "risk_level":       risk,
        "malicious":        malicious,
        "suspicious":       suspicious,
        "harmless":         harmless,
        "undetected":       undetected,
        "total_engines":    total,
        "flagged_engines":  flagged_engines,
        "categories":       categories,
        "registrar":        registrar,
        "creation_date":    creation_date,
        "dns_records":      dns_records,
        "reputation":       attrs.get("reputation", 0),
        "tags":             attrs.get("tags", []),
    }
