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


def get_page_by_request(request, queryset, paginate_by=6):
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


@for_htmx(use_template="_page_and_paging_controls.html")
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
        return HttpResponse(content=rendered_block)
    return TemplateResponse(
        request,
        template_name,
        context,
    )


@for_htmx(use_block="page-and-paging-controls")
def paging_with_inline_partials_improved(request):
    return TemplateResponse(
        request,
        "paging_with_inline_partials.html",
        {
            "page_obj": get_page_by_request(request, Monster.objects.all()),
        },
    )


# Similar to above, but with better Locality Of Behaviour,
# because the template specifies the "internal routing"
# of which block to use.
@for_htmx(use_block_from_params=True)
def paging_with_inline_partials_improved_lob(request):
    return TemplateResponse(
        request,
        "paging_with_inline_partials_improved_lob.html",
        {
            "page_obj": get_page_by_request(request, Monster.objects.all()),
        },
    )
