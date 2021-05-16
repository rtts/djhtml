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

    TAG = r"\{%.*?%\}"
    COMMENT = r"{% comment .*? endcomment %}"
    TOKEN = re.compile(f"(?s)({COMMENT})|({TAG})")

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

    def indent(self, tabwidth, level=0):
        """
        Return the indented text as a single string.

        """
        lines = self.tokenize(tabwidth, level)
        return "".join([str(line) for line in lines])

    def tokenize(self, tabwidth, level):
        """
        Split the source text into lines with tokens. Recursively call
        other modes when the token is recursive.

        """
        lines = []
        line = Line(tabwidth, level)

        for raw_token in self.TOKEN.split(self.source):
            if not raw_token:
                continue

            for token in self.create_tokens(raw_token):
                if token.newline:
                    lines.append(line)
                    line = next(line)
                elif token.recursive:
                    lines.append(
                        token.mode(token.text).indent(tabwidth, line.level).rstrip("\n")
                    )
                else:
                    line.append(token)

        # At the end of my money, I always have a little bit of month
        # left over - Loesje
        if line:
            lines.append(line)

        return lines

    def create_tokens(self, raw_token):
        """
        Given a raw token string, create one or more tokens.

        """
        tokens = []
        token_type = self.get_token_type(raw_token)
        if token_type is Comment:

            # Split token string into first line, middle, and last line
            head, body, tail = filter(bool, re.split(r"(^.*)\n|\n(.*$)", raw_token))
            tokens.append(Token.Open(head))
            tokens.append(Token.Newline())
            tokens.append(Token.Recursive(body, mode=Comment))
            tokens.append(Token.Newline())
            tokens.append(Token.Close(tail))

        elif "\n" in raw_token:

            # Create a separate token for each line in the token string
            for token in re.split("(\n)", raw_token):
                if token == "\n":
                    tokens.append(Token.Newline())
                elif token:
                    tokens.append(token_type(token))
                    token_type = Token.Text
        else:
            tokens.append(token_type(raw_token))

        return tokens

    def get_token_type(self, raw_token):
        """
        Given the raw token string, determine what type it is.

        """
        if raw_token.startswith("{% comment"):
            return Comment
        if raw_token.startswith("{%"):
            if tag_name := re.search(r"(\w+)", raw_token):
                if tag_name.group(1) in self.DJANGO_OPENING_TAGS:
                    return Token.Open
                if tag_name.group(1) in self.DJANGO_OPENING_AND_CLOSING_TAGS:
                    return Token.OpenAndClose
                if tag_name.group(1) in self.DJANGO_CLOSING_TAGS:
                    return Token.Close

        return Token.Text


class DjHTML(Mode):
    """
    This mode is the entrypoint of DjHTML. Usage:

    >>> DjHTML(input_string).indent(tabwidth=4)

    """

    STYLE = r"<style.*?</style>"
    SCRIPT = r"<script.*?</script>"
    COMMENT = r"<!--.*?-->"
    PRE = r"<pre.*?</pre>"
    TAG = r"<.*?>"
    TOKEN = re.compile(
        Mode.TOKEN.pattern + f"|({STYLE})|({SCRIPT})|({COMMENT})|({PRE})|({TAG})"
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

    def create_tokens(self, raw_token):
        """
        Create recursive tokens when a <style> or <script> tag is
        encountered.

        """
        tokens = []
        token_type = self.get_token_type(raw_token)

        if token_type is DjCSS:
            match = re.match(r"(?s)(<.*?>)(.*)(</style>)", raw_token)
            tokens.append(Token.Open(match.group(1)))
            tokens.append(Token.Newline())
            tokens.append(Token.Recursive(match.group(2).strip("\n"), mode=DjCSS))
            tokens.append(Token.Newline())
            tokens.append(Token.Close(match.group(3)))
            return tokens

        if token_type is DjJS:
            match = re.match(r"(?s)(<.*?>)(.*)(</script>)", raw_token)
            tokens.append(Token.Open(match.group(1)))
            tokens.append(Token.Newline())
            if re.match(r'<script[^>]+type="text/template"', raw_token):
                tokens.append(Token.Recursive(match.group(2).strip("\n"), mode=DjHTML))
            else:
                tokens.append(Token.Recursive(match.group(2).strip("\n"), mode=DjJS))
            tokens.append(Token.Newline())
            tokens.append(Token.Close(match.group(3)))
            return tokens

        return super().create_tokens(raw_token)

    def get_token_type(self, raw_token):
        if raw_token.startswith("<style"):
            if "\n" in raw_token:
                return DjCSS
            return Token.Text
        if raw_token.startswith("<script"):
            if "\n" in raw_token:
                return DjJS
            return Token.Text
        if raw_token.startswith("<!--"):
            if "\n" in raw_token:
                return Comment
            return Token.Text
        if raw_token.startswith("<pre"):
            if "\n" in raw_token:
                return Comment
            return Token.Text

        if raw_token.startswith("<"):
            if tag_name := re.search(r"(\w+)", raw_token):
                if tag_name.group(1).lower() in self.IGNORE_TAGS:
                    return Token.Text
                if raw_token.endswith("/>"):
                    return Token.Text
                if raw_token.startswith("</"):
                    return Token.Close
                return Token.Open

        return super().get_token_type(raw_token)


class DjCSS(Mode):
    """
    Mode for indenting CSS.

    """

    BRACES = r"[\{\}]"
    COMMENT = r"/\*.*?\*/"
    TOKEN = re.compile(Mode.TOKEN.pattern + f"|({BRACES})|({COMMENT})")

    def indent(self, tabwidth, level=0):
        lines = self.tokenize(tabwidth, level)
        for line in lines:
            if isinstance(line, Line):
                if line.text.startswith("*/"):
                    line.offset = 1
        return "".join([str(line) for line in lines])

    def get_token_type(self, raw_token):
        if raw_token == "{":
            return Token.Open
        if raw_token == "}":
            return Token.Close
        if raw_token.startswith("/*"):
            if "\n" in raw_token:
                return Comment
            return Token.Text
        return super().get_token_type(raw_token)


class DjJS(Mode):
    """
    Mode for indenting Javascript.

    """

    STRING = r"[\"'`].*?[\"'`]"
    BRACES = r"[\{\[\(\)\]\}]"
    COMMENT = DjCSS.COMMENT
    TOKEN = re.compile(Mode.TOKEN.pattern + f"|({STRING})|({BRACES})|({COMMENT})")

    def indent(self, tabwidth, level=0):
        lines = self.tokenize(tabwidth, level)
        for line in lines:
            if isinstance(line, Line):
                if line.text.startswith("."):
                    line.offset = tabwidth
                if line.text.startswith("*/"):
                    line.offset = 1
        return "".join([str(line) for line in lines])

    def get_token_type(self, raw_token):
        if raw_token in "{[(":
            return Token.Open
        if raw_token in "}])":
            return Token.Close
        if raw_token.startswith(("'", '"')):
            return Token.Text
        if raw_token.startswith("`"):
            if "\n" in raw_token:
                return Comment
            return Token.Text
        if raw_token.startswith("/*"):
            if "\n" in raw_token:
                return Comment
            return Token.Text
        return super().get_token_type(raw_token)


class Comment(Mode):
    """
    Mode for comments.

    """

    def indent(self, *args, **kwargs):
        return self.source
