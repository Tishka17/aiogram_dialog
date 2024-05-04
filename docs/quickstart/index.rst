.. _quickstart:

Quickstart
*************

Install library:

.. literalinclude:: ./install.sh

Let's assume that you have created your aiogram bot with dispatcher and states storage as you normally do. When we setup our ``DialogRegistry`` to use that dispatcher.
It is important you have proper storage because **aiogram_dialog** uses ``FSMContext`` internally to store it state:

.. literalinclude:: ./example.py
    :lines: 1, 4, 6, 25-27

Create states group for your dialog:

.. literalinclude:: ./example.py
    :lines: 3, 6, 14-15

Create at least one window with text and add buttons if needed:

.. literalinclude:: ./example.py
    :lines: 3, 6, 41, 10-11, 12-17, 18-22


Create dialog with your windows:

.. literalinclude:: ./example.py
    :lines: 42, 6, 23

Each ``Dialog`` must be attached to some ``Router`` or ``Dispatcher``.

.. literalinclude:: ./example.py
    :lines: 28

At this point we have configured everything. But dialog won't start itself.
We will create simple command handler to deal with it.
To start dialog we need ``DialogManager`` which is automatically injected by library. Also mind the ``reset_stack`` argument. The library can start multiple dialogs stacking one above other. Currently we do not want this feature, so we will reset stack on each start:

.. literalinclude:: ./example.py
    :lines: 2, 5, 6, 43, 30-35

Before starting your bot you need to setup aiogram-dialogs middlewares and core handlers. To do it use ``setup_dialogs`` function passing your ``Router`` or ``Dispatcher`` instance

.. literalinclude:: ./example.py
    :lines: 44, 6, 29

Last step, you need to start your bot as usual:

.. literalinclude:: ./example.py
    :lines: 44, 6, 45-46

Summary:

.. literalinclude:: ./example.py
    :lines: 1-39

The result will look like:

.. image:: /resources/quickstart.png
