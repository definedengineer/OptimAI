# OptimAI Daily AI Digest — Setup Guide

## What This Does

Every morning at 6am, this system:
1. Fetches live AI news via Google News RSS + tech publication feeds
2. Generates 5-7 curated updates (Claude/Anthropic, OpenAI, Microsoft priority)
3. Writes a TikTok on-camera script
4. Creates a LinkedIn value post
5. Produces 7 ready-to-post tweets
6. Drafts a full newsletter email
7. **Emails the full styled digest to your inbox** (optional)

Output files land in `content/YYYY-MM-DD_digest.md` (readable) and `.json` (structured).

---

## 1. Install Dependencies

```bash
pip install -r daily-digest/requirements.txt
```

---

## 2. Configure API Keys & Email

Create a `.env` file in the repo root (already in `.gitignore`):

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...

# Optional — enables email delivery
EMAIL_FROM=youremail@gmail.com
EMAIL_TO=youremail@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
```

### Gmail App Password Setup
1. Go to [myaccount.google.com/security](https://myaccount.google.com/security)
2. Enable **2-Step Verification**
3. Search for **"App passwords"** → create one for "Mail"
4. Use that 16-char password as `EMAIL_PASSWORD` (not your regular password)

---

## 3. Run Manually

```bash
# Generate digest only
python3 daily-digest/digest_generator.py

# Generate + email to yourself
python3 daily-digest/digest_generator.py --email

# Use a custom news file
python3 daily-digest/digest_generator.py --news my_news.txt --email

# Override date
python3 daily-digest/digest_generator.py --date "May 7, 2026"
```

---

## 4. Schedule at 6am Daily (Cron)

```bash
crontab -e
```

**Generate + email every day at 6am:**
```
0 6 * * * /home/user/OptimAI/daily-digest/run_digest.sh --email
```

**Generate only (no email), save to files:**
```
0 6 * * * /home/user/OptimAI/daily-digest/run_digest.sh
```

---

## 5. News Sources (Live RSS)

Priority order for news fetching:
| Priority | Source |
|----------|--------|
| 1 | Claude / Anthropic (Google News RSS) |
| 2 | OpenAI / ChatGPT (Google News RSS) |
| 3 | Microsoft AI / Copilot (Google News RSS) |
| 3 | TechCrunch AI feed |
| 3 | The Verge AI feed |
| 4 | Google Gemini / DeepMind |
| 5 | Meta AI / Llama |
| 6 | AI tools, agents, automation |

If live fetch fails, the system falls back to Claude's knowledge of recent events.

---

## 6. Custom News Input

To curate your own news and feed it in:

```bash
# Create a text file with your news items
cat > my_news.txt << 'EOF'
1. [CLAUDE/ANTHROPIC] Anthropic releases Claude 5 with...
2. [OPENAI] OpenAI announces...
EOF

python3 daily-digest/digest_generator.py --news my_news.txt --email
```

---

## 7. Output Structure

```
daily-digest/
├── digest_generator.py     # Main generator
├── news_fetcher.py         # Live RSS news fetcher
├── run_digest.sh           # Shell wrapper for cron
├── requirements.txt
├── SETUP.md
├── logs/
│   └── digest.log
└── content/
    ├── 2026-05-07_digest.md   # Human-readable full digest
    └── 2026-05-07_digest.json # Structured data
```

---

## 8. Content Niche

**Who:** Mid-market manufacturing leaders — plant managers, engineering directors, capital project
managers at $50M–$500M companies in pharma, food, and chemical sectors.

**What:** Translate AI tools into practical applications for capital project execution, plant
engineering, and maintenance operations. Bridge the gap between AI hype and the reality of
FDA-regulated environments, PSM/PHA, SAP PM, and the daily grind of running a manufacturing site.

**How:** A 25-year process and capital project engineer (Lilly, Emergent, Nestlé, Bunge, Cabot)
who actually builds with the tools — Make.com automations, no-code apps, Claude Code, AI video,
custom GPTs. Not a consultant talking about AI from the outside.

**Angle:** "AI vs. My Actual Job." Show what works, what fails, and what breaks when you point
modern AI at real engineering problems. Self-deprecating humor on top of deep technical credibility.

**Four content lanes:**
1. AI tools and updates with direct manufacturing or capital project use cases
2. Regulatory and compliance signals (FDA AI guidance, GxP, PSM/PHA, EU AI Act)
3. Mid-market manufacturing trends (capex cycles, reshoring, labor, OEE benchmarks)
4. Practical workflow experiments and case studies from peers who've shipped something

**Tone:** Direct, technically credible, occasionally self-deprecating. Written by someone who has
run a P&ID review at 11pm. No hype. No motivational filler. Real signal for plant floor leaders.
