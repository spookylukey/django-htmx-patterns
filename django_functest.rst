django-functest patterns
========================

I like to use `django-functest
<https://github.com/django-functest/django-functest/>`_ to write my tests. One
the big advantages of django-functest is that it allows writing a single test
that works both with a full browser (via Selenium), and with a method based on
`WebTest
<https://docs.pylonsproject.org/projects/webtest/en/latest/index.html>`_. If
possible, I like my tests to run with both methods. This has a number of big
advantages:

1. Speed: I can run the test suite (or part of it) with the slow Selenium tests
   disabled (just by doing ``pytest -m 'not selenium'``) and get a much faster
   iteration loop.

2. Robustness: I can avoid potentially flaky Selenium tests.

3. Clear failures and debugging: when a WebTest-based test fails, since it is a
   single-threaded, single Python process I get a useful stacktrace and I can
   use a debugger or `jump in with a REPL
   <https://lukeplant.me.uk/blog/posts/repl-python-programming-and-debugging-with-ipython/>`_.
   When you have a browser and multiple threads involved (one for the tests, one for the server in the
   background), things get much more complicated.


As soon as you add Javascript to a site, you potentially loses these advantages.
Thankfully, with htmx’s model, you can very often produce pages that continue to
work even if Javascript is disabled or ignored. This is not always possible, and
requires a little care, but can be worth doing. The main benefit I’m talking
about here is not to actually keep the site working for situations where
Javascript doesn’t load etc. (although that can be the case more than you
think), but to enable our testing strategies to get decent coverage of
server-side functionality without needing full browser automation.


Most of the example code in this repo is already written in a style that enables
this pattern. The main process:

- write views without any htmx and add tests for them. These pages will not benefit from partial page loads etc. but the basic functionality will be there.

- then add the ``hx-`` attributes and template/view modifications

- when needed, add some branches for htmx requests e.g. in the `“view restart”
  view code
  <https://github.com/spookylukey/django-htmx-patterns/blob/c96f6d595f88cbcb83b38463933e9661fd9b6174/code/htmx_patterns/views/restarts.py#L36>`_,
  I branch on ``is_htmx(request)`` and do a different kind of redirect for non-htmx requests.


For some other things, like modals where the partial page doesn’t even load until you’ve
clicked some buttons that require Javascript, this approach won’t work
perfectly. For these, you can try this instead:

- make the modal functional as a standalone page/view
- make the start of the test conditional on `is_full_browser_test <https://django-functest.readthedocs.io/en/latest/common.html?highlight=is_full_browser#django_functest.FuncCommonApi.is_full_browser_test>`_, so that where you have a full browser, you test the full flow, but for WebTest you jump straight to the modal view.

For more complex cases, where Javascript really is essential, this approach can
complicate things, so you have to use your head and just abandon the WebTest
version of the tests!
