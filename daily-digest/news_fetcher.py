#!/usr/bin/env python3
"""
Live AI news fetcher for OptimAI Daily Digest.
Pulls from Google News RSS + major tech publication feeds.
Priority: Claude/Anthropic > OpenAI > Microsoft > Google > Meta > General AI
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


# Google News RSS searches — no API key required
GOOGLE_NEWS_FEEDS = [
    {
        "label": "CLAUDE/ANTHROPIC",
        "url": "https://news.google.com/rss/search?q=Claude+Anthropic+AI&hl=en-US&gl=US&ceid=US:en",
        "priority": 1,
    },
    {
        "label": "OPENAI",
        "url": "https://news.google.com/rss/search?q=OpenAI+GPT+ChatGPT&hl=en-US&gl=US&ceid=US:en",
        "priority": 2,
    },
    {
        "label": "MICROSOFT AI",
        "url": "https://news.google.com/rss/search?q=Microsoft+AI+Copilot&hl=en-US&gl=US&ceid=US:en",
        "priority": 3,
    },
    {
        "label": "GOOGLE AI",
        "url": "https://news.google.com/rss/search?q=Google+Gemini+DeepMind+AI&hl=en-US&gl=US&ceid=US:en",
        "priority": 4,
    },
    {
        "label": "META AI",
        "url": "https://news.google.com/rss/search?q=Meta+AI+Llama+model&hl=en-US&gl=US&ceid=US:en",
        "priority": 5,
    },
    {
        "label": "AI TOOLS",
        "url": "https://news.google.com/rss/search?q=AI+tools+automation+agents+2026&hl=en-US&gl=US&ceid=US:en",
        "priority": 6,
    },
]

# Tech publication AI feeds
PUBLICATION_FEEDS = [
    {
        "label": "TechCrunch AI",
        "url": "https://techcrunch.com/tag/artificial-intelligence/feed/",
        "priority": 3,
    },
    {
        "label": "The Verge AI",
        "url": "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml",
        "priority": 3,
    },
]


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
