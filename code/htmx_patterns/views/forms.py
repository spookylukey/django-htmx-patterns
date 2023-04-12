from django.contrib import messages
from django.forms import ModelForm
from django.forms.fields import DateField
from django.forms.widgets import DateInput
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from htmx_patterns.form_renderers import BulmaFormMixin

from ..models import Monster


class CreateMonsterForm(BulmaFormMixin, ModelForm):
    date_of_birth = DateField(initial=None, widget=DateInput(attrs={"type": "date"}))

    class Meta:
        model = Monster
        fields = ["name", "is_happy", "date_of_birth", "type"]


def form_validation(request):
    if request.method == "POST":
        form = CreateMonsterForm(request.POST)
        if form.is_valid():
            monster = form.save()
            messages.info(request, f"Monster {monster.name} created. You can make another.")
            return redirect(".")
    else:
        form = CreateMonsterForm()
    return TemplateResponse(request, "form_validation.html", {"form": form})
