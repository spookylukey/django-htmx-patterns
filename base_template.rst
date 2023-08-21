Base template
=============

To get going, you’ll need to install htmx somehow into your template.

Most likely, you’ll want to put it into a base template. There are lots of
options for the exact details of how to do this in Django (depending on if you
are using bundlers for your static assets etc.), but the simplest is like one
of the following in your ``base.html`` template (or whatever you have called it):

Using the CDN:

.. code-block:: html+django

   <html>
     <head>
       <script defer src="https://unpkg.com/htmx.org@1.9.4" integrity="sha384-zUfuhFKKZCbHTY6aRR46gxiqszMk5tcHjsVFxnUo8VMus4kHGVdIYVbOYYNlKmHV" crossorigin="anonymous"></script>
       ...


(You should specify the version you want, see `htmx installation docs <https://htmx.org/docs/#installing>`_)

Or, download the ``htmx.min.js`` into one of your folders for `static assets in
your Django projects
<https://docs.djangoproject.com/en/stable/howto/static-files/>`_, and use like
this in your ``base.html``:


.. code-block:: html+django

   {% load static %}
   <html lang="en">
     <head>
       <script defer src="{% static 'js/htmx.min.js' %}"></script>

I normally include the version number in the file name when I do this.

`Example template <./code/htmx_patterns/templates/base.html>`_.

Bundlers
--------

You can use bundlers like webpack etc. I usually use
`django-compressor <https://django-compressor.readthedocs.io/en/stable/>`_, so my template ends up looking like:

.. code-block:: html+django

  {% compress js %}
    <script type="text/javascript" defer src="{% static "js/htmx.min.js" %}"></script>
    <script type="text/javascript" defer src="{% static "js/mystuff.js" %}"></script>
  {% endcompress %}


Note the use of ``defer`` (see the `docs on script async/defer <https://html.spec.whatwg.org/multipage/scripting.html#attr-script-defer>`_). By bundling my own code with htmx, and putting it after it, I know that htmx will have loaded before my own code executes, in case I need to use the `htmx Javascript API <https://htmx.org/reference/#api>`_. In development I set `COMPRESS_ENABLED <https://django-compressor.readthedocs.io/en/latest/settings.html#django.conf.settings.COMPRESS_ENABLED>`_ to ``True``. To aid debugging, I don’t run minify filters in development, and use unminified 3rd party libs if necessary.

Other
-----

You should also see the notes about `post requests <./posts.rst>`_ for things
you might want in your base templates.
