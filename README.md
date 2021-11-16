# DjHTML

***A pure-Python Django/Jinja template indenter without dependencies.***

DjHTML is a fully automatic template indenter that works with mixed
HTML/CSS/Javascript templates that contain
[Django](https://docs.djangoproject.com/en/stable/ref/templates/language/)
or [Jinja](https://jinja.palletsprojects.com/templates/) template
tags. It works similar to other code-formatting tools such as
[Black](https://github.com/psf/black) and interoperates nicely with
[pre-commit](https://pre-commit.com/).

DjHTML is an _indenter_ and not a _formatter_: it will only add/remove
whitespace at the beginning of lines. It will not insert newlines or
other characters. The goal is to correctly indent already
well-structured templates, not to fix broken ones.

For example, consider the following incorrectly indented template:

```jinja
<!doctype html>
<html>
    <body>
        {% block content %}
        Hello, world!
        {% endblock %}
        <script>
            $(function() {
            console.log('Hi mom!');
            });
        </script>
    </body>
</html>
```

This is what it will look like after processing by DjHTML:

```jinja
<!doctype html>
<html>
    <body>
        {% block content %}
            Hello, world!
        {% endblock %}
        <script>
            $(function() {
                console.log('Hi mom!');
            });
        </script>
    </body>
</html>
```


## Installation

Install DjHTML with the following command:

    $ pip install djhtml


## Usage

After installation you can indent templates using the `djhtml`
command. The default is to read from standard in and to write the
indented output to standard out.To modify the source file in-place,
use the `-i` / `--in-place` option and specify a filename:

    $ djhtml -i template.html
    reindented template.html
    1 template has been reindented.

Normally, the exit status of 0 means everything went well, regardless
of whether any files were changed. If any errors were encountered, the
exit status indicated the number of problematic files. However, when
the option `-c` / `--check` is used, the exit status is the number of
files that would have changed, but no changes are actually made.

All available options are:

- `-h` / `--help`: show overview of available options
- `-i` / `--in-place`: modify files in-place
- `-c` / `--check`: don't modify files; the exit status is the number
    of files that would have changed
- `-q` / `--quiet`: don't print any output
- `-t` / `--tabwidth`: set tabwidth (default is 4)
- `-o` / `--output-file`: write output to specified file


## `fmt:off` and `fmt:on`

You can exclude specific lines from being processed with the
`{# fmt:off #}` and `{# fmt:on #}` operators:

```jinja
<div class="
    {# fmt:off #}
      ,-._|\
     /     .\
     \_,--._/
    {# fmt:on #}
"/>
```

Contents inside `<pre> ... </pre>`, `<!-- ... --->`, `/* ... */`, and
`{% comment %} ... {% endcomment %}` tags are also ignored (depending
on the current mode).


## Modes

The indenter operates in one of three different modes:

- DjHTML mode: the default mode. Invoked by using the `djhtml` command
  or the pre-commit hook.

- DjCSS mode. Will be entered when a `<style>` tag is encountered in
  DjHTML mode. It can also be invoked directly with the command
  `djcss`.

- DjJS mode. Will be entered when a `<script>` tag is encountered in
  DjHTML mode. It can also be invoked directly with the command
  `djjs`.


## pre-commit configuration

You can use DjHTML as a [pre-commit](https://pre-commit.com/) hook to
automatically indent your templates upon each commit.

First, install pre-commit:

    $ pip install pre-commit
    $ pre-commit install

Then, add the following to your `.pre-commit-config.yaml`:

```yml
repos:
- repo: https://github.com/rtts/djhtml
  rev: 'main'  # replace with the latest tag on GitHub
  hooks:
    - id: djhtml
```

Finally, run the following command:

    $ pre-commit autoupdate

This will automatically replace `main` with the latest tag on GitHub,
[as recommended by pre-commit](https://pre-commit.com/#using-the-latest-version-for-a-repository).

Now when you run `git commit` you will see something like the
following output:

    $ git commit

    djhtml...................................................................Failed
    - hook id: djhtml
    - files were modified by this hook

    reindented template.html
    1 template has been reindented.

To inspect the changes that were made, use `git diff`. If you are
happy with the changes, you can commit them normally. If you are not
happy, please do the following:

1. Run `SKIP=djhtml git commit` to commit anyway, skipping the
   `djhtml` hook.

2. Consider [opening an issue](https://github.com/rtts/djhtml/issues)
   with the relevant part of the input file that was incorrectly
   formatted, and an example of how it should have been formatted.

Your feedback for improving DjHTML is very welcome!

## Development

Use your preferred system for setting up a virtualenv, docker environment,
or whatever else, then run the following:

```sh
python -m pip install -e .[dev]
pre-commit install --install-hooks
```

Tests can then be run quickly in that environment:

```sh
python -m unittest discover -v
```

Or testing in all available supported environments and linting can be run
with [`nox`](https://nox.thea.codes):

```sh
nox
```
