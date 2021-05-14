DjHTML
======

**A pure-Python Django template indenter without any dependencies.**


Installation
------------

Install DjHTML with the following command:

    $ pip install djhtml


Usage
-----

After installation you can indent Django templates using the `djhtml`
command. It has the following options:

    $ djhtml --help
    usage: djhtml [-h] [-i] [-q] [-t N] [-o filename] [filenames ...]

    DjHTML is a Django template indenter that works with mixed
    HTML/CSS/Javascript templates. It works similar to other code-
    formatting tools such as Black. The goal is to correctly indent
    already well-structured templates but not to fix broken ones. A
    non-zero exit status indicates that a template could not be
    indented.

    positional arguments:
      filenames             input filenames

    optional arguments:
      -h, --help            show this help message and exit
      -i, --in-place        modify files in-place
      -q, --quiet           be quiet
      -t N, --tabwidth N    tab width
      -o filename, --output-file filename
                            output filename


Pre-commit configuration
------------------------

Even better, you can use DjHTML as a
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
