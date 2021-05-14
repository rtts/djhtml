import re

from .lines import Line
from .tokens import Token


class Mode:
    """
    Base class for modes. Actual modes are implemented by the
    following subclasses:

    - DjHTML
    - DjCSS
    - DjJS
    - Comment

    This class contains their shared attributes and methods.

    """

    TOKEN = re.compile(r"(?s)(\{%.*?%})")

    DJANGO_OPENING_TAGS = [
        "if",
        "ifchanged",
        "for",
        "block",
        "with",
        "filter",
        "verbatim",
        "spaceless",
        "autoescape",
        "blocktrans",
        "blocktranslate",
    ]
    DJANGO_OPENING_AND_CLOSING_TAGS = [
        "elif",
        "else",
        "empty",
    ]
    DJANGO_CLOSING_TAGS = [
        "endif",
        "endifchanged",
        "endfor",
        "endblock",
        "endwith",
        "endfilter",
        "endverbatim",
        "endspaceless",
        "endautoescape",
        "endblocktrans",
        "endblocktranslate",
    ]

    def __init__(self, source):
        self.source = source

    def tokenize(self, line_nr):
        """
        Split the source text into tokens.

        """
        # Remove leading and trailing whitespace
        source = re.sub(r"[ \t]*\n[ \t]*", "\n", self.source.strip())

        tokens = []
        for token in self.TOKEN.split(source):
            if not token:
                continue
            tokens.extend(self.create_tokens(token, line_nr))
            if "\n" in token:
                line_nr += token.count("\n")

        return tokens

    def create_tokens(self, token, line_nr):
        """
        Given the raw token string, create one or more tokens.

        """
        token_type = self.get_token_type(token)
        return [token_type(token, line_nr)]

    def get_token_type(self, token):
        """
        Given the raw token string, determine what type it is.

        """
        if token.startswith("{%"):
            if tag_name := re.search(r"(\w+)", token):
                if tag_name.group(1) in self.DJANGO_OPENING_TAGS:
                    return Token.BlockOpen
                if tag_name.group(1) in self.DJANGO_OPENING_AND_CLOSING_TAGS:
                    return Token.BlockOpenAndClose
                if tag_name.group(1) in self.DJANGO_CLOSING_TAGS:
                    return Token.BlockClose

        return Token.Text

    def indent(self, tabwidth, level=0, line_nr=1):
        """
        Indenting algorithm: loop over tokens and indent or dedent based
        on their type.

        """

        tokens = self.tokenize(line_nr)
        lines = []
        thislevel = nextlevel = level
        line = Line(tabwidth)
        token = tokens.pop(0) if tokens else None

        # The stack plays no role in indenting but is used to detect
        # syntax errors
        stack = []

        while token:
            if token.indent:
                stack.append(token)
                nextlevel += 1
            if token.dedent:
                try:
                    match = stack.pop()
                except IndexError:
                    raise SyntaxError(
                        f"cannot match “{token.text}” on line {token.line_nr}"
                    )
                if match.type != token.type:
                    raise SyntaxError(
                        f"“{match.text}” opened on line {match.line_nr} should be"
                        f" closed before “{token.text}” on line {token.line_nr}"
                    )
                nextlevel -= 1
                if not line.text:
                    thislevel -= 1

            if token.mode:
                line.finish(thislevel)
                lines.append(line)
                line_nr += 1
                lines.append(
                    token.mode(token.text).indent(tabwidth, nextlevel, line_nr)
                )
                line = Line(tabwidth)
                token = tokens.pop(0) if tokens else None
                thislevel = nextlevel
            elif "\n" in token.text:
                if (nextlevel - thislevel) > 1:
                    raise SyntaxError(
                        f"too many opening statements on line {token.line_nr}"
                    )
                if (thislevel - nextlevel) > 1:
                    raise SyntaxError(
                        f"too many closing statements on line {token.line_nr}"
                    )

                # Split token in two, place second half on next line
                trail, remainder = token.text.split("\n", maxsplit=1)
                line.append(trail)
                line.finish(thislevel)
                lines.append(line)
                line_nr += 1
                token = Token.Text(remainder, line_nr)
                line = Line(tabwidth)
                thislevel = nextlevel
            else:
                line.append(token.text)
                token = tokens.pop(0) if tokens else None

        if stack:
            raise SyntaxError("reached EOF while still looking for closing tags")

        # At the end of my money, I always have a little bit of month
        # left over - Loesje
        line.finish(thislevel)
        lines.append(line)

        return "".join([str(line) for line in lines])


class DjHTML(Mode):
    """
    This mode is the official entrypoint of DjHTML. Usage:

    >>> DjHTML(input_string).indent(tabwidth=4)

    """

    TOKEN = re.compile(
        Mode.TOKEN.pattern + r"|(<style.*?</style>)|(<script.*?</script>)|(<.*?>)"
    )

    IGNORE_TAGS = [
        "doctype",
        "area",
        "base",
        "br",
        "col",
        "command",
        "embed",
        "hr",
        "img",
        "input",
        "keygen",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    ]

    def create_tokens(self, token, line_nr):
        """
        Create "special" tokens when a <style> or <script> tag is
        encountered.

        """
        token_type = self.get_token_type(token)
        if token_type is Token.Style and "\n" in token:
            if match := re.match("(?s)(<.*?>)(.*)(</style>)", token):
                token1 = Token.TagOpen(match.group(1), line_nr)
                token2 = Token.Style(match.group(2), line_nr, mode=DjCSS)
                token3 = Token.TagClose(match.group(3), line_nr)
                return [token1, token2, token3]
        if token_type is Token.Script and "\n" in token:
            if match := re.match("(?s)(<.*?>)(.*)(</script>)", token):
                token1 = Token.TagOpen(match.group(1), line_nr)
                token2 = Token.Text(match.group(2), line_nr, mode=DjJS)
                token3 = Token.TagClose(match.group(3), line_nr)
                return [token1, token2, token3]
        return [token_type(token, line_nr)]

    def get_token_type(self, token):
        if token.startswith("<style"):
            return Token.Style
        if token.startswith("<script"):
            return Token.Script

        if token.startswith("<"):
            if tag_name := re.search(r"(\w+)", token):
                if tag_name.group(1).lower() in self.IGNORE_TAGS:
                    return Token.Text
                if token.endswith("/>"):
                    return Token.Text
                if token.startswith("</"):
                    return Token.TagClose
                return Token.TagOpen

        return super().get_token_type(token)


class DjCSS(Mode):
    """
    Mode for indenting CSS.

    """

    TOKEN = re.compile(Mode.TOKEN.pattern + r"|([{}])")

    def get_token_type(self, token):
        if token == "{":
            return Token.BraceOpen
        if token == "}":
            return Token.BraceClose
        return super().get_token_type(token)


class DjJS(DjCSS):
    """
    Mode for indenting Javascript.

    """

    pass


class Comment(Mode):
    """
    Mode for comments. Preserves all whitespace within them.

    """

    pass
