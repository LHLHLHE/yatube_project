from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    template_name = 'app_about/author.html'


class AboutTechView(TemplateView):
    template_name = 'app_about/tech.html'
