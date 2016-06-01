========
pyangext
========

Sensible extensions for |pyang|_

.. image:: https://travis-ci.org/abravalheri/pyangext.svg?branch=master
    :target: https://travis-ci.org/abravalheri/pyangext
.. image:: https://coveralls.io/repos/github/abravalheri/pyangext/badge.svg?branch=master
    :target: https://coveralls.io/github/abravalheri/pyangext?branch=master

What's this all about?
======================

`YANG <http://tools.ietf.org/html/rfc6020>`_ is a data modeling language
born in the context of configuration and management of network devices
(like routers and other internet-related stuff). It is envisioned to work
with XML data encoding and remote procedure calls (so 2000s ...), but it is
extremelly flexible and can be used for a multitude of purposes.
In turn, |pyang|_ is a ``python`` project
that provides parsing, validation, transformation and code generation
functionalities.
Despite of being extensible, the |pyang|_ code is a little bit complex,
and the documentation scarce. This makes the task of building plugins
difficult.

``pyangext`` aims to provide a common foundation for plugins,
wrapping |pyang|_ features, and making easier to use it programatically
outside |pyang|_ own code-base.

.. topic:: If you are one of the |pyang|_ authors...

  You guys have done an amazing job, please don't feel upset about this
  documentation. I'm trying to make it interesting and a little bit funny.
  The ultimate goal is to have an amazing |pyang|_ environment,
  and if you would like to merge ``pyangext`` inside |pyang|_,
  please let me know.

Getting Started
===============

If you are not a plugin writer
------------------------------

Well, ``pyangext`` will not exactly change your life... but you can
have a little benefit from it, so let's **install all the things!**

.. code-block:: bash

   sudo pip install pyangext
   # drop sudo if you are using a virtualenv or pyenv

There are some python packages that register themselves as |pyang|_ plugins
using |setuptools|_ entry-points. While |pyang|_ does not nativelly support
it, ``pyangext`` will consider it and generate a complete plugin path.
You can activate it by doing:

.. code-block:: bash

   eval $(pyangext --export-path)

If you like it, you can also include it in your ``.(ba|z)shrc`` file.

**DONE**

If you **ARE** a plugin writer
------------------------------

You have probably noticed that |pyang|_ does not support the standard
|setuptools|_ entry-points way of writing plugins. Instead it requires
that the user either copies the plugin to the |pyang|_ plugins directory,
or changes manually the ``PYANG_PLUGINPATH`` env var.
Sometimes this makes difficult to describe how to use your plugin,
e.g. `pyangbind <https://github.com/robshakir/pyangbind>`_.

Using, ``pyangext`` you can:

#. Create an empty plugin package inside your project
   (folder with just and empty ``__init__.py`` file inside).
#. Put just your plugin modules inside it
   (``.py`` files containing ``pyang_plugin_init`` function).
#. Register a |setuptools|_ entry-point under the ``yang.plugins``
   section, with the name of your plugin, pointint to that function.
#. Ask your users in the documentation to use
   ``eval $(pyangext --export-path)`` before runing |pyang|_,
   **or** exchange the |pyang|_ shell commad by ``pyangext run``
   with the same arguments.
#. Distribute your package using PyPI/pip tools.

Additionally ``pyangext`` provides two other submodules with functions
that can be used in your code.
The :mod:`pyangext.utils` module provides functions like ``create_context``,
``parse``, ``dump``, ``walk``. This functions are very useful, and a little
example is provided bellow:

.. code-block:: python

  from pyangext.utils import create_context, dump, find, parse, walk
  ctx = create_context(keep_comments=True, features=['if:if-mib'])
  ast = parse('leaf id { type int32; }', ctx)  # tree-ish structure
  print(dump(ast, ctx))  # produce YANG code
  used_types = walk(ast,
                    select=lambda node: node.keyword == 'type',
                    apply=lambda node: node.arg)
  # => ['int32']
  int32_nodes = find(ast, 'type', 'int32')  # list with 1 object

``pyang.Context`` object plays a central role in the |pyang|_
architecture. The ``create_context`` can be used to create this object in a
similar way it is created by the |pyang|_ CLI.

The :mod:`pyangext.definitions` on the other hand provides some constants like
the ``BUILT_IN_TYPES`` list.

.. note::
  There are few well known issues with ``create_context`` and
  ``parse`` functions preventing them to be used by standalone python scripts,
  like the lack of YANG ``deviation`` support. Despite they can be used
  in most situations, the prefered way of manipulating the YANG
  Abstract Syntax Tree (AST) is yet writing a plugin.

.. seealso::
  :mod:`pyangext.cli`
  :mod:`pyangext.utils`


Stuff Doesn't Work
==================

This work was tested and I think it's stable, but any feedback you can
give me on this would be gratefully received (see section **Reporting a Bug**
at |guidelines|_.).

Can I help?
===========

Yes, please! Contributions of any kind are welcome, and also feel free
to ask your questions!

Please take a look at the |guidelines|_.

Well-known list of TODOs
------------------------

- Make sure ``augment``, ``deviation`` and ``include`` work with both
  ``ctx.add_module`` and ``parse``. (by writing tests and making it pass).
- Use ``ctx.add_module`` under the hood when a file name is passed to
  ``parse``. If it is a module, why not add it to context as well?
- Make ``parse`` and ``dump`` work with ``yin`` format.

Doubts
------

- Perform ``ctx.validate`` and ``validate_module`` under the hood?
- Abstract Context and ``i_`` magic method?

Ultimate Goals
--------------

- Allow |pyang|_ plugins to be written as standalone python scripts.
  (I think it is better to have small focused scripts, instead of
  a huge amount of options in the |pyang|_ CLI)
- Merged into |pyang|_ own code base.


.. |pyang| replace:: ``pyang``
.. _pyang: https://github.com/mbj4668/pyang
.. |setuptools| replace:: ``setuptools``
.. _setuptools: https://pythonhosted.org/setuptools/setuptools.html#dynamic-discovery-of-services-and-plugins
.. |guidelines| replace:: Contribution Guidelines
.. _guidelines: https://github.com/abravalheri/pyangext/blob/master/CONTRIBUTING.rst