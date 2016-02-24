"""
Web views
"""

from django.conf import settings
from django.contrib import auth
from django.contrib.auth import forms as auth_forms
from django.utils import decorators, http
from django.views import generic
from django.views.decorators import cache, csrf, debug

# pylint: disable=too-many-ancestors

class RootView(generic.TemplateView):
    """
    Root view
    """

    template_name = 'mymcadmin/root.html'

class LoginView(generic.FormView):
    """
    Login view

    Taken and adapted from:
    https://coderwall.com/p/sll1kw/django-auth-class-based-views-login-and-logout
    """

    form_class          = auth_forms.AuthenticationForm
    redirect_field_name = auth.REDIRECT_FIELD_NAME
    success_url         = settings.LOGIN_REDIRECT_URL
    template_name       = 'mymcadmin/login.html'

    @decorators.method_decorator(debug.sensitive_post_parameters('password'))
    @decorators.method_decorator(csrf.csrf_protect)
    @decorators.method_decorator(cache.never_cache)
    def dispatch(self, request, *args, **kwargs):
        # Sets a test cookie to make sure the user has cookies enabled
        request.session.set_test_cookie()

        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        auth.login(self.request, form.get_user())

        # If the test cookie worked, go ahead and delete it since its
        # no longer needed
        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()

        return super(LoginView, self).form_valid(form)

    def get_success_url(self):
        redirect_to = self.request.REQUEST.get(self.redirect_field_name)
        if not http.is_safe_url(url = redirect_to, host = self.request.get_host()):
            redirect_to = self.success_url

            return redirect_to

class LogoutView(generic.RedirectView):
    """
    Logout view

    Taken and adapted from:
    https://coderwall.com/p/sll1kw/django-auth-class-based-views-login-and-logout
    """

    url = settings.LOGIN_URL

    def get(self, request, *args, **kwargs):
        auth.logout(request)

        return super(LogoutView, self).get(request, *args, **kwargs)

