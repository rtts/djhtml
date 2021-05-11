DJHTML
======

**A pure-Python Django template indenter without any dependencies.**


Installation
------------

You can install DJHTML with the following command:

    $ pip install djhtml


Usage
-----

Next, you can use it like so:

    $ djhtml my-django-template.html


Pre-commit configuration
------------------------

Even better, you can use DJHTML as a
[pre-commit](https://pre-commit.com/) hook to automatically indent
your Django templates upon each commit.

First, add the following to your `.pre-commit-config.yaml`:

    repos:
    - repo: https://github.com/rtts/djhtml
      rev: main
      hooks:
      - id: djhtml

Then, run the following command:

    $ pre-commit autoupdate


Results
-------

Before:

    {% block extrahead %}
    <script>
    function f() {
    return 42;
    }
    </script>
    {% endblock %}

After:

    {% block extrahead %}
        <script>
            function f() {
                return 42;
            }
        </script>
    {% endblock %}
