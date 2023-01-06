View restart
============

This builds on the `Single view with actions combined <./actions.rst>`_ pattern.

In normal Django code, after processing a POST request, it is common to do an
HTTP redirect to another or the same page. This serves two purposes:

1. By doing a redirect, if the user presses the back button and then forward, or
   presses refresh, the browser won’t attempt to re-submit the POST request (or
   prompt the user about doing this) — it will just load the page, which is
   usually what we want.

2. By starting a new request, any data that the view function has loaded from
   the database will be discarded and the new request will trigger a fresh run
   of the view function. This is important as the handling of the POST request
   may have changed data such that already loaded data is invalid or partially
   inconsistent.


When using htmx, the first of these is not important, as a browser will never be
triggered to do a partial page update by things like pressing the refresh
button. The second concern can still be relevant, however.

Consider the following page where we have two lists of items, each item with a
checkbox, and with buttons for moving items between them. The view code looks
as follow without htmx. (For clarity, we have happy monsters that we can
select and “kick” to make them sad, and sad monsters we can “hug” to make them
happy)


.. code-block:: python

   def monster_list(request: HttpRequest):
       monsters = Monster.objects.all()
       sad_monsters, happy_monsters = partition(lambda m: m.is_happy, monsters)

       if request.method == "POST":
           if "kick" in request.POST:
               for monster in happy_monsters:
                   if f"happy_monster_{monster.id}" in request.POST:
                       monster.kick()
           if "hug" in request.POST:
               for monster in sad_monsters:
                   if f"sad_monster_{monster.id}" in request.POST:
                       monster.hug()
           return HttpResponseRedirect("")

       return TemplateResponse(
           request,
           "monster_list.html",
           {
               "happy_monsters": happy_monsters,
               "sad_monsters": sad_monsters,
           },
       )


The UI is best illustrated with a screenshot:

.. image:: images/view_restart_screenshot.png


This relies on some HTML that looks like this:


.. code-block:: html

   {% for monster in happy_monsters %}
     <label><input name="happy_monster_{{ monster.id }}" type="checkbox"> {{ monster.name }}</label><br>
   {% endfor %}

   ...

   <button name="kick" type="submit">Kick them!</button>


…and similarly for the other list and button.


When we come to htmx-ify this, we want the elements containing lists to get
refreshed, but everything else to stay the same. We can achieve this most easily
by adding blocks and IDs (using the `inline partials <./inline_partials.rst>`_ approach)
and using two `Out Of Band <https://htmx.org/docs/#oob_swaps>`_ swaps. Our
previous ``for_htmx`` decorator will work well for this.

However, what should we do instead of the redirect?

- If we leave the redirect as it is, we’ll get a GET request that loses the
  important htmx parameters in the POST data. Also, the latency of an extra
  browser round-trip for the extra HTTP request is completely unnecessary, and we
  want to avoid that to keep our page snappy.

- But, if we just allow flow control to continue through the view function, the
  ``sad_monsters`` and ``happy_monsters`` lists will be wrong — they reflect the
  data as it was at the beginning, not after we changed a bunch of their states.

  We could fix it up by modifying those lists, but this is easy to get wrong,
  especially with more complex cases.

Instead, what we want to do is “restart” the view from the top. This is a bit
like an “internal redirect”, in which we basically get the advantage of starting
from scratch, but without an extra HTTP request. We do want the original request
object to still be around and get applied when it comes to the ``for_htmx``
decorator.

We can thankfully do this really easily as follows:

- pull out the the “body” of the view function into a separate function
- instead of a redirect, call that function recursively, but with a modified
  request object (POST method changed to GET) so that we don’t go into an
  infinite loop.


Our code now looks like this:

.. code-block:: python

   @for_htmx(use_block_from_params=True)
   def monster_list(request: HttpRequest):
       return _monster_list(request)


   def _monster_list(request: HttpRequest):
       monsters = Monster.objects.all()
       sad_monsters, happy_monsters = partition(lambda m: m.is_happy, monsters)

       if request.method == "POST":
           if "kick" in request.POST:
               for monster in happy_monsters:
                   if f"happy_monster_{monster.id}" in request.POST:
                       monster.kick()
           if "hug" in request.POST:
               for monster in sad_monsters:
                   if f"sad_monster_{monster.id}" in request.POST:
                       monster.hug()
           ### New code here: ###
           if is_htmx(request):
               return _monster_list(make_get_request(request))
           return HttpResponseRedirect("")

       return TemplateResponse(
           request,
           "monster_list.html",
           {
               "happy_monsters": happy_monsters,
               "sad_monsters": sad_monsters,
           },
       )



The ``make_get_request`` function looks like this:

.. code-block:: python


   import copy
   from django.http.request import HttpRequest, QueryDict


   def make_get_request(request: HttpRequest) -> HttpRequest:
       """
       Returns a new GET request based on passed in request.
       """
       new_request = copy.copy(request)
       new_request.POST = QueryDict()
       new_request.method = "GET"
       return new_request


Another way to look at this pattern is by an analogy with `the Elm Architecture
<https://en.wikipedia.org/wiki/Elm_(programming_language)#The_Elm_Architecture>`_
or “redux” architecture used in client side state handling. The idea is that we
separate out model updates from UI rendering, so that instead of trying to patch
up the UI after we’ve modified the model (i.e. the state), we just update the
model, then re-render the UI from scratch as essentially a pure function based
on the new state. In the same, way, our view function here doesn’t try to patch
up the local variables after modifying DB state, it just starts over from the
top.

An extension to this pattern is sometimes needed if there is extra information
needed from the POST data that needs to be propagated. In the above example, we
have a buglet if the user selects items from both lists, and then presses one
button — the checked items in the other list become unchecked, as their state is
reset to unchecked every time the templates are rendered. If we want to fix
that, we can check which items are selected, and then propagate forward the
selected items as additional data passed into our “internal” view function. See
the full code for an example.

Full code: `view <./code/htmx_patterns/views/restarts.py>`_, `template <./code/htmx_patterns/templates/view_restart.html>`__
