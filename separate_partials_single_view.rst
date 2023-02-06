Separate partials with a single view
====================================

In contrast to the `first example <separate_partials.rst>`_, sometimes it’s most
convenient to use a single view for both the full and the htmx view when using
partials. A common example is paginated views.

Here, we typically want to display “more items”, loading more down the page, or
we might want to display “next page”, swapping out the existing set of items. In
this example I’m doing the first. This means that the paging control block gets
replaced by the next page plus the next paging control.

The HTML looks like this:

Main template:

.. code-block:: html+django


   {% extends "base.html" %}

   {% block body %}
     <h1>List of monsters</h1>

     {% if page_obj.paginator.count == 0 %}
       <p>We have no monsters!</p>
     {% else %}
       {% include "_page_and_paging_controls.html" %}
     {% endif %}

   {% endblock %}


``_page_and_paging_controls.html`` partial:

.. code-block:: html+django

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
   </div>


Our single view function looks like this:


.. code-block:: python

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


However, this pattern comes up a lot, and ``TemplateResponse`` has a very nice
feature: you can change the template that is used before the template actually
gets rendered.

This means we can move the ``if`` statements into a ``for_htmx`` decorator that
wraps up the logic for us - see `implementation
<./code/htmx_patterns/utils.py>`_ – so it looks quite a lot neater like this:


.. code-block:: python

   @for_htmx(use_template="_page_and_paging_controls.html")
   def paging_with_separate_partials_improved(request):
       return TemplateResponse(
           request,
           "paging_with_separate_partials.html",
           {
               "page_obj": get_page_by_request(request, Monster.objects.all()),
           },
       )


This decorator has some other tricks — it can match on specific ``Hx-Target``
headers to choose different templates, which can be useful if you are doing more
advanced things, like both htmx search and paging in the same view.

Example `view code <./code/htmx_patterns/views/partials.py>`_, `main template <./code/htmx_patterns/templates/paging_with_separate_partials.html>`_, `partial template <./code/htmx_patterns/templates/_page_and_paging_controls.html>`_

Improvements to this pattern include:

- `inline partials <./inline_partials.rst>`_.

Variants on this pattern include:

- `Single view with actions combined <./actions.rst>`_ (where we also include
  processing of POST in the single view, as well as multiple templates).


Security issues
---------------

The same potential security issues apply here as described for `inline partials
<./inline_partials.rst#security-issues>`_.
