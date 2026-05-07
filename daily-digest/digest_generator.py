#!/usr/bin/env python3
"""
OptimAI Daily AI News Digest Generator
Runs at 6am daily via cron/scheduler.

Outputs: 5-7 news updates, TikTok script, LinkedIn post, 7 tweets, newsletter email.
Optionally delivers the digest to your inbox via email.

Usage:
  python3 digest_generator.py                  # generate today's digest
  python3 digest_generator.py --email          # generate + email to EMAIL_TO
  python3 digest_generator.py --news my.txt    # use custom news file
  python3 digest_generator.py --date "May 7, 2026"
"""

import argparse
import json
import os
import smtplib
import ssl
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import anthropic

from news_fetcher import get_live_news


CONTENT_DIR = Path(__file__).parent / "content"
CONTENT_DIR.mkdir(exist_ok=True)

SYSTEM_PROMPT = """You are the content strategist for OptimAI — a brand that helps creators,
entrepreneurs, and professionals use AI to optimize their work and life.
Your audience follows AI trends closely and wants to stay ahead of the curve.
They are action-oriented, ambitious, and love practical insights over hype.

Tone: Confident, energetic, clear. No fluff. Real value every time.
Brand voice: Smart friend who's always ahead on AI news, not a corporate newsletter."""

DIGEST_PROMPT = """
Based on the latest AI news as of {date}, generate a complete daily content package for OptimAI.

Here are the verified news items to use:

{news_items}

Generate the following, using exactly this JSON structure:

{{
  "date": "{date}",
  "news_updates": [
    {{
      "headline": "short punchy headline",
      "source": "company/publication",
      "summary": "2-3 sentence summary of what happened and why it matters",
      "impact": "1 sentence on what this means for AI users/creators"
    }}
  ],
  "tiktok_script": {{
    "hook": "opening 3-5 seconds — pattern interrupt, bold claim, or question",
    "body": "main script broken into 5-7 punchy sections, each 1-2 sentences. Use line breaks. Conversational, fast-paced. Written to be read on camera.",
    "cta": "strong closing call to action — follow, comment, share",
    "estimated_duration": "e.g. 45-60 seconds",
    "visual_cues": ["list of simple B-roll or text overlay suggestions"]
  }},
  "linkedin_post": {{
    "hook": "first line that stops the scroll",
    "body": "value-packed post with line breaks for readability. Use numbers, bullets where helpful. Professional but not boring. 150-250 words.",
    "cta": "engagement-driving question or prompt",
    "hashtags": ["5-7 relevant hashtags"]
  }},
  "tweets": [
    {{
      "tweet": "tweet text under 280 chars",
      "type": "insight | hot take | thread starter | engagement bait | news drop | tip | prediction"
    }}
  ],
  "newsletter_email": {{
    "subject_line": "compelling subject line",
    "preview_text": "preview/preheader text (40-90 chars)",
    "greeting": "personalized opener",
    "intro": "1-2 sentence warm intro connecting the week's theme",
    "sections": [
      {{
        "title": "section title",
        "content": "section body"
      }}
    ],
    "closing": "warm, brand-consistent sign-off",
    "ps": "optional P.S. line — bonus tip, teaser, or personal note"
  }}
}}

Requirements:
- news_updates: exactly 5-7 items, prioritizing Claude/Anthropic, OpenAI, Microsoft
- tweets: exactly 7 tweets, varied types
- All content should feel cohesive — like a single themed edition
- Write everything as if publishing TODAY
"""

DEFAULT_NEWS_TEMPLATE = """
CURATED AI NEWS FOR {date}:

1. [CLAUDE/ANTHROPIC] Latest updates from Anthropic on Claude models, features, partnerships, and safety research.

2. [OPENAI] Latest developments from OpenAI including model releases, product updates, and business moves.

3. [MICROSOFT AI] Microsoft Copilot, Azure AI, and enterprise AI integration news.

4. [GOOGLE AI] Gemini, DeepMind research, and Google's AI product updates.

5. [META AI] Meta's Llama models, AI research, and product integrations.

6. [AI TOOLS] Emerging AI tools, agent frameworks, and automation trends shaping workflows.

7. [AI BUSINESS] Enterprise AI adoption, funding rounds, and market shifts.

NOTE TO AI: Use your knowledge of recent events up to your training cutoff to fill in
the most newsworthy real stories for each category above. Be specific with company names,
model versions, and actual announcements — do not fabricate details.
"""


