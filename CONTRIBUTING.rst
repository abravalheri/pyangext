How to contribute
=================

Pull-requests and discussions are essential for any open-source project.
Any contribution to this project will be considered lovely. Here's just
a quick guide to help you in this journey.

Please have in mind that nothing can be considered 100% truth and
immutable (including this statement). This project will not adhere to
any ``strict`` way of development.

Pull-Requests
-------------

Github has two great GREAT articles about contributing:
`Contributing to Open Source on GitHub <https://guides.github.com/activities/contributing-to-open-source/>`_
and `Using pull requests <https://help.github.com/articles/using-pull-requests/>`_.
Please make sure to read it in your lifetime (everyone that reads became
a better person).

.. note::
    Oh man, `guides.github.com <https://guides.github.com/>`_ and
    `help.github.com <https://help.github.com>`_ are astonishing!

Please, try to keep your commit messages as communicative as possible.
There is a good
`reference <https://github.com/erlang/otp/wiki/Writing-good-commit-messages>`_
for it as well.

.. note::
    I usually think in the commit itself as an implicit subject of
    commit message. For example: ``[This commit] Add .gitignore``
    Also take a look at `this commit message format proposal <https://gist.github.com/abravalheri/34aeb7b18d61392251a2>`_, that borrows some convention
    from `AngularJS <https://github.com/angular/angular.js/blob/master/CONTRIBUTING.md>`_.

Communication is *always* handy! If you have any doubt or would like to
discuss your thoughts, you are more than welcome to send me a message!
Please comment directly on the code, open an issue, submit a pull
request, mention me anywhere... I think GitHub has good tools to help
developers communicate and share experiences.

Code Guidelines
~~~~~~~~~~~~~~~

This repository try to adhere to
`PEP8 <https://www.python.org/dev/peps/pep-0008/>`_
as much as possible.

Please make use of tools like
`flake8 <https://flake8.readthedocs.io>`_,
`pylint <https://www.pylint.org>`_,
`isort <https://github.com/timothycrosley/isort>`_, and
`pre-commit <http://pre-commit.com>`_ before submitting
your code. There are configuration files for all these tools in the
root of the repository and the easiest way of starting is by doing:

.. code-block:: bash

   sudo pip install pre-commit
   # drop sudo if you are using a virtualenv or pyenv
   # inside project directory:
   pre-commit install
   pre-commit run --all-files

Please also consider running the test suite before submitting a pull request:

.. code-block:: bash

   python setup.py test

Reporting a Bug
---------------

-  Update to the most recent master release if possible. Someone may
   have already fixed your bug (such a wonderful scenario!)
-  Search for similar issues. It's possible somebody has encountered
   this bug already. In this case comment your experience too!
-  Clearly describe the issue including steps to reproduce when it is a
   bug and preferably send a script that does so. Try to keep all the
   things fully operational with the exception of the bug you want to
   demonstrate. (Ok, I admit this is boring, but is probably the fastest
   way to get thing working).
-  Keep up to date with feedback from the project team, maybe you can
   help us to test ;)
-  If possible, submit a Pull Request with a failing test. It would be
   wonderful to increase the test coverage!
-  Consider the challenge of fixing the bug, I'm sure it can be funny or
   at least very aggrandizing.

Requesting a Feature
--------------------

-  Search Issues for similar feature requests. It's possible somebody
   has already asked for this feature or provided a pull request that
   we're still discussing.
-  Provide a clear and detailed explanation of the feature you want and
   why it's important to add. Keep in mind that features should be
   useful to the majority of users and not just a small subset. If
   you're just targeting a minority of users, consider writing an add-on
   library.
-  If the feature is complex, consider writing some initial
   documentation for it. If we do end up accepting the feature it will
   need to be documented and this will also help us to understand it
   better ourselves.
-  Attempt a Pull Request. If you're at all able, start writing some
   code. We always have more work to do than time to do it. If you can
   write some code then that will speed the process along.

.. note::
    This guide was partially copied from

    - `ember.js <https://raw.githubusercontent.com/emberjs/ember.js/master/CONTRIBUTING.md>`_
    - `factory_girl <https://raw.github.com/thoughtbot/factory_girl_rails/master/CONTRIBUTING.md>`_
    - `puppet <https://raw.githubusercontent.com/puppetlabs/puppet/master/CONTRIBUTING.md>`_
    - `rails <http://edgeguides.rubyonrails.org/contributing_to_ruby_on_rails.html#contributing-to-the-rails-documentation>`_

    Please consider reading them. They are just great!
