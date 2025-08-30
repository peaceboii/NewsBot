from django.db import models

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    telegram = models.CharField(max_length=50)

    def __str__(self):
        return self.username

class Article(models.Model):
    topic = models.CharField(max_length=100, db_index=True) 
    source = models.CharField(max_length=50)
    title = models.TextField()
    url = models.URLField(unique=True)
    published_at = models.DateTimeField()
    content = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.topic} - {self.title[:50]}"