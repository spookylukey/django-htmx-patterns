Form validation
===============

Django has an awesome `form <https://docs.djangoproject.com/en/stable/topics/forms/>`_ abstraction that allows us to define all the input handling, validation and HTML in a single place, so that rendering a complete form can be as simple as:

.. code-block:: html+django

   <form method="POST" action=".">
     {{ form }}
     <button type="submit">Submit</button>
   </form>


Plus we can make the form a `ModelForm <https://docs.djangoproject.com/en/stable/topics/forms/modelforms/>`_ so that we can re-use our model definition to create a form automatically, with constraints etc. respected.

But now we want some htmx goodness, so that either:

- the submit button will do a server call without leaving the page, updating the form inline

- or, as the user types, we validate each field they change one by one, so that they don’t have to wait until the end to see problems with the form.

The first of these is fairly standard htmx that you can do with the techniques
shown already; the second has more moving parts, and is what this page deals
with.

In addition, we want this to work in the real world, which means that we may need to significantly change the HTML of a form to match our custom design or what our CSS framework/library expects the HTML to look like.

But we don’t want to give up anything Django has given us! No compromise on UX **or** DX!

So let’s go!

But first
---------

Actually before we start, ask yourself “Do I really need this?”. HTML5 already provides lots of `form validation features <https://developer.mozilla.org/en-US/docs/Learn/Forms/Form_validation>`_. In Django and you can emit these attributes by:

- using `Field <https://docs.djangoproject.com/en/stable/ref/forms/fields/>`_ arguments like ``required`` to set the HTML ``required`` attribute.
- choosing the right `widget <https://docs.djangoproject.com/en/stable/ref/forms/widgets/>`_ (or a custom widget),
- or using `Widget.attrs <https://docs.djangoproject.com/en/stable/ref/forms/widgets/#django.forms.Widget.attrs>`_ to set things like the HTML ``pattern`` attribute.

If you can lean on HTML, do so! If you need additional server-side validation and want it to appear immediately, read on.

Form HTML and styling
---------------------

Rather than focus on just the htmx/Django techniques, I’m doing a fuller example, partly because real-world concerns often affect the solution. In particular, styling of a form normally affects the HTML, and that affects how we can break it up in order to update fragments via htmx, so you actually need to start with styling and form layout. If you just want to the htmx details, skip down to the “htmx it!” heading.

I’ll include some of the main things you’ll need on this page, with some brief notes for the techniques used. For full details the code is available in the `code folder <./code/>`_ as always.

For styling this demo, I chose to use `Bulma <https://bulma.io/>`_ as an example of a popular, real world CSS framework that has a decent story regarding form rendering, but one I haven’t actually used before. I didn’t pick because I knew it was easy, to make this more realistic! Our aim is that we’ll be able to do the styling work once, and re-use it for all forms in our project. For a different CSS framework, most of what is written here should apply.

Bulma
~~~~~

First, we grab the Bulma CSS and add it somewhere in our repo’s static files:

.. code-block:: shell

   curl https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.css > my_app/static/vendor/bulma.scss

(We could also get a minimised version, or get the Sass source files, but we don’t actually need them for this example).

Note that I’ve saved the CSS file to an SCSS extension, which will be useful later.

Django/Python deps
~~~~~~~~~~~~~~~~~~

I’m going to use Sass to help with CSS, and the easiest way to do that in Django, avoiding the use of nodejs and other things, is to use libsass, is which pip-installable via `libsass-python <https://github.com/sass/libsass-python>`_. We can use it from Django by installing `django-libsass <https://github.com/torchbox/django-libsass>`_ and using `django-compressor <https://django-compressor.readthedocs.io/en/latest/>`_. For help rendering forms, we’ll also use `django-widget-tweaks <https://github.com/jazzband/django-widget-tweaks>`_.

.. code-block:: shell

   pip install django-compressor django-libsass django-widget-tweaks

We now have have a few tweaks to make to our settings:

