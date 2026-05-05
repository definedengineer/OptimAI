#!/usr/bin/env python3
"""
OptimAI Daily AI News Digest Generator
Runs at 6am daily via cron/scheduler
Outputs: news updates, TikTok script, LinkedIn post, 7 tweets, newsletter email
"""

import anthropic
import json
import os
from datetime import datetime
from pathlib import Path


CONTENT_DIR = Path(__file__).parent / "content"
CONTENT_DIR.mkdir(exist_ok=True)

SYSTEM_PROMPT = """You are the content strategist for OptimAI — a brand that helps creators,
entrepreneurs, and professionals use AI to optimize their work and life.
Your audience follows AI trends closely and wants to stay ahead of the curve.
They are action-oriented, ambitious, and love practical insights over hype.

Tone: Confident, energetic, clear. No fluff. Real value every time.
Brand voice: Smart friend who's always ahead on AI news, not a corporate newsletter."""

NEWS_TOPICS = """
Priority sources to cover (in order of priority):
1. Anthropic / Claude
2. OpenAI / ChatGPT
3. Microsoft AI (Copilot, Azure AI, etc.)
4. Google DeepMind / Gemini
5. Meta AI / Llama
6. AI tools, agents, and automation trends

Today's date: {date}
"""

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


def load_news_items(news_file: str = None) -> str:
    """Load news items from a file or use defaults."""
    if news_file and Path(news_file).exists():
        return Path(news_file).read_text()

    # Default to today's curated news if no file provided
    today = datetime.now().strftime("%B %d, %Y")
    return f"""
VERIFIED NEWS FOR {today}:

1. [CLAUDE/ANTHROPIC] Anthropic teams with Goldman Sachs, Blackstone & Hellman & Friedman to launch a $1.5B AI services company targeting PE-owned mid-market firms. Claude Opus 4.7 debuts as the flagship model for financial services work.

2. [CLAUDE/ANTHROPIC] Claude connects to Adobe, Canva, Blender, Autodesk, Ableton & more via new creative software connectors. Partnerships with RISD, Ringling College, and Goldsmiths give students direct Claude access for coursework.

3. [CLAUDE/ANTHROPIC] Claude Security launches in public beta for Enterprise customers — code vulnerability scanning with proposed fixes powered by Opus 4.7, plus scheduled scans and workflow integrations.

4. [CLAUDE/ANTHROPIC] Anthropic announces Claude will permanently remain ad-free, stating advertising incentives are fundamentally incompatible with a genuinely helpful AI assistant.

5. [OPENAI] GPT-5.5 launches on Amazon Bedrock, letting AWS customers build with OpenAI's latest frontier model inside their existing AWS environment — a major shift in OpenAI's cloud strategy away from Microsoft exclusivity.

6. [MICROSOFT/OPENAI] Microsoft and OpenAI restructure their partnership: Microsoft stays primary cloud partner (Azure-first), but OpenAI can now serve customers across any cloud provider. A major shift in the relationship.

7. [PENTAGON/AI] Pentagon signs AI deals with OpenAI, Microsoft, Google, Amazon, Nvidia, Oracle, SpaceX, and Reflection for classified military use — marking a new era of government-grade AI deployment.
"""


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

    # Extract JSON from response
    start = raw.find("{")
    end = raw.rfind("}") + 1
    json_str = raw[start:end]

    return json.loads(json_str)


def save_digest(digest: dict) -> Path:
    """Save the full digest to a dated file."""
    date_slug = datetime.now().strftime("%Y-%m-%d")
    output_path = CONTENT_DIR / f"{date_slug}_digest.json"
    output_path.write_text(json.dumps(digest, indent=2))
    return output_path


def render_markdown(digest: dict) -> str:
    """Render the digest as a clean readable markdown file."""
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

    # TikTok Script
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

    # LinkedIn
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

    # Tweets
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

    # Newsletter
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


def save_markdown(digest: dict) -> Path:
    """Save the rendered markdown digest."""
    date_slug = datetime.now().strftime("%Y-%m-%d")
    output_path = CONTENT_DIR / f"{date_slug}_digest.md"
    output_path.write_text(render_markdown(digest))
    return output_path


def main():
    digest = generate_digest()
    json_path = save_digest(digest)
    md_path = save_markdown(digest)

    print(f"\nDigest saved to:")
    print(f"  JSON: {json_path}")
    print(f"  Markdown: {md_path}")
    print("\n" + "=" * 60)
    print(render_markdown(digest))


if __name__ == "__main__":
    main()
