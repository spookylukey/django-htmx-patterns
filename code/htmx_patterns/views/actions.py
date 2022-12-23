from django.http import HttpRequest
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from htmx_patterns.models import Monster
from htmx_patterns.utils import for_htmx, is_htmx


@for_htmx(use_block_from_params=True)
def multiple_actions(request: HttpRequest, monster_id: int):
    monster: Monster = get_object_or_404(Monster.objects.all(), id=monster_id)

    if request.method == "POST":
        if "kick" in request.POST:
            monster.kick()
        elif "hug" in request.POST:
            monster.hug()
        if not is_htmx(request):
            return HttpResponseRedirect("")

    return TemplateResponse(
        request,
        "multiple_actions.html",
        {
            "monster": monster,
        },
    )
