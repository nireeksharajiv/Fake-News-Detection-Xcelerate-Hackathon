Fake News & Deepfake Detection — Real-Time Twitter Analysis

Team GenFocus | Developed for BIT Xcelerate 2025 (Top 47/294)

1. Project Summary
A real-time system that detects misinformation, hoax text, and deepfake images directly from Twitter without training custom ML models. It combines linguistic analysis, visual verification models (VLM), and account credibility signals to score content instantly.

2. Core Features
Real-Time Extraction: Pulls live tweets using multiple queries; filters retweets and captures metadata via Tweepy.
Profile Forensics: Evaluates account trust based on follower ratios, verification status, and post history.
Multi-Signal Scoring: Aggregates scores from Regex patterns (clickbait/panic), VLM analysis, LLM classification (Llama 3), and metadata.

3. Tech Stack
Backend: Python, FastAPI, Flask
Data & API: Tweepy (Twitter API), Pandas, Requests
AI/Analysis: Llama-3 (Text), VLM (Images), Regex
Frontend: Chrome Extension (optional interface)

Credit:
Project by Team GenFocus 
Developed during BIT Xcelerate 2025
