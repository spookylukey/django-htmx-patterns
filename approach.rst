Approach
========

The approach I recommend is:

1. Read the `htmx docs <https://htmx.org/docs/>`_
2. Work out the simplest way of applying the flow control and changes necessary in a Django view.
3. After you have done step 2 **at least 3 or 4 times**, look for nicer patterns
   or abstractions.

In particular, abstracting too early will cause you pain. Just stick to ``if``
statements etc until you know you have something better.

I also strongly recommend starting from **function based views**, and not class
based views. There are `many excellent reasons to always use function based
views <https://spookylukey.github.io/django-views-the-right-way/>`_, especially
when we are talking about views that are generating HTML, but if you are doing htmx
there are even more. To see and extract good htmx patterns, you need:

1. To be able see the complete control flow
2. To be able to re-arrange the control flow

Using CBVs will seriously hinder you in both these.

In my experience so far, the best patterns for using htmx are likely to be
project specific. In addition, while both Django and htmx are mature, the best
patterns to use for the combination of these two is still an area for growth and
needs refining. So for now I’m suggesting that if you like anything you see in
this repo, you should:

* copy-paste it freely into your project (the code is in public domain)
* improve on it (and discard it if it gets in your way)
* if you want, share your improvements or alternatives back here.

But don’t ask me to release this code as a library, and I suggest you shouldn’t
either (at least not yet).
