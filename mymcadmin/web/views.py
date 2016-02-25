"""
Web views
"""

from django.views import generic

class UIView(generic.TemplateView):
    """
    UI view for the Angular application
    """

    template_name = 'mymcadmin/ui.html'

