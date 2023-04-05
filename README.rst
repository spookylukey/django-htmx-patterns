Django + htmx patterns
======================

This repo is a rough-and-ready compilation of the patterns I’m using and
developing when writing `Django <https://www.djangoproject.com/>`_ projects that
use `htmx <https://htmx.org/>`_.

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
* `Modals <./modals.rst>`_

This is a work in progress, I’ll try to keep it up to date. PRs welcome.

Monsters
--------

My example code includes sad and happy monsters that can be hugged or kicked to
change their state. Please note that I do not endorse the kicking of monsters,
nor advise hugging them.


Code folder
-----------

In the `code folder <./code/>`_ is a demo app which has full working examples of
everything in the docs.

To install locally, use a virtualenv, and then either use poetry or see the
code/requirements.txt file for pip.

Feedback
--------

Your feedback is very welcome! Star this repo if you like it, and please share
ideas on `discussions
<https://github.com/spookylukey/django-htmx-patterns/discussions>`_.

Links
-----

Some other good htmx resources:

* `How to use htmx in Django <https://www.mattlayman.com/blog/2021/how-to-htmx-django/>`_ - tutorial blog post
* `django-htmx <https://github.com/adamchainz/django-htmx>`_ - utility library with helpful docs
* `django-htmx-fun <https://github.com/guettli/django-htmx-fun>`_ - example application with Django/htmx
* `django-siteajax <https://github.com/idlesign/django-siteajax>`_ - has some similar ideas to this repo

If you liked this repo, you might also be helped by some of my other resources:

* `django-functest <https://github.com/django-functest/django-functest>`_
* `Django Views — The Right Way
  <https://spookylukey.github.io/django-views-the-right-way/>`_
