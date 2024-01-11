Modal dialogs
=============

Modal dialogs are a common UI element that you may need to create using htmx.
The `htmx modal dialog docs <https://htmx.org/examples/modal-custom/>`_ provide
a great starting point, but below I will show a complete example in Django, with
a small amount of vanilla JS that you have to write once and can re-use for
every modal interaction, and a few enhancements.

This example will be more full-featured than the one in the htmx docs, and
considers the case where the modal includes a form that may itself need server
round-trips before it closes.

Our example will be a page that lists monsters. We then want a button that will
load a dialog for adding a new monster. This dialog will post back to and endpoint
that will do validation. On success we will close the dialog and also refresh part
of the parent page so it shows the new item. The interaction looks like this:

.. raw:: html

   <video src="https://github.com/spookylukey/django-htmx-patterns/assets/62745/4030d635-dad8-48cf-965e-f9a1f6c8dbbf" width=180 ></video>

The HTML for the “Add a monster” button looks like this:

.. code-block:: html

   <button
     hx-trigger="click"
     hx-get="{% url 'modals_create_monster' %}"
     hx-target="body"
     hx-swap="beforeend"
     >
     Add a monster
   </button>


It loads the new HTML (for the dialog) at the end of the body. We need to ensure
that this content gets displayed at the right point, but in this example we are
going to lean heavily on ``<dialog>`` (see `MDN docs for dialog
<https://developer.mozilla.org/en-US/docs/Web/HTML/Element/dialog>`_), which
thankfully has the desired behaviour of being invisible by default, and also
`has reached the level of support where it is probably your best option
<https://www.scottohara.me/blog/2023/01/26/use-the-dialog-element.html>`_.

Our view code for returning the dialog is going to be based on the
standard “create form” flow you’ll recognise, with a few changes, which I’ll
show a bit later.

The template needs a ``<dialog>``, and also a ``<form>`` that will post back to
the same view via htmx, replacing the whole contents, using our normal `inline
partials <./inline_partials.rst>`_ approach:

.. code-block:: html

   <dialog id="dialog-main" data-onload-showmodal>
     {% block dialog-contents %}
       <form
           hx-post="{{ request.get_full_path }}"
           hx-target="#dialog-main"
           hx-vals='{"use_block": "dialog-contents"}'
           hx-swap="innerHTML"
       >
         {{ form.as_p }}

         <button type="submit">Add</button>
       </form>
     {% endblock %}
   </dialog>


This will enable our view to do validation as normal, showing the results in the
same dialog.

Notice we’ve used ``hx-post="{{ request.get_full_path }}"`` rather than the
shortcut ``hx-post="."``, because ``.`` would refer to the current browser URL,
which is the parent page since we didn’t change the URL when we popped up the
dialog.

This approach means we need to add the ``@for_htmx(use_block_from_params=True)``
decorator to our view.



I’ve added an attribute ``data-onload-showmodal`` which is going to trigger the
showing of our own modal. We need to call the ``.showModal()`` method on the
``<dialog>`` element after it loads, which we can do using a very few lines of
vanilla JS:

.. code-block:: javascript

    document.body.addEventListener("htmx:afterSettle", function(detail) {
        const dialog = detail.target.querySelector('dialog[data-onload-showmodal]');
        if (dialog) {
            dialog.showModal();
        };
    });

Wherever I have action-at-a-distance like this (i.e. the Javascript
implementation is not close to the HTML which uses it), I like to use explicit
attributes like ``data-onload-showmodal``, even if I always want this behaviour
for ``<dialog>`` elements, because it makes it much easier to see that something
magic is going on, and grep for the code that is causing the behaviour.

It’s also a good idea to ensure clean up happens, by first adding an event
handler that will completely remove the dialog HTML from the DOM when the dialog
closes:

.. code-block:: javascript

   dialog.addEventListener("close", () => {
     dialog.remove();
   });


Finally, we want the dialog to close when the save button is pressed and the
object successfully created. We achieve this most easily by having the server
return an `Hx-Trigger response header <https://htmx.org/headers/hx-trigger/>`_
and respond to that via Javascript. In addition, since we added an item, the
parent page is now out of date, and we also want to trigger the parent page to
update somehow. We’ll use another event for that which the parent can subscribe
to using an `hx-trigger attribute <https://htmx.org/attributes/hx-trigger/>`_.

