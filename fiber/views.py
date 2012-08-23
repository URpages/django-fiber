from django.conf import settings
from django.http import HttpResponsePermanentRedirect, Http404
from django.views.generic.base import TemplateView

from . import app_settings
from . import mixins
from . import models

class FiberTemplateView(mixins.FiberPageMixin, TemplateView):
    model = models.Page

    def get_fiber_page_url(self):
        return self.request.path_info

    def get_template_names(self):
        page = self.get_fiber_page()
        templates = []
        if getattr(page.site, 'id'):
            templates.append('sites/{0}/node-{1}.html'.format(page.site.id, page.id))
        templates.append('default/node-{0}.html'.format(page.id))
        templates.append('default/page.html')

        return templates
    def render_to_response(self, *args, **kwargs):
        if self.get_fiber_page() == None:
            """
            Take care of Django's CommonMiddleware redirect if the request URL doesn't end in a slash, and APPEND_SLASH=True
            https://docs.djangoproject.com/en/dev/ref/settings/#append-slash
            """
            url = self.get_fiber_page_url()

            if not url.endswith('/') and settings.APPEND_SLASH:
                return HttpResponsePermanentRedirect('%s/' % url)
            else:
                raise Http404
        else:
            """
            Block access to pages that the current user isn't supposed to see.
            """
            if not self.get_fiber_page().is_public_for_user(self.request.user):
                raise Http404

            if self.get_fiber_page().redirect_page and self.get_fiber_page().redirect_page != self.get_fiber_page():  # prevent redirecting to itself
                return HttpResponsePermanentRedirect(self.get_fiber_page().redirect_page.get_absolute_url())

        return super(FiberTemplateView, self).render_to_response(*args, **kwargs)

page = FiberTemplateView.as_view()
