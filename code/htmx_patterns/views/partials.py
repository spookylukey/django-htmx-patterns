from django.core.paginator import Paginator
from django.http.response import HttpResponse
from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST
from render_block import render_block_to_string

from ..models import Monster
from ..utils import for_htmx


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


def get_page_by_request(request, queryset, paginate_by=10):
    return Paginator(queryset, per_page=paginate_by).get_page(request.GET.get("page"))


def paging_with_separate_partials(request):
    if request.headers.get("Hx-Request", False):
        template_name = "_page_and_paging_controls.html"
    else:
        template_name = "paging_with_separate_partials.html"
    return TemplateResponse(
        request,
        template_name,
        {
            "page_obj": get_page_by_request(request, Monster.objects.all()),
        },
    )


@for_htmx(template="_page_and_paging_controls.html")
def paging_with_separate_partials_improved(request):
    return TemplateResponse(
        request,
        "paging_with_separate_partials.html",
        {
            "page_obj": get_page_by_request(request, Monster.objects.all()),
        },
    )


def paging_with_inline_partials(request):
    template_name = "paging_with_inline_partials.html"
    context = {
        "page_obj": get_page_by_request(request, Monster.objects.all()),
    }

    if request.headers.get("Hx-Request", False):
        rendered_block = render_block_to_string(
            template_name, "page-and-paging-controls", context=context, request=request
        )
        # Create new simple HttpResponse as replacement
        return HttpResponse(content=rendered_block)
    return TemplateResponse(
        request,
        template_name,
        context,
    )


@for_htmx(block="page-and-paging-controls")
def paging_with_inline_partials_improved(request):
    return TemplateResponse(
        request,
        "paging_with_inline_partials.html",
        {
            "page_obj": get_page_by_request(request, Monster.objects.all()),
        },
    )
