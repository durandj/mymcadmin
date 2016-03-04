"""
Web views
"""

from django.contrib.auth import models as auth_models
from django.utils import decorators
from django.views import generic
from django.views.decorators import csrf
from rest_framework import viewsets

from . import serializers

class UIView(generic.TemplateView):
    """
    UI view for the Angular application
    """

    template_name = 'mymcadmin/ui.html'

    @decorators.method_decorator(csrf.ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super(UIView, self).dispatch(*args, **kwargs)

class UserViewSet(viewsets.ModelViewSet):
    queryset         = auth_models.User.objects.all().order_by('-date_joined')
    serializer_class = serializers.UserSerializer

class GroupViewSet(viewsets.ModelViewSet):
    queryset         = auth_models.Group.objects.all()
    serializer_class = serializers.GroupSerializer

