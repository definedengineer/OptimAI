#!/usr/bin/env python3
"""
Live news fetcher for OptimAI Daily Digest.
Niche: AI tools for mid-market manufacturing leaders in pharma, food, and chemical sectors.

Four content lanes:
  1. AI tools with manufacturing / capital project use cases (Claude, OpenAI, Microsoft)
  2. Regulatory & compliance signals (FDA AI guidance, GxP, PSM, EU AI Act)
  3. Mid-market manufacturing trends (capex, reshoring, labor, OEE)
  4. Workflow experiments & case studies (no-code AI, Make.com, shipped solutions)
"""

import re
import time
from datetime import datetime, timezone
from typing import Optional

try:
    import feedparser
    HAS_FEEDPARSER = True
except ImportError:
    HAS_FEEDPARSER = False

try:
    import urllib.request
    HAS_URLLIB = True
except ImportError:
    HAS_URLLIB = False


# ── LANE 1: AI Tools with Manufacturing / Capital Project Use Cases ──────────
LANE1_AI_TOOLS = [
    {
        "label": "CLAUDE/ANTHROPIC",
        "url": "https://news.google.com/rss/search?q=Claude+Anthropic+AI+engineering+manufacturing&hl=en-US&gl=US&ceid=US:en",
        "priority": 1,
    },
    {
        "label": "OPENAI INDUSTRIAL",
        "url": "https://news.google.com/rss/search?q=OpenAI+GPT+manufacturing+enterprise+workflow&hl=en-US&gl=US&ceid=US:en",
        "priority": 2,
    },
    {
        "label": "MICROSOFT AI OPS",
        "url": "https://news.google.com/rss/search?q=Microsoft+Copilot+SAP+industrial+AI&hl=en-US&gl=US&ceid=US:en",
        "priority": 2,
    },
    {
        "label": "AI MANUFACTURING TOOLS",
        "url": "https://news.google.com/rss/search?q=AI+tools+manufacturing+operations+automation&hl=en-US&gl=US&ceid=US:en",
        "priority": 3,
    },
]

# ── LANE 2: Regulatory & Compliance Signals ───────────────────────────────────
LANE2_REGULATORY = [
    {
        "label": "FDA AI GUIDANCE",
        "url": "https://news.google.com/rss/search?q=FDA+AI+artificial+intelligence+guidance+pharma&hl=en-US&gl=US&ceid=US:en",
        "priority": 2,
    },
    {
        "label": "GXP / COMPLIANCE",
        "url": "https://news.google.com/rss/search?q=GxP+validation+AI+21+CFR+Annex+11+manufacturing&hl=en-US&gl=US&ceid=US:en",
        "priority": 2,
    },
    {
        "label": "PSM / PROCESS SAFETY",
        "url": "https://news.google.com/rss/search?q=PSM+PHA+process+safety+AI+chemical+pharma&hl=en-US&gl=US&ceid=US:en",
        "priority": 3,
    },
    {
        "label": "EU AI ACT INDUSTRIAL",
        "url": "https://news.google.com/rss/search?q=EU+AI+Act+manufacturing+regulated+industry&hl=en-US&gl=US&ceid=US:en",
        "priority": 3,
    },
]

# ── LANE 3: Mid-Market Manufacturing Trends ───────────────────────────────────
LANE3_MANUFACTURING = [
    {
        "label": "PHARMA MANUFACTURING",
        "url": "https://news.google.com/rss/search?q=pharma+manufacturing+capital+projects+AI&hl=en-US&gl=US&ceid=US:en",
        "priority": 2,
    },
    {
        "label": "FOOD & CHEMICAL MFG",
        "url": "https://news.google.com/rss/search?q=food+chemical+manufacturing+operations+AI+automation&hl=en-US&gl=US&ceid=US:en",
        "priority": 3,
    },
    {
        "label": "CAPEX & RESHORING",
        "url": "https://news.google.com/rss/search?q=manufacturing+reshoring+capex+capital+projects+2026&hl=en-US&gl=US&ceid=US:en",
        "priority": 3,
    },
    {
        "label": "OEE & WORKFORCE",
        "url": "https://news.google.com/rss/search?q=OEE+manufacturing+workforce+labor+maintenance+AI&hl=en-US&gl=US&ceid=US:en",
        "priority": 4,
    },
]

# ── LANE 4: Workflow Experiments & Case Studies ───────────────────────────────
LANE4_WORKFLOWS = [
    {
        "label": "AI WORKFLOW CASE STUDIES",
        "url": "https://news.google.com/rss/search?q=AI+workflow+automation+manufacturing+case+study&hl=en-US&gl=US&ceid=US:en",
        "priority": 3,
    },
    {
        "label": "NO-CODE AI TOOLS",
        "url": "https://news.google.com/rss/search?q=Make.com+n8n+no-code+AI+automation+engineering&hl=en-US&gl=US&ceid=US:en",
        "priority": 4,
    },
    {
        "label": "SAP PM AI",
        "url": "https://news.google.com/rss/search?q=SAP+PM+maintenance+AI+plant+engineering&hl=en-US&gl=US&ceid=US:en",
        "priority": 3,
    },
]

