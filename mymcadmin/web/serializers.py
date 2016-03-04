from django.contrib.auth import models as auth_models
from rest_framework import serializers

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta(object):
        model  = auth_models.User
        fields = ('url', 'username', 'email', 'groups')

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta(object):
        model  = auth_models.Group
        fields = ('url', 'name')

