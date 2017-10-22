from django.db import models

class User(models.Model):
    id = models.CharField(max_length=256, primary_key=True)
    api_endpoint = models.CharField(max_length=256)
    access_token = models.CharField(max_length=256)
    refresh_token = models.CharField(max_length=256)
    expires_in = models.IntegerField(default=0)
    last_logged_at = models.DateTimeField(null=True)
    display_name = models.CharField(max_length=256)

class Group(models.Model):
    users = models.ManyToManyField(User)

class Track(models.Model):
    id = models.CharField(max_length=256, primary_key=True)
    name = models.CharField(max_length=256)
    artists = models.CharField(max_length=512)
    preview_url = models.CharField(max_length=256)

class Playlist(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    tracks = models.ManyToManyField(Track)
