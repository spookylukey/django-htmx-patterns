from django.template.response import TemplateResponse
from htmx_patterns.models import Monster


def home(request):
    return TemplateResponse(
        request,
        "home.html",
        {
            "monster": Monster.objects.first(),
        },
    )
