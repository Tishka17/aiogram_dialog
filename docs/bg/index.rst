Updating from another chat or background
*********************************************************************

There are several cases when you do not have proper ``dialog_manager`` instance:

* background tasks
* http/broker handlers
* handlers for another user/chat

In all these cases you should use so called "background manager" which can be obtained from ``BgManagerFactory`` or another ``dialog_manager`` instance using ``.bg()`` method.
Note, that you cannot use normal ``dialog_manager`` outside of aiogram dialog handler.

Using BgManager
------------------------------------------------

Background manager can be used to asynchronously update dialog stack. All these actions are handled in background and you have not access to current state or dialog data.

.. code-block:: python

    await bg_manager.start(state)
    await bg_manager.done()
    await bg_manager.switch_to(state)
    await bg_manager.update(data)

Or you can enter a context to use normal dialog manager accessing all necessary data:

.. code-block:: python

    with bg_manager.fg() as dialog_manager:
        dialog_manager.dialog_data["key"] = value
        dialog_manager.update()


Obtaining BgManagerFactory
------------------------------------------------

In aiogram handlers:

.. code-block:: python

    async def handler(update: Any, dialog_bg_factory: BgManagerFactory) -> None: ...


In middleware. Works if the middleware is registered after setup_dialogs. In 99% of cases, you won’t need this.

.. code-block:: python

    async def __call__(self, handler, event, data):
        dialog_bg_factory = data[BG_FACTORY_KEY]

As a result of the setup_dialogs function:

.. code-block:: python

    dialog_bg_factory = setup_dialogs(dispatcher)

In aiogram dialog handlers:

.. code-block:: python

    async def handler(update: Any, widget: Widget, manager: DialogManager) -> None:
        dialog_bg_factory = manager.middleware_data["dialog_bg_factory"]

Getting a BgManager
------------------------------------------------

Using ``DialogManager`` (another background manager will work as well):

.. code-block:: python

    bg_manager = dialog_manager.bg(
        user_id=other_user_id,
        chat_id=other_chat_id,
    )

Using ``BgManagerFactory``

.. code-block:: python

    bg_manager = dialog_manager.bg(
        bot,
        user_id=other_user_id,
        chat_id=other_chat_id,
    )


Dealing with middlewares
------------------------------------------------

Background manager sends custom events using aiogram dispatcher, so you have to your middlewares won't be triggered by default. To fix it register you middleware for dialog events:

.. code-block:: python

    from aiogram_dialog import DIALOG_EVENT_NAME

    dispatcher.observers[DIALOG_EVENT_NAME].middleware(...)


Classes and signatures
------------------------------------------------

.. autoclass:: aiogram_dialog.api.protocols.BaseDialogManager
   :members: done, start, switch_to, update, bg, fg

.. autoclass:: aiogram_dialog.api.protocols.BgManagerFactory
   :members: bg
