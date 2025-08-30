from django.shortcuts import render
from django.http import JsonResponse
from .service import fetch_newsapi, fetch_gnews, save_articles
from .models import Article,User
from django.contrib.auth import logout,login as auth_login, authenticate,get_user_model
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password,check_password
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from dateutil.parser import parse
from django.utils import timezone
from functools import lru_cache


# Create your views here.
def timed_lru_cache(seconds, maxsize):  # expires after `seconds`
    def wrapper(func):
        cache = lru_cache(maxsize=maxsize)(func)
        cache.lifetime = timedelta(seconds=seconds)
        cache.expiry = timezone.now() - cache.lifetime

        def wrapped(*args, **kwargs):
            if timezone.now() >= cache.expiry:
                cache.cache_clear()  # reset cache after expiry
                cache.expiry = timezone.now() + cache.lifetime
            return cache(*args, **kwargs)

        return wrapped
    return wrapper

def parse_datetime(dt_str):
    # This will parse the string including the 'Z' and any timezone info
    parsed_dt = parse(dt_str)

    # Ensure the datetime object is timezone-aware
    if timezone.is_aware(parsed_dt):
        return parsed_dt
    else:
        # If it's not timezone-aware, assume it's UTC (Zulu time)
        return timezone.make_aware(parsed_dt, timezone.utc)



def logout_view(request):
    logout(request)
    return render(request, "home.html")


@login_required
def home(request):
    topic = request.GET.get("q", "")
    topic_articles = {}

    articles = Article.objects.filter(topic=topic).order_by("-published_at")[:5]  # max 5
    print("available topics:", Article.objects.values_list("topic", flat=True).distinct())

    if articles.count() >= 3:  # ensure at least 3
        topic_articles[topic] = articles  

    return render(request, "home.html", {"topic_articles": topic_articles})



def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")
        telegram = request.POST.get("telegram")
        hashed_password = make_password(password)

        # Here you would typically save the user to the database
        user = User.objects.create_user(username=username, password=password,email=email)
        
        user.save() 

        return render(request, "login.html", {"message": "Registration successful. Please log in."})
    return render(request, "register.html")


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        

        # Check if username exists
        if not User.objects.filter(username=username).exists():
         
            return render(request, "login.html", {"error": "User does not exist."})

        user = authenticate(request, username=username, password=password)

        if user is not None:
            
            auth_login(request, user)
            return redirect("home")
        else:
            
            return render(request, "login.html", {"error": "Invalid credentials. Please try again."})

    return render(request, "login.html")
  

from django.db import IntegrityError

@timed_lru_cache(seconds=120, maxsize=32)
@login_required
def fetch_and_store(request):
    topic = request.GET.get("q", "").lower()
    print(f"Fetching news for topic: {topic}")

    if not topic:
        return JsonResponse({"error": "No topic provided"}, status=400)

    recent_time = timezone.now() - timedelta(days=1)
    articles = Article.objects.filter(
        topic=topic,
        published_at__gte=recent_time
    )

    if not articles.exists():
        
        api_articles = fetch_newsapi(topic) or fetch_gnews(topic)

        if api_articles:
            
            for a in api_articles:
                try:
                    Article.objects.update_or_create(
                        url=a["url"],
                        defaults={
                            "source": a["source"],
                            "title": a["title"],
                            "published_at": a["published_at"],
                            "content": a["content"],
                            "topic": topic,
                        }
                    )
                except Exception as e:
                    
                    continue  # Skip to the next article
        else:
            
            return JsonResponse({"error": "No articles found from APIs"}, status=404)

    # Re-query the database to get all articles, including the newly saved ones
    articles = Article.objects.filter(topic=topic).order_by("-published_at")[:5]
    

    # Build and return the JSON response
    data = [
        {
            "source": a.source,
            "title": a.title,
            "url": a.url,
            "published_at": a.published_at,
            "content": a.content,
            "topic": a.topic,
        }
        for a in articles
    ]

    return JsonResponse({"topic": topic, "articles": data})