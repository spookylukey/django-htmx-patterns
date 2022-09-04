Inline partials
===============

This improves on the patterns used for `a single view with
separate partial files <./separate_partials_single_view.st>`_.

Having partial templates in separate files makes the logic harder to follow.
Thanks to `django-render-block
<https://github.com/clokep/django-render-block>`_, however, instead of an
include and separate files, we can put the partials into named blocks within the
main template, and then just render that block if we have an htmx request.

In our example, as before, we have a paged list of objects (monsters, in this
case), with a “load more” style paging control at the end. When the button is
pressed, it will replace the paging controls with the next page of items plus
the updated paging controls (which might now say “no more items”).

So our template looks like this:

.. code-block:: html+django

   {% extends "base.html" %}

   {% block body %}
     <h1>List of monsters</h1>

     {% if page_obj.paginator.count == 0 %}
       <p>We have no monsters at all!</p>
     {% else %}

       {% block page-and-paging-controls %}
         {% for monster in page_obj %}
           <p class="card">{{ monster.name }}</p>
         {% endfor %}

         {% if page_obj.has_next %}
           <p id="paging-area">
             <a href="#"
               hx-get="?page={{ page_obj.next_page_number }}"
               hx-target="#paging-area"
               hx-swap="outerHTML"
             >Load more</a>
           </p>
         {% else %}
           <p>That's all of them!</p>
         {% endif %}
       {% endblock %}

     {% endif %}

   {% endblock %}


For htmx requests we must pull out the ``page-and-paging-controls`` block and
render just that bit. So, the long version of our view code looks like this:


.. code-block:: python

   from render_block import render_block_to_string

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

However, thanks to the fact that ``TemplateResponse`` doesn’t immediately render
itself, but just stores the template and context to be rendered later, we can
instead implement all the logic relating to htmx and ``render_block_to_string``
using a `decorator <./code/htmx_patterns/utils.py>`_, which I’m calling
``for_htmx``.

Now our view code is now both more readable and much shorter, like this:

.. code-block:: python

   @for_htmx(use_block="page-and-paging-controls")
   def paging_with_inline_partials_improved(request):
       return TemplateResponse(
           request,
           "paging_with_inline_partials.html",
           {
               "page_obj": get_page_by_request(request, Monster.objects.all()),
           },
       )

For some cases where I’m doing different htmx calls within the same page (e.g. a
page that uses htmx for both search and paging), I’ve found that I need to
choose the block based on the ``Hx-Target`` header. So the ``for_htmx``
decorator takes an extra ``if_hx_target`` keyword arguments for that e.g.:


.. code-block:: python

   @for_htmx(if_hx_target="search-results", use_block="search-result-block")
   @for_htmx(if_hx_target="paging-controls", use_block="page-and-paging-controls")
   def my_view(request):
       ...


This approach can be extended with other functionality, depending on your use cases.


Full code: `view <./code/htmx_patterns/views/partials.py>`_, `template
<./code/htmx_patterns/templates/paging_with_inline_partials.html>`_, `decorator
<./code/htmx_patterns/utils.py>`_.

Caveats and future work
-----------------------

One effect of this pattern is that it turns your un-rendered `TemplateResponse
<https://docs.djangoproject.com/en/stable/ref/template-response/>`_ into a normal
`HttpResponse
<https://docs.djangoproject.com/en/stable/ref/request-response/#django.http.HttpResponse>`_.
This has consequences for any code later on (like other decorators or
middleware) that expect a ``TemplateResponse``, and any “post render callbacks”
attached to the ``TemplateResponse``, which now won’t be called. You should
check this isn’t an issue in your case.

Alternatively, perhaps this pattern could be extended by inventing a
``TemplateBlockResponse`` which is lazily rendered in the same way as
``TemplateResponse``. It will need to present the same interface, with methods
like ``render()`` etc.
