from django.http import HttpRequest
from django.http.response import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.functional import partition
from htmx_patterns.models import Monster
from htmx_patterns.utils import for_htmx, is_htmx, make_get_request


@for_htmx(use_block_from_params=True)
def view_restart(request: HttpRequest):
    return _view_restart(request)


def _view_restart(
    request: HttpRequest,
    *,
    selected_happy_monsters: list[Monster] | None = None,
    selected_sad_monsters: list[Monster] | None = None,
):
    monsters = Monster.objects.all()
    sad_monsters, happy_monsters = partition(lambda m: m.is_happy, monsters)

    if request.method == "POST":
        selected_happy_monsters = [
            monster for monster in happy_monsters if f"happy_monster_{monster.id}" in request.POST
        ]
        selected_sad_monsters = [monster for monster in sad_monsters if f"sad_monster_{monster.id}" in request.POST]
        if "kick" in request.POST:
            for monster in selected_happy_monsters:
                monster.kick()
            selected_happy_monsters = []
        if "hug" in request.POST:
            for monster in selected_sad_monsters:
                monster.hug()
            selected_sad_monsters = []
        if is_htmx(request):
            return _view_restart(
                make_get_request(request),
                selected_sad_monsters=selected_sad_monsters,
                selected_happy_monsters=selected_happy_monsters,
            )
        return HttpResponseRedirect("")

    return TemplateResponse(
        request,
        "view_restart.html",
        {
            "happy_monsters": happy_monsters,
            "sad_monsters": sad_monsters,
            "selected_happy_monsters": selected_happy_monsters or [],
            "selected_sad_monsters": selected_sad_monsters or [],
        },
    )
