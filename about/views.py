from django.views.generic.base import TemplateView


class AboutAuthor(TemplateView):
    template_name = "author.html"


class AboutTech(TemplateView):
    template_name = "tech.html"
