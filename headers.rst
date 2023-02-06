Headers
=======

The headers sent by htmx are documented `here <https://htmx.org/reference/#request_headers>`_.

The following code show how you access them in Django. This view behaves differently
for htmx requests compared to normal requests:


.. code-block:: python

   def headers_demo(request):
       if request.headers.get("Hx-Request", False):
           current_url = request.headers["Hx-Current-URL"]
           return HttpResponse(f"This is a response to a request sent by htmx from {current_url}<br>")

       return TemplateResponse(request, "headers.html", {})

Example `view code <./code/htmx_patterns/views/headers.py>`_, `template <./code/htmx_patterns/templates/headers.html>`_


Links
-----

* The django-htmx package has `a convenience middleware to make it easier to
  read htmx headers
  <https://django-htmx.readthedocs.io/en/latest/middleware.html>`_.
