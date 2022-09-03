POST requests
=============

POST requests (or anything that isn’t GET or HEAD) require some care due to CSRF
protection.

The simplest approach involves creating a form as normal and including the ``{%
csrf_token %}`` template tag.

.. code-block:: html+django

   <h1>Make some monsters!</h1>
   <form>
     {% csrf_token %}
     How many: <input type="number" name="howmany" value="1">
     <button
       hx-post="{% url 'post_form_endpoint' %}"
       hx-trigger="click"
       hx-target="#monsters-created"
       hx-swap="beforeend"
     >Make some!
     </button>

   </form>


In this case the whole of the form, including the CSRF token and other
parameters like ``howmany``, get submitted as part of the POST request, and you
will have no problems.

Example `view code <./code/htmx_patterns/views/posts.py>`_, `template <./code/htmx_patterns/templates/simple_post_form.html>`__

Note that the normal pattern of `POST/redirect/GET
<https://en.wikipedia.org/wiki/Post/Redirect/Get>`_, which is needed to avoid
problems with page refresh and form re-submission, is not needed in this case as
the POST request doesn’t return a full page.

However, in many cases it will be inconvenient to use a form, or you may want to
use controls that wouldn’t normally submit other values, such as links. An easy
solution is to put the token into custom htmx headers, by adding ``hx-headers``
into the ``<body>`` element, usually in a ``base.html`` template:

.. code-block::

   <body hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'>


Example `view code <./code/htmx_patterns/views/posts.py>`_, `template
<./code/htmx_patterns/templates/post_without_form.html>`__, `base template
<./code/htmx_patterns/templates/base.html>`_.
