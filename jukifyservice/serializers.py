from rest_framework import serializers
from jukifyservice.models import User, Group, Track, Playlist


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('spotify_id', 'api_endpoint', 'access_token', 'refresh_token',
                  'expires_in', 'last_logged_at', 'display_name')


class GroupSerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ('id', 'users')


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = ('spotify_id', 'name', 'artists', 'preview_url')


class PlaylistSerializer(serializers.ModelSerializer):
    group = serializers.RelatedField(read_only=True)
    tracks = TrackSerializer(many=True, read_only=True)

    class Meta:
        model = Playlist
        fields = ('id', 'group', 'tracks')
