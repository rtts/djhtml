DJHTML
======

**Finally! An elegant Django template indenter without any dependencies!**


Installation
------------

First, add the following to your `.pre-commit-config.yaml`:

    repos:
    - repo: https://github.com/rtts/djhtml
      rev: main
      hooks:
      - id: djhtml

Then run the following command:

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
