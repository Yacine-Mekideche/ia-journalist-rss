import feedparser
import os
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def load_rss_sources(file="rss_sources.txt"):
    with open(file, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def fetch_articles(keyword, feeds, max_articles=10):
    articles = []
    for feed_url in feeds:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:max_articles]:
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            link = entry.get("link", "")
            published = entry.get("published", "Unknown date")
            if keyword.lower() in title.lower() or keyword.lower() in summary.lower():
                articles.append({
                    "title": title,
                    "summary": summary,
                    "link": link,
                    "published": published,
                    "source": feed.feed.get("title", "Unknown source")
                })
    return articles

def generate_journalist_story(articles):
    compiled_info = ""
    for article in articles:
        compiled_info += f"- Title: {article['title']}\n"
        compiled_info += f"- Summary: {article['summary']}\n"
        compiled_info += f"- Published: {article['published']}\n"
        compiled_info += f"- Source: {article['source']}\n"
        compiled_info += f"- Link: {article['link']}\n\n"

    prompt = f'''
You are an AI journalist writing a friendly news story about recent events.

Using the provided articles, craft a short but coherent story (like a newsletter or a journalist article) summarizing what's been going on. Use clear transitions and connect facts across articles. Mention time references like "two days ago", "last week", etc.

Each time you reference a fact or event, end the sentence with a clickable markdown link using this format: (source: [Source Name](URL))

Here's the content to base your story on:
{compiled_info}

Your story should be in markdown and feel like it’s written by a human journalist.
'''

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500
    )
    return response.choices[0].message.content.strip()
