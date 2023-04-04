import copy

from django.http.request import HttpRequest, QueryDict
from django.http.response import HttpResponse
from django.utils.functional import wraps
from render_block import render_block_to_string

# This decorator combines a bunch of functionality, which you might not need all of!

# The names of parameters are chosen to make usage sound close to natural language:

# for htmx, if hx-target = "foo", then use block "bar"
# @for_htmx(if_hx_target="foo", use_block="bar")

# Future work for this decorator:

# - typing. You could use type hints and static typing checks to ensure that is only used
#   on view functions that return TemplateResponse

# - different ways of matching htmx requests, if needed.


def is_htmx(request: HttpRequest):
    return request.headers.get("Hx-Request", False)


def for_htmx(
    *,
    if_hx_target: str | None = None,
    use_template: str | None = None,
    use_block: str | list[str] | None = None,
    use_block_from_params: bool = False,
):
    """
    If the request is from htmx, then render a partial page, using either:
    - the template specified in `use_template` param
    - the block/blocks specified in `use_block` param
    - the block/blocks specified in GET/POST parameter "use_block", if `use_block_from_params=True` is passed

    If the optional `if_hx_target` parameter is supplied, the
    hx-target header must match the supplied value as well in order
    for this decorator to be applied.
    """
    if len([p for p in [use_block, use_template, use_block_from_params] if p]) != 1:
        raise ValueError("You must pass exactly one of 'use_template', 'use_block' or 'use_block_from_params=True'")

    def decorator(view):
        @wraps(view)
        def _view(request, *args, **kwargs):
            resp = view(request, *args, **kwargs)
            if is_htmx(request):
                if if_hx_target is None or request.headers.get("Hx-Target", None) == if_hx_target:
                    blocks_to_use = use_block
                    if not hasattr(resp, "render"):
                        if not resp.content and any(
                            h in resp.headers
                            for h in (
                                "Hx-Trigger",
                                "Hx-Trigger-After-Swap",
                                "Hx-Trigger-After-Settle",
                                "Hx-Redirect",
                            )
                        ):
                            # This is a special case response, it doesn't need modifying:
                            return resp

                        raise ValueError("Cannot modify a response that isn't a TemplateResponse")
                    if resp.is_rendered:
                        raise ValueError("Cannot modify a response that has already been rendered")

                    if use_block_from_params:
                        use_block_from_params_val = _get_param_from_request(request, "use_block")
                        if use_block_from_params_val is not None:
                            blocks_to_use = use_block_from_params_val

                    if use_template is not None:
                        resp.template_name = use_template
                    elif blocks_to_use is not None:
                        if not isinstance(blocks_to_use, list):
                            blocks_to_use = [blocks_to_use]

                        rendered_blocks = [
                            render_block_to_string(resp.template_name, b, context=resp.context_data, request=request)
                            for b in blocks_to_use
                        ]
                        # Create new simple HttpResponse as replacement
                        resp = HttpResponse(
                            content="".join(rendered_blocks),
                            status=resp.status_code,
                            headers=resp.headers,
                        )

            return resp

        return _view

    return decorator


def _get_param_from_request(request, param):
    """
    Checks GET then POST params for specified param
    """
    if param in request.GET:
        return request.GET.getlist(param)
    elif request.method == "POST" and param in request.POST:
        return request.POST.getlist(param)
    return None


def make_get_request(request: HttpRequest) -> HttpRequest:
    """
    Returns a new GET request based on passed in request.
    """
    new_request = copy.copy(request)
    new_request.POST = QueryDict()
    new_request.method = "GET"
    return new_request
