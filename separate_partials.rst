Separate partial templates
==========================

Often when using htmx, you will want responses to htmx requests to be “partial
templates” i.e. HTML fragments from a large page. The simplest way to do this in
Django is to:

1. pull out the template into a separate file
2. use an `include
   <`https://docs.djangoproject.com/en/stable/ref/templates/builtins/#include>`_
   in the parent template
3. respond to the htmx request by using the partial template only.


The below example is for a page that allows us to individually toggle the state
of items in a list, loading only the individual part of the page.

In our example, we are making monsters either happy or sad!

The templates look like this:

Main template: toggle_with_separate_partials.html

.. code-block:: html+django

   {% extends "base.html" %}

   {% block body %}
     <h1>Are the monsters happy or sad?</h1>

     {% for monster in monsters %}
       {% include "_toggle_item_partial.html" %}
     {% endfor %}

   {% endblock %}

Partial template ``_toggle_item_partial.html``:

.. code-block:: html+django

   <div class="card" id="monster-{{ monster.id }}">
     <p>{{ monster.name }} is {% if monster.is_happy %}happy{% else %}sad{% endif %}</p>

     <button hx-post="{% url 'toggle_item' monster_id=monster.id %}"
             hx-target="#monster-{{ monster.id }}"
             hx-swap="outerHTML"
             >{% if monster.is_happy %}Kick it!{% else %}Hug it!{% endif %}
     </button>
   </div>

We also have two separate views, which look like this:

.. code-block:: python

   def toggle_with_separate_partials(request):
       return TemplateResponse(
           request,
           "toggle_with_separate_partials.html",
           {
               "monsters": Monster.objects.all(),
           },
       )


   @require_POST
   def toggle_item(request, monster_id):
       monster = Monster.objects.get(id=monster_id)
       monster.toggle_happiness()
       return TemplateResponse(request, "_toggle_item_partial.html", {"monster": monster})

(Instead of toggling, we could also have chosen to include a parameter in the
POST data to indicate which state to change to).

Example `view code <./code/htmx_patterns/views/partials.py>`_, `main template <./code/htmx_patterns/templates/toggle_with_separate_partials.html>`_, `partial template <./code/htmx_patterns/templates/_toggle_item_partial.html>`_

Possible improvements to this pattern include:

- `Inline partials <./inline_partials.rst>`_.
- `Single view with actions combined <./actions.rst>`_

Security issues
---------------

The same potential security issues apply here as described for `inline partials
<./inline_partials.rst#security-issues>`_.
