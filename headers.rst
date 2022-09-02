Headers
=======

The headers sent by HTMX are documented `here <https://htmx.org/reference/#request_headers>`_.

Here’s how you access them in Django, in a view that behaves different for HTMX
requests compared to normal requests:


.. code-block:: python

   def headers_demo(request):
       if request.headers.get("Hx-Request", False):
           current_url = request.headers["HX-Current-URL"]
           return HttpResponse(f"This is a response to a request sent by HTMX from {current_url}<br>")

       return TemplateResponse(request, "headers.html", {})

Example `view code <./code/htmx_patterns/views/headers.py>`_, `template <./code/htmx_patterns/templates/headers.html>`_