# ── Trade Publication Feeds ───────────────────────────────────────────────────
PUBLICATION_FEEDS = [
    {
        "label": "Pharma Manufacturing",
        "url": "https://www.pharmamanufacturing.com/rss/",
        "priority": 2,
    },
    {
        "label": "Chemical Engineering",
        "url": "https://www.chemengonline.com/feed/",
        "priority": 2,
    },
    {
        "label": "Food Engineering",
        "url": "https://www.foodengineeringmag.com/rss/content",
        "priority": 3,
    },
    {
        "label": "Plant Engineering",
        "url": "https://www.plantengineering.com/rss/",
        "priority": 2,
    },
    {
        "label": "Control Global",
        "url": "https://www.controlglobal.com/rss/",
        "priority": 3,
    },
]

# All feeds in one list for the fetcher
GOOGLE_NEWS_FEEDS = LANE1_AI_TOOLS + LANE2_REGULATORY + LANE3_MANUFACTURING + LANE4_WORKFLOWS


def _clean_html(text: str) -> str:
    """Strip HTML tags from text."""
    return re.sub(r"<[^>]+>", "", text).strip()


def _is_recent(entry, max_age_hours: int = 36) -> bool:
    """Check if a feed entry was published within max_age_hours."""
    published = entry.get("published_parsed") or entry.get("updated_parsed")
    if not published:
        return True  # include if no date available
    pub_time = datetime(*published[:6], tzinfo=timezone.utc)
    age_hours = (datetime.now(timezone.utc) - pub_time).total_seconds() / 3600
    return age_hours <= max_age_hours


def fetch_feed(feed_config: dict, max_articles: int = 3) -> list[dict]:
    """Fetch articles from a single RSS feed."""
    if not HAS_FEEDPARSER:
        return []

    articles = []
    try:
        parsed = feedparser.parse(feed_config["url"])
        for entry in parsed.entries[:max_articles * 2]:
            if not _is_recent(entry):
                continue
            title = _clean_html(entry.get("title", ""))
            summary = _clean_html(entry.get("summary", entry.get("description", "")))
            if not title:
                continue
            articles.append({
                "label": feed_config["label"],
                "priority": feed_config["priority"],
                "title": title,
                "summary": summary[:300] if summary else "",
                "link": entry.get("link", ""),
                "published": entry.get("published", ""),
            })
            if len(articles) >= max_articles:
                break
    except Exception as e:
        print(f"  [warn] Feed fetch failed ({feed_config['label']}): {e}")

    return articles


def fetch_all_news(max_per_feed: int = 2) -> list[dict]:
    """Fetch news from all feeds, sorted by priority."""
    if not HAS_FEEDPARSER:
        return []

    all_articles = []
    all_feeds = GOOGLE_NEWS_FEEDS + PUBLICATION_FEEDS

    for feed in sorted(all_feeds, key=lambda f: f["priority"]):
        print(f"  Fetching {feed['label']}...")
        articles = fetch_feed(feed, max_articles=max_per_feed)
        all_articles.extend(articles)
        time.sleep(0.5)  # polite delay

    return all_articles


def format_news_for_prompt(articles: list[dict]) -> str:
    """Format fetched articles into the prompt-ready news block."""
    if not articles:
        return ""

    today = datetime.now().strftime("%B %d, %Y")
    lines = [f"LIVE NEWS FEED FOR {today}:\n"]

    seen_titles = set()
    item_num = 1

    for article in articles:
        title_key = article["title"][:50].lower()
        if title_key in seen_titles:
            continue
        seen_titles.add(title_key)

        summary = article["summary"] or "(no summary)"
        lines.append(
            f"{item_num}. [{article['label']}] {article['title']}\n"
            f"   {summary}\n"
        )
        item_num += 1

    return "\n".join(lines)


def get_live_news() -> Optional[str]:
    """
    Main entry point. Returns formatted news string or None if fetch fails.
    Falls back gracefully when feedparser is not installed.
    """
    if not HAS_FEEDPARSER:
        print("  [info] feedparser not installed — run: pip install feedparser")
        return None

    print("Fetching live AI news...")
    articles = fetch_all_news(max_per_feed=2)

    if not articles:
        print("  [warn] No articles fetched. Falling back to curated defaults.")
        return None

    print(f"  Fetched {len(articles)} articles total.")
    return format_news_for_prompt(articles)
