from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST

from ..models import Monster


def toggle_with_separate_partials(request):
    return TemplateResponse(
        request,
        "toggle_with_separate_partials.html",
        {
            "monsters": Monster.objects.all(),
        },
    )


@require_POST
def toggle_item(request, monster_id):
    monster = Monster.objects.get(id=monster_id)
    monster.is_happy = not monster.is_happy
    monster.save()
    return TemplateResponse(request, "_toggle_item_partial.html", {"monster": monster})
