from django.template.response import TemplateResponse


def home(request):
    return TemplateResponse(request, "home.html", {})
