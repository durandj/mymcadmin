"""
Web views
"""

from django.views import generic

class RootView(generic.TemplateView):
    """
    Root view
    """

    template_name = 'mymcadmin/base.html'

