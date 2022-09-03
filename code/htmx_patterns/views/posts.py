from django.http.response import HttpResponse
from django.template.response import TemplateResponse
from django.utils.html import format_html
from django.views.decorators.http import require_POST

from ..models import make_monsters


def simple_post_form(request):
    return TemplateResponse(request, "simple_post_form.html", {})


def post_without_form(request):
    return TemplateResponse(request, "post_without_form.html", {})


@require_POST
def post_form_endpoint(request):
    monsters = make_monsters(int(request.POST.get("howmany", "1")))
    # Unlike the normal POST/redirect/GET pattern, we can directly return
    # a partial, becasuse there is no problem with page refresh or back button
    return HttpResponse("".join(format_html("Created {0}<br>", monster.name) for monster in monsters))
