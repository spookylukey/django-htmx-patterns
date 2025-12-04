Inline partials
===============

.. note::

   Django 6.0 now has built-in support for `Template partials
   <https://docs.djangoproject.com/en/6.0/ref/templates/language/#template-partials>`_!
   The patterns below can almost certainly be improved and simplified, without
   needing the external ``django-render-block`` library, but I haven’t had time
   to do so yet.


Also known as `“template fragments”
<https://htmx.org/essays/template-fragments/>`_.

This improves on the patterns used for `a single view with
separate partial files <./separate_partials_single_view.rst>`_.

Having partial templates in separate files makes the logic harder to follow.
Thanks to `django-render-block
<https://github.com/clokep/django-render-block>`_, however, instead of an
include and separate files, we can put the partials into named blocks within the
main template, and then just render a specific block if we have an htmx request.

In our example, as before, we have a paged list of objects (monsters, in this
case), with a “load more” style paging control at the end. When the button is
pressed, it will replace the paging controls with the next page of items plus
the updated paging controls (which might now say “no more items”).


Template
--------

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



View code — basic version
-------------------------

For htmx requests we must pull out the ``page-and-paging-controls`` block and
render just that bit. The simplest (if slightly ugly) version of our view code
looks like this:


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


Improved view — decorator
-------------------------

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
<./code/htmx_patterns/templates/paging_with_inline_partials.html>`__, `decorator
<./code/htmx_patterns/utils.py>`_

Security issues
---------------

There are potential security issues regarding use of partials (whether
implemented using blocks or separate templates). If you do any kind of
permission checking in the template regarding what information to be displayed,
allowing the client to request a partial response could allow them to bypass the
permission checking. For example:

.. code-block:: html+django

   {% if user.can_view_sensitive_info %}
     {% block sensitive_info_block %}
       <p>{{ sensitive_info }}</p>
     {% endblock %}
   {% endif %}

If the client can trigger a request that would, according to the rules defined
on the view, result in ``sensitive_info_block`` being rendered and returned,
they can bypass the ``user.can_view_sensitive_info`` check.

Mitigation techniques for this problem include:

- Move the permission check from the template into the view code where it cannot
  be bypassed, such that the data is never passed to the template if the user
  doesn’t have permission to see it. The template then just checks “is the data
  present”, rather than “does the user have permission to see it”. This is best
  practice anyway — if the template shouldn’t be displaying data, it shouldn’t
  be given the data.

- Move the permission check conditional into the partial block or template, so
  that it cannot be bypassed.




Block selection in the template
-------------------------------

An issue with the pattern described above is that our view code and template
code have to be changed together in terms of the names of blocks, and we also
can’t fully understand the template without referring to the view to see what
block is going to be rendered. This is a `Locality of Behaviour
<https://htmx.org/essays/locality-of-behaviour/>`_ problem.

We can improve it by having the template itself specify the block that will be
rendered. The value will be defined in the template, and then sent with the htmx
request, so that the view code doesn’t need to be concerned with this at all. We
can achieve this easily with `hx-vals <https://htmx.org/attributes/hx-vals/>`_
and a special parameter ``use_block`` which we will respond to server-side.

Our template now looks like this - the only change is the ``hx-vals`` line:

.. code-block:: html+django

   {% extends "base.html" %}

   {% block body %}
     <h1>List of monsters</h1>

     {% if page_obj.paginator.count == 0 %}
       <p>We have no monsters!</p>
     {% else %}

       {% block page-and-paging-controls %}
         {% for monster in page_obj %}
           <p class="card">{{ monster.name }}</p>
         {% endfor %}

         {% if page_obj.has_next %}
           <p id="paging-area">
             <a
               href="#"
               hx-get="?page={{ page_obj.next_page_number }}"
               hx-vals='{"use_block": "page-and-paging-controls"}'
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

And the view code, which depends on a new parameter ``use_block_from_params``
added to our ``for_htmx`` decorator, is reduced to:

.. code-block:: python

   @for_htmx(use_block_from_params=True)
   def paging_with_inline_partials_improved_lob(request):
       return TemplateResponse(
           request,
           "paging_with_inline_partials_improved_lob.html",
           {
               "page_obj": get_page_by_request(request, Monster.objects.all()),
           },
       )



This is a pretty nice pattern — the complete “template routing” logic is visible
within the template, and can be understood or changed without referring to the
view code. The view code still has to explicitly opt-in to this behaviour, but
is not concerned with the details. The pattern shines even more for complex
cases involving multiple targets and partials — it’s much easier to follow than
using the ``if_hx_target`` routing mentioned above.

Notice how in this case the target of the htmx swap is the ``#paging-area`` DOM
element, while the template that gets rendered “into” it is a larger section of
the template. Other patterns are possible — in some common cases the DOM element
and the template block line up exactly, but they could be completely different.
In all cases you need to pay attention to `hx-swap
<https://htmx.org/attributes/hx-swap/>`_ values.

To better support cases like Out Of Band swaps, we can also allow multiple
blocks to be rendered.

Instead of ``hx-vals``, there are other options like `hx-headers
<https://htmx.org/attributes/hx-headers/>`_ which could be used for indicating
the block to use.

Full code: `view <./code/htmx_patterns/views/partials.py>`_, `template
<./code/htmx_patterns/templates/paging_with_inline_partials_improved_lob.html>`__, `decorator
<./code/htmx_patterns/utils.py>`_



Downsides
~~~~~~~~~

The only significant downside to this pattern that I can see is a potential
security issue — the same security concerns as mentioned above apply, but more
so, since we are now giving the client direct and complete control over which
block gets rendered, and they can choose from any in the template (if they know
the name, and we should assume they do). The same mitigation techniques can be
used, however, so in most cases this wouldn’t put me off the pattern.




Caveats and future work
-----------------------

One effect of this pattern (all versions mentioned on this page) is that it
turns your un-rendered `TemplateResponse
<https://docs.djangoproject.com/en/stable/ref/template-response/>`_ into a
normal `HttpResponse
<https://docs.djangoproject.com/en/stable/ref/request-response/#django.http.HttpResponse>`_.
This has consequences for any code later on (like other decorators or
middleware) that expect a ``TemplateResponse``, and any “post render callbacks”
attached to the ``TemplateResponse``, which now won’t be called. You should
check this isn’t an issue in your case.

Alternatively, perhaps this pattern could be extended by inventing a
``TemplateBlockResponse`` which is lazily rendered in the same way as
``TemplateResponse``. It will need to present the same interface, with methods
like ``render()`` etc.

Or, perhaps ``TemplateResponse`` and other parts of the Django template system
could gain this functionality.
