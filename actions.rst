Single view with actions combined
=================================

Sometimes with htmx you may have one view to render the whole page, and separate
views to manage any POST actions (see the `toggle_with_separate_partials and
toggle_item view functions <./code/htmx_patterns/views/partials.py>`_ for an
example of this). Sometimes, however, it is more convenient and logical to
define those actions with a single view.

The pattern I use here is almost identical to the code I would write if I wasn’t
using htmx at all. Consider a page that shows an item, and has a couple of
buttons to control it - first without htmx:

View code:

.. code-block:: python

   def monster_detail(request: HttpRequest, monster_id: int):
       monster: Monster = get_object_or_404(Monster.objects.all(), id=monster_id)

       if request.method == "POST":
           if "kick" in request.POST:
               monster.kick()
           elif "hug" in request.POST:
               monster.hug()
           return HttpResponseRedirect("")

       return TemplateResponse(
           request,
           "monster_detail.html",
           {
               "monster": monster,
           },
       )


Notice how we can have multiple actions, as above, by detecting different
parameters present in the POST request. The HTML to make this work simply needs
a POST form with two ``<button type="submit">`` or ``<input type="submit">``
elements with different ``name`` attributes (because the clicked button’s
``name`` attribute will be included in the POST data):

.. code-block:: html

    <form
      method="POST"
      action=""
      >
      {% csrf_token %}
      {% if monster.is_happy %}
        <p>{{ monster.name }} is happy.</p>
        <button name="kick" type="submit">Kick it!</button>
      {% else %}
        <p>{{ monster.name }} is sad.</p>
        <button name="hug" type="submit">Hug it!</button>
      {% endif %}

    </form>


Here, the available button actions depend on the current ``is_happy`` state, and
are mutually exclusive, but that doesn’t have to be the case.

Nice things about this include:

- less “wiring” compared to using multiple views. You can just do ``action=""``,
  and ``HttpResponseRedirect("")`` and everything gets posted/redirected to the
  same URL.

  Instead of the empty string ``""`` (which represents the empty relative URL,
  meaning “the current URL”), often you will see ``"."``. The only difference is
  that the relative URL ``.`` represents the current path **without query
  parameters**, so it will cause the query string to be stripped, which you may
  or may not want, while the empty URL (sometimes spelled as a single space in
  ``action=" "``) includes the whole of the current location.

- Less boilerplate and repetition of the initial parts of the view function.

- The single “page” is represented by a single view function. If you have
  multiple views for this, those views are usually tightly coupled together, so
  it helps when the source code reflects this, and you achieve better locality
  of behaviour — similar to how template fragments/inline partials achieve the
  same thing at the template layer.

To htmx-ify this, we have a few very small tweaks to make:

* In the template, add some blocks (or partials) for the parts we need to render separately.
* In the template, add some ``hx-`` attributes
* Don’t do a redirect for htmx requests (or use a `view restart <./view_restart.rst>`_)
* For the htmx POST request, render a part of the template.

Here I will do this using our previous `for_htmx decorator with inline partials <./inline_partials.rst>`_ pattern.

New view code:

.. code-block:: python

   @for_htmx(use_block_from_params=True)
   def monster_detail(request: HttpRequest, monster_id: int):
       monster: Monster = get_object_or_404(Monster.objects.all(), id=monster_id)

       if request.method == "POST":
           if "kick" in request.POST:
               monster.kick()
           elif "hug" in request.POST:
               monster.hug()
           if not is_htmx(request):
               return HttpResponseRedirect("")

       return TemplateResponse(
           request,
           "monster_detail.html",
           {
               "monster": monster,
           },
       )


New HTML:

.. code-block:: html

  {% block monster-form %}
    <form
      method="POST"
      action=""
      id="monster-form"
      hx-post=""
      hx-target="#monster-form"
      hx-swap="outerHTML"
      hx-vals='{"use_block": "monster-form"}'
      >
      {% csrf_token %}
      {% if monster.is_happy %}
        <p>{{ monster.name }} is happy.</p>
        <button name="kick" type="submit">Kick it!</button>
      {% else %}
        <p>{{ monster.name }} is sad.</p>
        <button name="hug" type="submit">Hug it!</button>

      {% endif %}

    </form>
  {% endblock %}


Here, I’ve also ensured that the page continues to work even if the htmx library doesn’t load client side.

Full code: `view <./code/htmx_patterns/views/actions.py>`_, `template <./code/htmx_patterns/templates/multiple_actions.html>`__

For improvements to this pattern, see:

* `View restart pattern <./view_restart.rst>`_
