Headers
=======

The headers sent by htmx are documented `here <https://htmx.org/reference/#request_headers>`_.

Here’s how you access them in Django, in a view that behaves different for htmx
requests compared to normal requests:


.. code-block:: python

   def headers_demo(request):
       if request.headers.get("Hx-Request", False):
           current_url = request.headers["HX-Current-URL"]
           return HttpResponse(f"This is a response to a request sent by htmx from {current_url}<br>")

       return TemplateResponse(request, "headers.html", {})

Example `view code <./code/htmx_patterns/views/headers.py>`_, `template <./code/htmx_patterns/templates/headers.html>`_, `live demo <https://django-htmx-patterns.spookylukey1.repl.co/headers/>`__