def load_news_items(news_file: str = None) -> str:
    """Load news: try live RSS first, then file, then knowledge-based defaults."""
    if news_file and Path(news_file).exists():
        print(f"Using custom news file: {news_file}")
        return Path(news_file).read_text()

    # Try live RSS fetch
    live_news = get_live_news()
    if live_news:
        return live_news

    # Fall back to knowledge-based prompt
    print("Using knowledge-based news defaults.")
    today = datetime.now().strftime("%B %d, %Y")
    return DEFAULT_NEWS_TEMPLATE.format(date=today)


def generate_digest(date: str = None, news_file: str = None) -> dict:
    """Generate the full daily digest using Claude API."""
    if not date:
        date = datetime.now().strftime("%B %d, %Y")

    news_items = load_news_items(news_file)
    client = anthropic.Anthropic()
    prompt = DIGEST_PROMPT.format(date=date, news_items=news_items)

    print(f"Generating OptimAI Daily Digest for {date}...")

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text
    start = raw.find("{")
    end = raw.rfind("}") + 1
    return json.loads(raw[start:end])


def render_markdown(digest: dict) -> str:
    """Render the digest as clean readable markdown."""
    date = digest.get("date", "Today")
    lines = [
        f"# OptimAI Daily AI Digest — {date}",
        "",
        "---",
        "",
        "## TOP AI UPDATES",
        "",
    ]

    for i, item in enumerate(digest.get("news_updates", []), 1):
        lines += [
            f"### {i}. {item['headline']} — _{item['source']}_",
            "",
            item["summary"],
            "",
            f"> **Impact:** {item['impact']}",
            "",
        ]

    tk = digest.get("tiktok_script", {})
    lines += [
        "---",
        "",
        "## TIKTOK SCRIPT",
        f"**Estimated Duration:** {tk.get('estimated_duration', '')}",
        "",
        f"**HOOK:** {tk.get('hook', '')}",
        "",
        "**BODY:**",
        "",
        tk.get("body", ""),
        "",
        f"**CTA:** {tk.get('cta', '')}",
        "",
        "**Visual Cues:**",
    ]
    for cue in tk.get("visual_cues", []):
        lines.append(f"- {cue}")
    lines.append("")

    li = digest.get("linkedin_post", {})
    lines += [
        "---",
        "",
        "## LINKEDIN POST",
        "",
        f"**{li.get('hook', '')}**",
        "",
        li.get("body", ""),
        "",
        li.get("cta", ""),
        "",
        " ".join(li.get("hashtags", [])),
        "",
    ]

    lines += [
        "---",
        "",
        "## 7 TWEETS",
        "",
    ]
    for i, t in enumerate(digest.get("tweets", []), 1):
        lines += [
            f"**Tweet {i}** _{t.get('type', '')}_",
            f"> {t.get('tweet', '')}",
            "",
        ]

    em = digest.get("newsletter_email", {})
    lines += [
        "---",
        "",
        "## NEWSLETTER EMAIL",
        "",
        f"**Subject:** {em.get('subject_line', '')}",
        f"**Preview:** {em.get('preview_text', '')}",
        "",
        em.get("greeting", ""),
        "",
        em.get("intro", ""),
        "",
    ]
    for section in em.get("sections", []):
        lines += [
            f"### {section.get('title', '')}",
            "",
            section.get("content", ""),
            "",
        ]
    lines += [
        em.get("closing", ""),
        "",
        f"_{em.get('ps', '')}_",
    ]

    return "\n".join(lines)


