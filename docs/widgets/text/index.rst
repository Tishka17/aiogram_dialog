Text widget types
*****************************

Every time you need to render text use any of text widgets:

* :ref:`Const<const_text>` - returns text with no modifications
* :ref:`Format<format_text>` - formats text using ``format`` function. If used in window the data is retrived via ``getter`` function.
* :ref:`Multi<multi_text>` - multiple texts, joined with a separator
* :ref:`Case<case_text>` - shows one of texts based on condition
* :ref:`Progress<progress_bar>` - shows a progress bar
* :ref:`List<list_text>` - shows a dynamic group of texts (similar to :ref:`Select<select>` keyboard widget)
* :ref:`Jinja<jinja>` - represents a HTML rendered using jinja2 template


.. toctree::
    :hidden:

    passing_data/index
    const/index
    format/index
    multi/index
    case/index
    progress/index
    list/index
    jinja/index