.. code-block:: python

   INSTALLED_APPS = [
       ...
       "django.forms",
       "compressor",
       "widget_tweaks",
   ]
   STATICFILES_FINDERS = (
       "django.contrib.staticfiles.finders.FileSystemFinder",
       "django.contrib.staticfiles.finders.AppDirectoriesFinder",
       # other finders..
       "compressor.finders.CompressorFinder",
   )
   STATIC_ROOT = BASE_DIR / "_static"

   COMPRESS_ENABLED = True
   COMPRESS_PRECOMPILERS = [("text/x-scss", "django_libsass.SassCompiler")]

Base templates
~~~~~~~~~~~~~~

We need something like this now in our ``base.html``:

.. code-block:: html

   {% load static %}
   {% load compress %}
   <!DOCTYPE html>
   <html lang="en">
     <head>
       {% compress css %}
         <link rel="stylesheet" type="text/x-scss" href="{% static 'css/base_bulma.scss' %}">

       {% endcompress %}

Our ``base_bulma.scss`` starts something like this:

.. code-block:: scss

   @import "../vendor/bulma.scss";

   // Our styles here …
   body {
       padding: 1rem;
   }
   // …

Form renderer
~~~~~~~~~~~~~

Next, we need some custom form templates. This is needed not just to apply our custom HTML/CSS stuff, but also to be able to do rendering of the form on a field-by-field basis, which we’ll need later.

In this example I’m going to isolate changes so that they only affect the forms we want, rather than all forms, so I’m going to do it with a custom form renderer:

.. code-block:: python

   from django.forms.renderers import TemplatesSetting


   class BulmaFormRenderer(TemplatesSetting):
       form_template_name = "forms/bulma/div.html"


