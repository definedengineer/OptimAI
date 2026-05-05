# OptimAI Daily AI Digest — Setup Guide

## What This Does

Every morning at 6am, this system:
1. Pulls the latest AI news (Claude, OpenAI, Microsoft priority)
2. Generates 5-7 curated updates
3. Writes a TikTok on-camera script
4. Creates a LinkedIn value post
5. Produces 7 ready-to-post tweets
6. Drafts a full newsletter email

Output files land in `content/YYYY-MM-DD_digest.md` (readable) and `.json` (structured).

---

## Requirements

```bash
pip install anthropic
export ANTHROPIC_API_KEY=your_key_here
```

---

## Run Manually

```bash
cd /home/user/OptimAI
python3 daily-digest/digest_generator.py
```

---

## Schedule at 6am Daily (Cron)

```bash
crontab -e
```

Add this line:
```
0 6 * * * cd /home/user/OptimAI && ANTHROPIC_API_KEY=your_key_here python3 daily-digest/digest_generator.py >> daily-digest/logs/digest.log 2>&1
```

Or use the shell wrapper (which also logs):
```
0 6 * * * ANTHROPIC_API_KEY=your_key_here /home/user/OptimAI/daily-digest/run_digest.sh
```

---

## Content Niche: AI / OptimAI

Priority coverage order:
1. Anthropic / Claude
2. OpenAI / ChatGPT
3. Microsoft AI
4. Google DeepMind / Gemini
5. Meta AI / Llama
6. AI tools, agents, automation trends

---

## Customizing News Input

To feed your own curated news (e.g., from RSS, newsletters, or manual curation):

```bash
python3 daily-digest/digest_generator.py --news my_news.txt
```

Or edit `load_news_items()` in `digest_generator.py` to hook into a news API.

---

## Output Structure

```
daily-digest/
├── digest_generator.py     # Main generator script
├── run_digest.sh           # Shell wrapper for cron
├── requirements.txt
├── SETUP.md                # This file
├── logs/
│   └── digest.log
└── content/
    ├── 2026-05-05_digest.md   # Human-readable
    └── 2026-05-05_digest.json # Structured data
```