def render_html_email(digest: dict) -> str:
    """Render the full digest as a styled HTML email."""
    date = digest.get("date", "Today")
    em = digest.get("newsletter_email", {})
    tk = digest.get("tiktok_script", {})
    li = digest.get("linkedin_post", {})

    def nl2br(text: str) -> str:
        return text.replace("\n", "<br>")

    sections_html = ""
    for s in em.get("sections", []):
        sections_html += f"""
        <h3 style="color:#1a1a2e;margin-top:24px;">{s.get('title','')}</h3>
        <p style="color:#374151;line-height:1.7;">{nl2br(s.get('content',''))}</p>
        """

    news_html = ""
    for i, item in enumerate(digest.get("news_updates", []), 1):
        news_html += f"""
        <div style="border-left:3px solid #6366f1;padding-left:14px;margin-bottom:20px;">
          <strong style="color:#1a1a2e;">{i}. {item['headline']}</strong>
          <span style="color:#9ca3af;font-size:13px;"> — {item['source']}</span>
          <p style="color:#374151;margin:6px 0;">{item['summary']}</p>
          <p style="color:#6366f1;font-size:13px;margin:0;"><strong>Impact:</strong> {item['impact']}</p>
        </div>
        """

    tweets_html = ""
    for i, t in enumerate(digest.get("tweets", []), 1):
        tweets_html += f"""
        <div style="background:#f8fafc;border-radius:8px;padding:12px 16px;margin-bottom:10px;">
          <span style="color:#9ca3af;font-size:12px;text-transform:uppercase;">{t.get('type','')}</span>
          <p style="color:#1a1a2e;margin:6px 0 0;">{t.get('tweet','')}</p>
        </div>
        """

    tiktok_body = nl2br(tk.get("body", ""))
    visual_cues = "".join(f"<li>{c}</li>" for c in tk.get("visual_cues", []))
    hashtags = " ".join(li.get("hashtags", []))

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <div style="max-width:640px;margin:0 auto;background:#ffffff;">

    <!-- Header -->
    <div style="background:linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%);padding:32px 32px 24px;text-align:center;">
      <p style="color:#818cf8;font-size:12px;letter-spacing:3px;text-transform:uppercase;margin:0 0 8px;">OptimAI Daily</p>
      <h1 style="color:#ffffff;font-size:22px;margin:0 0 6px;">AI News Digest</h1>
      <p style="color:#94a3b8;font-size:14px;margin:0;">{date}</p>
    </div>

    <!-- Preview strip -->
    <div style="background:#6366f1;padding:10px 32px;text-align:center;">
      <p style="color:#e0e7ff;font-size:13px;margin:0;">{em.get('preview_text','')}</p>
    </div>

    <div style="padding:32px;">

      <!-- Greeting + Intro -->
      <p style="font-size:17px;color:#1a1a2e;font-weight:600;margin:0 0 6px;">{em.get('greeting','')}</p>
      <p style="color:#374151;line-height:1.7;margin:0 0 28px;">{em.get('intro','')}</p>

      <!-- Top AI Updates -->
      <h2 style="color:#1a1a2e;font-size:18px;border-bottom:2px solid #e5e7eb;padding-bottom:8px;">🔥 Top AI Updates</h2>
      {news_html}

      <!-- Newsletter Sections -->
      {sections_html}

      <!-- TikTok Script -->
      <h2 style="color:#1a1a2e;font-size:18px;border-bottom:2px solid #e5e7eb;padding-bottom:8px;margin-top:32px;">🎬 TikTok Script ({tk.get('estimated_duration','')})</h2>
      <div style="background:#fafafa;border-radius:8px;padding:20px;">
        <p style="color:#6366f1;font-weight:700;margin:0 0 8px;">HOOK</p>
        <p style="color:#1a1a2e;font-style:italic;margin:0 0 16px;">"{tk.get('hook','')}"</p>
        <p style="color:#6366f1;font-weight:700;margin:0 0 8px;">BODY</p>
        <p style="color:#374151;line-height:1.8;margin:0 0 16px;">{tiktok_body}</p>
        <p style="color:#6366f1;font-weight:700;margin:0 0 8px;">CTA</p>
        <p style="color:#374151;margin:0 0 16px;">{tk.get('cta','')}</p>
        <p style="color:#6366f1;font-weight:700;margin:0 0 8px;">Visual Cues</p>
        <ul style="color:#374151;margin:0;padding-left:20px;">{visual_cues}</ul>
      </div>

      <!-- LinkedIn Post -->
      <h2 style="color:#1a1a2e;font-size:18px;border-bottom:2px solid #e5e7eb;padding-bottom:8px;margin-top:32px;">💼 LinkedIn Post</h2>
      <div style="background:#fafafa;border-radius:8px;padding:20px;">
        <p style="color:#1a1a2e;font-weight:700;margin:0 0 12px;">{li.get('hook','')}</p>
        <p style="color:#374151;line-height:1.8;margin:0 0 12px;">{nl2br(li.get('body',''))}</p>
        <p style="color:#6366f1;margin:0 0 8px;">{li.get('cta','')}</p>
        <p style="color:#94a3b8;font-size:13px;margin:0;">{hashtags}</p>
      </div>

      <!-- 7 Tweets -->
      <h2 style="color:#1a1a2e;font-size:18px;border-bottom:2px solid #e5e7eb;padding-bottom:8px;margin-top:32px;">🐦 7 Tweets</h2>
      {tweets_html}

      <!-- Closing -->
      <div style="border-top:1px solid #e5e7eb;margin-top:32px;padding-top:20px;">
        <p style="color:#374151;margin:0 0 12px;">{em.get('closing','')}</p>
        <p style="color:#6366f1;font-style:italic;font-size:14px;margin:0;">{em.get('ps','')}</p>
      </div>

    </div>

    <!-- Footer -->
    <div style="background:#1a1a2e;padding:20px 32px;text-align:center;">
      <p style="color:#64748b;font-size:12px;margin:0;">OptimAI · Daily AI Intelligence · Sent every morning at 6am</p>
    </div>

  </div>
