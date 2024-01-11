Django + htmx patterns
======================

This repo is a rough-and-ready compilation of the patterns I’m using and
developing when writing `Django <https://www.djangoproject.com/>`_ projects that
use `htmx <https://htmx.org/>`_, with complete example code.

The docs are intended to be viewed on GitHub:
https://github.com/spookylukey/django-htmx-patterns/ and the code can be run
locally if needed.

My aims are to document and share:

1. The basic patterns and control flow needed
2. Some enhancements we can make with a few utilities

The code presented depends only on Django and htmx, unless otherwise noted. I
won’t be packaging it up as a library. It is instead being released into the
public domain, and you are encouraged to copy-paste it for your own needs. (See
the “Approach” docs for why).

There are some Django packages that provide shortcuts for some of the things
mentioned here, such as `django-htmx
<https://github.com/adamchainz/django-htmx>`_, but I won’t be using any of them
for the sake of clarity.


Contents
--------

* `Approach <./approach.rst>`_
* `Base template <./base_template.rst>`_
* `Headers <./headers.rst>`_
* `Post requests <./posts.rst>`_
* `Partials using separate templates <./separate_partials.rst>`_
* `Separate partials with a single view <./separate_partials_single_view.rst>`_
* `Inline partials <./inline_partials.rst>`_
* `Single view with actions combined <./actions.rst>`_
* `View restart <./view_restart.rst>`_
* `django-functest patterns <./django_functest.rst>`_
* `Modal dialogs <./modals.rst>`_
* `Form validation <./form_validation.rst>`_

This is a work in progress, I’ll try to keep it up to date. PRs welcome.

tl;dr
-----

The biggest contributions in this repo are:

* `inline partials with block selection in the template
  <https://github.com/spookylukey/django-htmx-patterns/blob/master/inline_partials.rst#block-selection-in-the-template>`_.

  This is a pattern which allows you to keep the parts of the page together for
  great “locality of behaviour”, and avoid the view code having to know anything
  about which template fragments/partials are being used. Template code changes
  for htmx are usually a matter of wrapping some parts of a template in a Django
  template ``block`` and adding standard htmx attributes. View code changes for
  htmx are often just adding a single decorator on the view function:
  ``@for_htmx(use_block_from_params=True)``.

  This pattern makes a huge difference to htmx usability in Django.

* `full example of field-by-field htmx form validation <./form_validation.rst>`_, while keeping Django’s Form abstraction and all its benefits.

* `nice patterns for doing modals <./modals.rst>`_


Requirements
------------

* `Django <https://www.djangoproject.com/>`_
* `htmx <https://htmx.org/>`_ (see `Base template <./base_template.rst>`_ for suggested installation docs)
* The nicest patterns here require `django-render-block <https://github.com/clokep/django-render-block>`_::

    pip install django-render-block


Monsters
--------

My example code includes sad and happy monsters that can be hugged or kicked to
change their state. Please note that I do not endorse the kicking of monsters,
nor advise hugging them.


Code folder
-----------

In the `code folder <./code/>`_ is a demo app which has full working examples of
everything in the docs.

To install locally, create and activate a virtualenv, and then do::

  cd code
  pip install -r requirements.txt
  python manage.py migrate
  python manage.py runserver


Feedback
--------

Your feedback is very welcome! Star this repo if you like it, and please share
ideas on `discussions
<https://github.com/spookylukey/django-htmx-patterns/discussions>`_.

Links
-----

Some other good htmx resources:

* `How to create a Django form (using HTMX) in 90 seconds 🐎 <https://www.photondesigner.com/articles/submit-async-django-form-with-htmx>`_ - short, simple post (and video) showing how to start using HTMX with Django very quickly 
* `How to use htmx in Django <https://www.mattlayman.com/blog/2021/how-to-htmx-django/>`_ - tutorial blog post
* `django-htmx <https://github.com/adamchainz/django-htmx>`_ - utility library with helpful docs
* `django-htmx-fun <https://github.com/guettli/django-htmx-fun>`_ - example application with Django/htmx
* `django-siteajax <https://github.com/idlesign/django-siteajax>`_ - has some similar ideas to this repo

If you liked this repo, you might also be helped by some of my other resources:

* `django-functest <https://github.com/django-functest/django-functest>`_
* `Django Views — The Right Way
  <https://spookylukey.github.io/django-views-the-right-way/>`_
