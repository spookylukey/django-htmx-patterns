from django.http import HttpResponse
from django.template.response import TemplateResponse


def headers_demo(request):
    if request.headers.get("Hx-Request", False):
        current_url = request.headers["HX-Current-URL"]
        return HttpResponse(f"This is a response to a request sent by htmx from {current_url}<br>")

    return TemplateResponse(request, "headers.html", {})
