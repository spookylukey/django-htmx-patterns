from django.http.response import HttpResponse
from django.utils.functional import wraps
from render_block import render_block_to_string

# This decorator combines a bunch of functionality, which you might not need all of!

# Future work for this decorator:

# - typing. You could use type hints and static typing checks to ensure that is only used
#   on view functions that return TemplateResponse

# - different ways of matching HTMX requests, if needed.


def for_htmx(*, if_hx_target: str | None = None, template: str | None = None, block: str | None = None):
    """
    If the request is from htmx, then render a partial page, using either:
    - the supplied template name.
    - the specified block name

    If the optional `if_hx_target` parameter is supplied, the
    hx-target header must match the supplied value as well in order
    for this decorator to be applied.
    """
    if block and template:
        raise ValueError("Pass only one of 'template' and 'block'")
    if not (block or template):
        raise ValueError("You must pass one of 'template' and 'block'")

    def decorator(view):
        @wraps(view)
        def _view(request, *args, **kwargs):
            resp = view(request, *args, **kwargs)
            if request.headers.get("Hx-Request", False):
                if if_hx_target is None or request.headers.get("Hx-Target", None) == if_hx_target:
                    if not hasattr(resp, "render"):
                        raise ValueError("Cannot modify a response that isn't a TemplateResponse")
                    if resp.is_rendered:
                        raise ValueError("Cannot modify a response that has already been rendered")

                    if template is not None:
                        resp.template_name = template
                    elif block is not None:
                        rendered_block = render_block_to_string(
                            resp.template_name, block, context=resp.context_data, request=request
                        )
                        # Create new simple HttpResponse as replacement
                        resp = HttpResponse(content=rendered_block, status=resp.status_code, headers=resp.headers)

            return resp

        return _view

    return decorator
