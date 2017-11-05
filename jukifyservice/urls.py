"""jukifyservice URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from jukifyservice import views, views_usage_data

urlpatterns = [
    url(r'^admin', admin.site.urls),
    url(r'^login', views.login),
    url(r'^user', include([
        url(r'all', views.list_users),
        url(r'(?P<user_id>[\w]+)', include([
            url(r'groups$', views.list_groups_from_user),
            url(r'fetch', include([
                url(r'saved-tracks$', views_usage_data.save_saved_tracks),
                url(r'top-artists$', views_usage_data.save_top_artists_tracks),
                url(r'top-tracks$', views_usage_data.save_top_tracks),
                url(r'playlists$', views_usage_data.save_playlists),
            ])),
        ])),
    ])),
    url(r'^group', include([
        url(r'^$', views.groups),
        url(r'(?P<group_id>[0-9]+)$', views.group_users),
        url(r'(?P<group_id>[0-9]+)/playlist$', views.group_playlist),
        url(r'(?P<group_id>[0-9]+)/recommendations$', views.group_recommendations),
    ]))
]
