Inline partials with Jinja2
===============

For this, we assume you have read the article about `inline partials <./inline-partials.st>`_.

If you are using Jinja2 as a template engine for Django, there are some solutions that offer template fragment features:

- https://pypi.org/project/jinja2-fragments/0.1.0/
- https://github.com/mikeckennedy/jinja_partials

Both of them do not work well with the way jinja2 is integrated into Django. They have the following drawbacks:

- You are giving up on the Jinja2 environment that Django configures for you.
- You need to make sure that all the paths are set in the right way so that Jinja2 finds your templates.
- You cannot use `TemplateResponse()` any longer.
- You need to adjust all your routes quite heavily to make use of the new render logic.

We propose another solution: write your own Jinja2 template backend. It is not a lot of code, can be copied in large parts from the existing Jinja2 backend that Django includes, and provides a lot of flexibility while staying in the common workflows that Django offers.

Let's start with your template configuration if you are using Jinja2. We will need to make some minor adjustments, so it is good to know how it should approximately look like before:

.. code-block:: python

    TEMPLATES = [
        # ...
        {
            "BACKEND": "django.template.backends.jinja2.Jinja2",
            "DIRS": [os.path.join(PROJECT_DIR, "jinja2")],
            "APP_DIRS": True,
            "OPTIONS": {"environment": "your_app.jinja2.environment"},
        },
    ]

To make working with Django + Jinja2 + Fragments easier we have written a custom template backend that is heavily inspired by the `default Django Jinja2 backend <https://github.com/django/django/blob/0dd29209091280ccf34e07c9468746c396b7778e/django/template/backends/jinja2.py>`_.

.. code-block:: python

    import jinja2
    from django.template import TemplateDoesNotExist, TemplateSyntaxError
    from django.template.backends.jinja2 import Jinja2, get_exception_info, Template


    class Jinja2WithFragments(Jinja2):
    def from_string(self, template_code):
        return FragmentTemplate(self.env.from_string(template_code), self)

    def get_template(self, template_name):
        try:
            return FragmentTemplate(self.env.get_template(template_name), self)
        except jinja2.TemplateNotFound as exc:
            raise TemplateDoesNotExist(exc.name, backend=self) from exc
        except jinja2.TemplateSyntaxError as exc:
            new = TemplateSyntaxError(exc.args)
            new.template_debug = get_exception_info(exc)
            raise new from exc


    class FragmentTemplate(Template):
    """Extend the original jinja2 template so that it supports fragments."""

    def render(self, context=None, request=None):
        from django.template.backends.utils import csrf_input_lazy, csrf_token_lazy

        if context is None:
            context = {}
        if request is not None:
            context["request"] = request
            context["csrf_input"] = csrf_input_lazy(request)
            context["csrf_token"] = csrf_token_lazy(request)

            for context_processor in self.backend.template_context_processors:
                context.update(context_processor(request))

        try:
            if "RENDER_BLOCKS" in context:
                bctx = self.template.new_context(context)
                return "".join(
                    [self.template.blocks[bn](bctx) for bn in context["RENDER_BLOCKS"]]
                )
            return self.template.render(context)
        except jinja2.TemplateSyntaxError as exc:
            new = TemplateSyntaxError(exc.args)
            new.template_debug = get_exception_info(exc)
            raise new from exc

You need to configure your Django settings to use this new template engine. Create a `jinja2.py` file inside your `your_app` folder and place the code from above in this file. Also make sure that your environment is also in this file or that you adjust the path to your environment.

.. code-block:: python

    TEMPLATES = [
        # ...
        {
            "BACKEND": "your_app.jinja2_backend.Jinja2WithFragments",
            "DIRS": [os.path.join(PROJECT_DIR, "jinja2")],
            "APP_DIRS": True,
            "OPTIONS": {"environment": "your_app.jinja2.environment"},
        },
    ]


If you define any block in your templates:

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

You can now choose to render only a certain block quite easily via:

.. code-block:: python

   def paging_with_inline_partials(request):
       template_name = "paging_with_inline_partials.html"
       context = {
           "page_obj": get_page_by_request(request, Monster.objects.all()),
       }

       if request.headers.get("Hx-Request", False):
           context["RENDER_BLOCKS"] = ["page-and-paging-controls"]

       return TemplateResponse(request, template_name, context)

In theory, you could also render multiple blocks at the same time even though we do not yet see the usecase for this.

Our template backend will look for the key `RENDER_BLOCKS` inside the context and if it is available, it will switch to rendering only the blocks that are specified in the variable.