So our final view code for the modal looks like this:

.. code-block:: python

   @for_htmx(use_block_from_params=True)
   def create_monster(request: HttpRequest):
       if request.method == "POST":
           form = CreateMonsterForm(request.POST)
           if form.is_valid():
               monster = form.save()
               return HttpResponse(
                   headers={
                       "Hx-Trigger": json.dumps(
                           {
                               "closeModal": True,
                               "monsterCreated": monster.id,
                           }
                       )
                   }
               )
       else:
           form = CreateMonsterForm()
       return TemplateResponse(request, "modals_create_monster.html", {"form": form})


To respond to the ``closeModal`` trigger, we need this Javascript:

.. code-block:: javascript

    document.body.addEventListener('closeModal', function() {
        document.querySelector('dialog[open]').close();
    });

To respond to the ``monsterCreated`` event, we need the relevant part of the
main page to look something like this, using our normal inline partials pattern:

.. code-block:: html

   {% block monster-list %}
     <div
         id="monster-list"
         hx-trigger="monsterCreated from:body"
         hx-get="."
         hx-vals='{"use_block": "monster-list"}'
         hx-target="#monster-list"
         hx-swap="outerHTML"
     >
       {% for monster in monsters %}
          …
       {% endfor %}

     </div>
   {% endblock %}

In English: “when the ``monsterCreated`` event is triggered on the document
body, then do a GET request to the current URL, with additional query parameter
``use_block=monster-list``, which asks the server to render only the
``monster-list`` block; the result should be use to replace the outerHTML of the
``#monster-list`` DOM element”.

This again requires ``@for_htmx(use_block_from_params=True)`` on the list view.


Tips
----

Dialog elements are now very well supported, and do a lot of things for us, like
focus and accessibility. I’ve collected a few more tips if you want to improve
the look, and add support for transitions.

Closing
~~~~~~~

In addition to using ``Esc`` button for closing a dialog (which is automatically
supported by ``<dialog>``), you can add a no-Javascript close button like this::

  <form method="dialog"><button>Close</button></form>


Transitions and styling
~~~~~~~~~~~~~~~~~~~~~~~

You can add a transition for loading and style the dialog with this CSS:

.. code-block:: CSS

   dialog {
       /* Override some builtins that limit us: */
       max-height: 100vh;
       max-width: 100vw;

       /* Positioning */
       box-sizing: border-box;
       width: calc(100vw - 40px);
       height: calc(100vh - 40px);
       top: 20px;
       left: 20px;
       position: fixed;
       margin: 0;

       /* Styling */
       border: 0;
       border-top: 2px solid #888;
       padding: 20px;

       /* Fade in: */
       display: flex;  /* for some reason, display: block disables the transition. */
       flex-direction: column;
       opacity: 0;
       transition: opacity 0.15s;
       pointer-events: none; /* necessary or the main page becomes inaccessible after closing dialog */
   }

   dialog[open] {
       opacity: 1;
       pointer-events: inherit;
   }

   dialog::backdrop {
       background-color: #0008;
   }


(Thanks to `this Stackoverflow answer
<https://stackoverflow.com/questions/24991072/how-to-fade-in-a-html5-dialog/64708195#64708195>`_)

Reusing
~~~~~~~

If you have a standard dialog format you want to use, you can use normal Django
template inheritance to define your modal templates, with the ``<dialog>`` in
the parent and blocks to override for the content.

Related patterns
----------------

If your modal is simply a confirmation prompt, I would instead use the
`hx-confirm <https://htmx.org/attributes/hx-confirm/>`_, or build something using
the `hx:confirm event <https://htmx.org/events/#htmx:confirm>`_.

Full code
---------

- `view <./code/htmx_patterns/views/modals.py>`__
- `main template <./code/htmx_patterns/templates/modals_main.html>`__
- `modal template <./code/htmx_patterns/templates/modals_create_monster.html>`__
- `Javsacript <./code/htmx_patterns/static/js/modals.js>`__
- `CSS <./code/htmx_patterns/static/css/modals.css>`__
- `decorator <./code/htmx_patterns/utils.py>`__
