# Phishing Analyzer

A desktop app that analyzes emails, domains, and IPs for phishing threats using machine learning and AI.

## Features
- Paste or upload an email, IP, or domain (auto-detected)
- Risk score (Low / Medium / High / Critical)
- "Explain with AI" - local AI gives a plain-English summary
- Image upload — extracts text from email screenshots via OCR
- Export results as PDF

## Setup

1. Clone the repo and create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Add your API key — open the app and click **VT Key** to enter your [VirusTotal API key](https://www.virustotal.com).

4. Install [Ollama](https://ollama.com) and pull the local AI models:
   ```bash
   ollama pull qwen2.5:3b
   ollama pull gemma3:4b
   ```

5. Run the app:
   ```bash
   python main.py
   ```

## Tech Stack
Python · PyQt5 · scikit-learn · Ollama · VirusTotal API · ReportLab
