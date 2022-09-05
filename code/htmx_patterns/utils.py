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


def for_htmx(
    *,
    if_hx_target: str | None = None,
    use_template: str | None = None,
    use_block: str | None = None,
    use_block_from_params: bool = False,
):
    """
    If the request is from htmx, then render a partial page, using either:
    - the template specified in `use_template` param
    - the block specified in `use_block` param
    - the block specified in GET/POST parameter "use_block", if `use_block_from_params=True` is passed

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
            if request.headers.get("Hx-Request", False):
                if if_hx_target is None or request.headers.get("Hx-Target", None) == if_hx_target:
                    block_to_use = use_block
                    if not hasattr(resp, "render"):
                        raise ValueError("Cannot modify a response that isn't a TemplateResponse")
                    if resp.is_rendered:
                        raise ValueError("Cannot modify a response that has already been rendered")

                    if use_block_from_params:
                        use_block_from_params_val = _get_param_from_request(request, "use_block")
                        if use_block_from_params_val is None:
                            return HttpResponse("No `use_block` in request params", status="400")

                        block_to_use = use_block_from_params_val

                    if use_template is not None:
                        resp.template_name = use_template
                    elif block_to_use is not None:
                        rendered_block = render_block_to_string(
                            resp.template_name, block_to_use, context=resp.context_data, request=request
                        )
                        # Create new simple HttpResponse as replacement
                        resp = HttpResponse(content=rendered_block, status=resp.status_code, headers=resp.headers)

            return resp

        return _view

    return decorator


def _get_param_from_request(request, param):
    """
    Checks GET then POST params for specified param
    """
    if param in request.GET:
        return request.GET[param]
    elif request.method == "POST" and param in request.POST:
        return request.POST[param]
    return None
