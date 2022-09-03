Django + HTMX patterns
======================

This repo is a rough-and-ready compilation of the patterns I’m using and
developing when writing `Django <https://www.djangoproject.com/>`_ projects that
use `HTMX <https://htmx.org/>`_.

My aims are to document and share:

1. The basic patterns and control flow needed
2. Some enhancements we can make with a few utilities

The code presented depends only on Django and HTMX, unless otherwise noted. I
wont be packaging it up as a library. It is instead being released into the
public domain, and you are encouraged to copy-paste it for your own needs. (See
the “Approach” docs for why).

There are some Django packages that provide shortcuts for some of the things
mentioned here, such as `django-htmx
<https://github.com/adamchainz/django-htmx>`_, but I won’t be using any of them
for the sake of clarity.

* `Approach </approach.rst>`_
* `Base template </base_template.rst>`_
* `Headers </headers.rst>`_
* `Post requests </posts.rst>`_
* `Partials using separate templates </separate_partials.rst>`_
* `Separate partials with a single view </separate_partials_single_view.rst>`_
* `Partials using inline template </inline_partials.rst>`_  TODO

This is a work in progress, I’ll try to keep it up to date. PRs welcome.

Full Django project demoing code examples is in the `code folder <./code/>`_.