We are using our own form templates, to minimize disruption to other forms. You could instead override the provided ``django/forms/*.html`` templates by adding templates with those names to your own templates directories, but that will affect all forms.

We then create a form mixin that specifies this renderer, plus some other small tweaks:

.. code-block:: python

   class BulmaFormMixin:
       default_renderer = BulmaFormRenderer()

       def __init__(self, *args, **kwargs) -> None:
           # We don’t want ':' as a label suffix:
           return super().__init__(*args, label_suffix="", **kwargs)


We can then use this in a form like:

.. code-block:: python

   class CreateMonsterForm(BulmaFormMixin, Form):
      ...


Form templates
~~~~~~~~~~~~~~

We can use the builtin `django/forms/div.html <https://github.com/django/django/blob/main/django/forms/templates/django/forms/div.html>`_ template as a starting point for our main form template. We need to make a bunch of changes to fit the HTML to what Bulma expects. So far it looks like this:

.. code-block:: html+django

   {% load widget_tweaks %}
   {{ errors }}
   {% if errors and not fields %}
     <div>{% for field in hidden_fields %}{{ field }}{% endfor %}</div>
   {% endif %}
   {% for field, errors in fields %}
     <div{% with classes=field.css_classes %} class="field is-horizontal {{ classes }}"{% endwith %}>
       {% if field.label %}
         <div class="field-label is-normal">
           {{ field.label_tag }}
         </div>
       {% endif %}
       <div class="field-body">
         {% with error_class=errors|yesno:"is-danger,," %}
           <div class="field">
             <div class="control">
               {% if field|widget_type == "select" %}
                 <div class="select {{ error_class }}">
                   {{ field }}
                 </div>
               {% else %}
                 {{ field|add_class:error_class }}
               {% endif %}
             </div>
             {% if field.help_text %}
               <p class="help">{{ field.help_text|safe }}</p>
             {% endif %}
             {% if errors %}
               <div class="help is-danger">
                 {{ errors }}
               </div>
             {% endif %}
           </div>
         {% endwith %}
       </div>

       {% if forloop.last %}
         {% for field in hidden_fields %}{{ field }}{% endfor %}
       {% endif %}
     </div>
   {% endfor %}
   {% if not fields and not errors %}
     {% for field in hidden_fields %}{{ field }}{% endfor %}
   {% endif %}

Later on we are going to pull out the body of this into a partial.

There is a `bit of SCSS <./code/htmx_patterns/static/css/base_bulma.scss>`_ we’ve added to support this.

I won’t go over all of the above in detail, but here are some of the things we’ve used:

- We’re using the ``widget_type`` template filter from django-widget-tweaks to be able to render different HTML for different types of widgets – in this case, an extra ``<div class="select">`` is needed for ``<select>`` elements.

- We’re using the ``add_class`` template filter, again from django-widget-tweaks, to be able to customise the HTML for widgets for the case of adding a class to mark errors (in this case applying an ``is-danger`` class).

- For some other CSS/HTML needs, I’ve gone for a different technique. Normally, for `Bulma styled inputs <https://bulma.io/documentation/form/input/>`_ and `checkboxes <https://bulma.io/documentation/form/checkbox/>`_ etc., you need HTML like ``<input type="text" class="input">`` and  ``<input type="checkbox" class="checkbox">`` etc. This is tedious to specify in a template, but with Sass we have a different technique available, based on the `@extend <https://sass-lang.com/documentation/at-rules/extend>`_ rule. We can write rules like this:

  .. code-block:: scss

     @import "../vendor/bulma.scss";

     .field-body {
         input[type=text], input[type=email], input[type=password], input[type=date] {
             @extend .input;
         }
         input[type=checkbox] {
             @extend .checkbox;
         }
     }

  This basically means “treat all ``input[type=text]`` elements inside a ``.field-body`` element as if it had the ``.input`` class applied” etc. Sass does a bunch of magic to make this work, including applying related rules like ``.input:focus``.

  A neat thing about this technique is that it works even if our CSS library doesn’t provide Sass source – here we just renamed the CSS to SCSS and ``@import`` -ed it. If you have Sass source available, providing mixins and variables etc, you can have more control, and also produce smaller HTML.

  This same technique is used to add styling to the ErrorList object displayed as ``{{ errors }}`` at the top of the form, without having to override the HTML rendering or duplicate CSS.

- We can control some of the HTML by adding tweaks at the widget level defined in the form e.g. to make our date input render as ``<input type="date">`` instead of ``type="text"`` we do something like:

  .. code-block:: python

     class CreateMonsterForm(ModelForm):
         class Meta:
             fields = [..., "date_of_birth"]
             widgets = {
                 "date_of_birth": DateInput(attrs={"type": "date"}),
             }

  or:

  .. code-block:: python

     class CreateMonsterForm(ModelForm):
         date_of_birth = DateField(widget=DateInput(attrs={"type": "date"}))

  You can also added ``class`` attributes as part of ``attrs`` if you want, but I think that’s not so neat as keeping that in the template.

Form view
~~~~~~~~~

With all that in place, we can write a very simple standard form view:

.. code-block:: python

   def create_monster(request):
       if request.method == "POST":
           form = CreateMonsterForm(request.POST)
           if form.is_valid():
               monster = form.save()
               messages.info(request, f"Monster {monster.name} created. You can make another.")
               return redirect(".")
       else:
           form = CreateMonsterForm()
       return TemplateResponse(request, "create_monster.html", {"form": form})


And the template achieves our aim of being able to do just ``{{ form }}`` for rendering:

.. code-block:: html+django

  <h1 class="title">Add a monster</h1>
  <form method="POST" action=".">
    {% csrf_token %}

    {% if form.errors %}
      <p>There were some problems with your input:</p>
    {% endif %}
    {{ form }}

    <div class="field is-horizontal">
      <div class="field-label">
      </div>
      <div class="field-body">
        <button class="is-primary" type="submit">Add</button>
      </div>
    </div>
  </form>

Result:

.. image:: images/bulma_form.png

htmx it!
--------

TODO!

Tips
----
Inherit from TemplateSettings, not DjangoTemplates, to get TEMPLATES customisations, and also to get reloading of templates to work with dev server, which seems not to happen for DjangoTemplates
