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
       <script defer src="https://unpkg.com/htmx.org@1.8.0" integrity="sha384-cZuAZ+ZbwkNRnrKi05G/fjBX+azI9DNOkNYysZ0I/X5ZFgsmMiBXgDZof30F5ofc" crossorigin="anonymous"></script>
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


`Example template <./code/htmx_patterns/templates/base.html>`_.

You should also see the notes about `post requests <./posts.rst>`_ for things
you might want in your base templates.