</body>
</html>"""


def send_email(digest: dict, subject: str = None) -> bool:
    """Send the digest to EMAIL_TO via SMTP. Config loaded from env/.env."""
    email_from = os.getenv("EMAIL_FROM")
    email_to = os.getenv("EMAIL_TO")
    email_password = os.getenv("EMAIL_PASSWORD")
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))

    if not all([email_from, email_to, email_password]):
        print("[email] Skipped — EMAIL_FROM, EMAIL_TO, or EMAIL_PASSWORD not set in .env")
        return False

    em = digest.get("newsletter_email", {})
    subject = subject or em.get("subject_line", f"OptimAI Digest — {digest.get('date','Today')}")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"OptimAI Daily <{email_from}>"
    msg["To"] = email_to

    # Plain-text fallback
    plain = render_markdown(digest)
    msg.attach(MIMEText(plain, "plain"))

    # Rich HTML version
    html = render_html_email(digest)
    msg.attach(MIMEText(html, "html"))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls(context=context)
            server.login(email_from, email_password)
            server.sendmail(email_from, email_to, msg.as_string())
        print(f"[email] Digest sent to {email_to}")
        return True
    except Exception as e:
        print(f"[email] Failed to send: {e}")
        return False


def save_digest(digest: dict) -> Path:
    date_slug = datetime.now().strftime("%Y-%m-%d")
    output_path = CONTENT_DIR / f"{date_slug}_digest.json"
    output_path.write_text(json.dumps(digest, indent=2))
    return output_path


def save_markdown(digest: dict) -> Path:
    date_slug = datetime.now().strftime("%Y-%m-%d")
    output_path = CONTENT_DIR / f"{date_slug}_digest.md"
    output_path.write_text(render_markdown(digest))
    return output_path


def parse_args():
    parser = argparse.ArgumentParser(description="OptimAI Daily AI Digest Generator")
    parser.add_argument("--date", help='Override date, e.g. "May 7, 2026"')
    parser.add_argument("--news", metavar="FILE", help="Path to custom news text file")
    parser.add_argument("--email", action="store_true", help="Send digest to EMAIL_TO after generating")
    parser.add_argument("--no-save", action="store_true", help="Skip saving files (print only)")
    return parser.parse_args()


def main():
    args = parse_args()

    # Load .env from repo root if present
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip())

    digest = generate_digest(date=args.date, news_file=args.news)

    if not args.no_save:
        json_path = save_digest(digest)
        md_path = save_markdown(digest)
        print(f"\nDigest saved to:")
        print(f"  JSON: {json_path}")
        print(f"  Markdown: {md_path}")

    print("\n" + "=" * 60)
    print(render_markdown(digest))

    if args.email:
        send_email(digest)


if __name__ == "__main__":
    main()
