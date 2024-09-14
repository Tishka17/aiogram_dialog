.. _quickstart:

Quickstart
*************

Install library:

.. literalinclude:: ./install.sh

Let's assume that you have created your aiogram bot with dispatcher and states storage as you normally do. When we setup our ``DialogRegistry`` to use that dispatcher.
It is important you have proper storage because **aiogram_dialog** uses ``FSMContext`` internally to store its state:

.. literalinclude:: ./bot.py

Create states group for your dialog:

.. literalinclude:: ./sg.py

Create at least one window with text and add buttons if needed:

.. literalinclude:: ./window.py

Create dialog with your windows:

.. literalinclude:: ./dialog.py

Each ``Dialog`` must be attached to some ``Router`` or ``Dispatcher``.

.. literalinclude:: ./register.py

At this point we have configured everything. But dialog won't start itself.
We will create simple command handler to deal with it.
To start dialog we need ``DialogManager`` which is automatically injected by library. Also mind the ``reset_stack`` argument. The library can start multiple dialogs stacking one above other. Currently we do not want this feature, so we will reset stack on each start:

.. literalinclude:: ./start.py

Before starting your bot you need to setup aiogram-dialogs middlewares and core handlers. To do it use ``setup_dialogs`` function passing your ``Router`` or ``Dispatcher`` instance

.. literalinclude:: ./setup_dialogs.py

Last step, you need to start your bot as usual:

.. literalinclude:: ./start_bot.py

Summary:

.. literalinclude:: ./summary.py

The result will look like:

.. image:: /resources/quickstart.png
