import requests
from .models import Article
from django.utils.dateparse import parse_datetime
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()  # take environment variables from .env.
API_KEY_NEWSAPI = os.getenv("API_KEY_NEWSAPI")
API_KEY_GNEWS = os.getenv("API_KEY_GNEWS")


to_date = datetime.utcnow()
from_date = to_date - timedelta(days=3)
def fetch_newsapi(query):
    url = "https://newsapi.org/v2/everything"
    params = {"q": query,"from": from_date.strftime("%Y-%m-%d"),"to": to_date.strftime("%Y-%m-%d"), "language": "en", "apiKey": API_KEY_NEWSAPI}
    res = requests.get(url, params=params)
    articles = res.json()["articles"]
    print(f"DEBUG: NewsAPI returned {len(articles)} articles.")
    result = [
        {
            "source": "newsapi",
            "title": art["title"],
            "url": art["url"],
            "published_at": parse_datetime(art["publishedAt"]),
            "content": art.get("description", ""),
        }
        for art in articles
    ]
    return result

def fetch_gnews(query):
    url = f"https://gnews.io/api/v4/search"
    params = {"q": query,"from": from_date.strftime("%Y-%m-%d"),"to": to_date.strftime("%Y-%m-%d"), "lang": "en", "token": API_KEY_GNEWS}
    res = requests.get(url, params=params).json()
    return [
        {
            "source": "gnews",
            "title": art["title"],
            "url": art["url"],
            "published_at": parse_datetime(art["publishedAt"]),
            "content": art.get("description", ""),
        }
        for art in res.get("articles", [])
    ]

def save_articles(articles):
    for art in articles:
        Article.objects.get_or_create(
            url=art["url"],  # prevents duplicates
            defaults=art
        )

