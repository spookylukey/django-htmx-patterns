import json

from django.forms import ModelForm
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse

from ..models import Monster
from ..utils import for_htmx


@for_htmx(use_block_from_params=True)
def main(request: HttpRequest):
    return TemplateResponse(
        request,
        "modals_main.html",
        {
            "monsters": Monster.objects.all().order_by("name"),
        },
    )


class CreateMonsterForm(ModelForm):
    class Meta:
        model = Monster
        fields = ["name", "is_happy"]


@for_htmx(use_block_from_params=True)
def create_monster(request: HttpRequest):
    if request.method == "POST":
        form = CreateMonsterForm(request.POST)
        if form.is_valid():
            monster = form.save()
            return HttpResponse(
                headers={
                    "Hx-Trigger": json.dumps(
                        {
                            "closeModal": True,
                            "monsterCreated": monster.id,
                        }
                    )
                }
            )
    else:
        form = CreateMonsterForm()
    return TemplateResponse(request, "modals_create_monster.html", {"form": form})
