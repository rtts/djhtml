import re

from .lines import Line
from .tokens import Token


class DjText:
    """
    Mode for indenting text files that contain Django template tags.
    Also serves as the base class for the other modes:

    - DjHTML
    - DjCSS
    - DjJS
    - DjNoOp

    """

    TAG = r"\{%.*?%\}"
    LINECOMMENT = r"{#.*?#}"
    BLOCKCOMMENT = r"{% *comment.*?endcomment *%}"
    TOKEN = re.compile(f"(?s)({LINECOMMENT})|({BLOCKCOMMENT})|({TAG})")

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
        "localize",
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
        "endlocalize",
        "endblocktrans",
        "endblocktranslate",
    ]

    def __init__(self, source, level=0, line_nr=1):
        self.level = level
        self.line_nr = line_nr
        self.source = source

    def indent(self, tabwidth):
        """
        Return the indented text as a single string.

        """
        lines = self.tokenize(tabwidth)
        self.parse(lines)
        return "".join([str(line) for line in lines])

    def parse(self, lines):
        """
        You found the top-secret indenting algorithm!

        """
        stack = []
        for line in lines:
            first_token = True
            for token in line.tokens:

                # When a dedenting token is found, match it with the
                # token at the top of the stack. If there is no match,
                # raise a syntax error.
                if token.dedents:
                    try:
                        opening_token = stack.pop()
                    except IndexError:
                        raise SyntaxError(
                            f"found closing “{token.text}” on line {token.line_nr} that"
                            " was never opened."
                        )
                    if token.expect and token.expect != opening_token.expect:
                        raise SyntaxError(
                            f"found closing “{token.text}” on line {token.line_nr}"
                            f" while expecting “{opening_token.expect}”."
                        )

                    # If this dedenting token is the first in line,
                    # it's somewhat special: the line level will be
                    # set to to the line level of the corresponding
                    # opening token.
                    if first_token:
                        line.level = opening_token.level

                # If the first token is _not_ a dedenting token, the
                # line level will one higher than that of the token at
                # the top of the stack.
                elif first_token:
                    line.level = stack[-1].level + 1 if stack else self.level

                # Push indenting tokens onto the stack. Note that some
                # tokens can be both indenting and dedenting (e.g.,
                # ``{% else %}``), hence the if instead of elif.
                if token.indents:
                    token.level = line.level
                    stack.append(token)

                # Subsequent tokens have no effect on the line level
                # (but tokens with only spaces don't count).
                if token.text.strip():
                    first_token = False

        # Ensure the stack is empty at the end of the run.
        if stack:
            token = stack.pop()
            raise SyntaxError(
                f"found opening “{token.text}” on line {token.line_nr} that wasn’t"
                " closed."
            )

    def tokenize(self, tabwidth):
        """
        Split the source text into tokens and place them on lines.

        """
        lines = []
        line_nr = self.line_nr
        line = Line(tabwidth)

        for raw_token in self.TOKEN.split(self.source):
            if not raw_token:
                continue

            for token in self.create_tokens(raw_token, line_nr):
                if token.newline:
                    lines.append(line)
                    line = Line(tabwidth)
                    line_nr += 1

                elif token:
                    line.append(token)
                    line_nr += token.text.count("\n")

        # At the end of my money, I always have a little bit of month
        # left over - Loesje
        if line:
            lines.append(line)

        return lines

    def create_tokens(self, raw_token, line_nr):
        """
        Given a raw token string, return a list of tokens.

        """
        if re.match(r"{% *comment.*\n.*\n", raw_token):
            return self.create_noop_tokens(raw_token, line_nr)

        if "\n" in raw_token:
            return self.split_tokens(raw_token, line_nr)

        return [self.create_token(raw_token, line_nr)]

    def create_token(self, raw_token, line_nr):
        """
        Given a raw token string, return a single token.

        """
        if raw_token.startswith("{%"):
            if tag := re.search(r"(\w+)", raw_token):
                name = tag.group(1)

                # The "expect" value should really be set to the
                # expected end tag of this block. However, Django's
                # elif, else and empty tags are throwing soot in the
                # food.
                expect = "{% endsomething %}"
                if name in self.DJANGO_OPENING_TAGS:
                    return Token.Open(raw_token, line_nr, expect)
                if name in self.DJANGO_OPENING_AND_CLOSING_TAGS:
                    return Token.OpenAndClose(raw_token, line_nr, expect)
                if name in self.DJANGO_CLOSING_TAGS:
                    return Token.Close(raw_token, line_nr, expect)

        return Token.Text(raw_token, line_nr)

    def create_noop_tokens(self, raw_token, line_nr):
        """
        Create 3 tokens: an opening one, a recursive one, and a closing one.

        """
        tokens = []
        lines = raw_token.split("\n")
        head = lines[0]
        body = "\n".join(lines[1:-1])
        tail = lines[-1]

        tokens.append(Token.Open(head, line_nr))
        tokens.append(Token.Newline())
        tokens.append(Token.Recursive(body + "\n", line_nr + 1, mode=DjNoOp))
        tokens.append(Token.Newline())
        tokens.append(Token.Close(tail, line_nr + raw_token.count("\n")))

        return tokens

    def split_tokens(self, raw_token, line_nr):
        """
        Create a separate token for each line in the token string.

        """
        tokens = []
        for token in raw_token.split("\n"):
            tokens.append(self.create_token(token, line_nr))
            tokens.append(Token.Newline())

        # Omit final newline token
        return tokens[:-1]


class DjHTML(DjText):
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
        DjText.TOKEN.pattern + f"|({STYLE})|({SCRIPT})|({COMMENT})|({PRE})|({TAG})"
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

    def indent(self, tabwidth):
        lines = self.tokenize(tabwidth)
        self.parse(lines)
        for line in lines:
            if isinstance(line, Line) and line.text.startswith(">"):
                line.offset -= tabwidth

        return "".join([str(line) for line in lines])

    def create_tokens(self, raw_token, line_nr):
        if re.match(r"<style[ >].*\n.*\n", raw_token):
            return self.create_style_tokens(raw_token, line_nr)
        if re.match(r"<script[ >].*\n.*\n", raw_token):
            return self.create_script_tokens(raw_token, line_nr)
        if re.match(r"<pre[ >].*\n.*\n", raw_token):
            return self.create_noop_tokens(raw_token, line_nr)
        if re.match(r"<!--.*\n.*\n", raw_token):
            return self.create_noop_tokens(raw_token, line_nr)

        return super().create_tokens(raw_token, line_nr)

    def create_token(self, raw_token, line_nr):
        if raw_token.startswith(("<style", "<script", "<pre", "<!--")):
            return Token.Text(raw_token, line_nr)

        if raw_token.startswith("<"):
            if tag_name := re.match(r"<[/!]?(\w+)", raw_token):
                name = tag_name.group(1).lower()
                if name in self.IGNORE_TAGS:
                    return Token.Text(raw_token, line_nr)
                if raw_token.endswith("/>"):
                    return Token.Text(raw_token, line_nr)
                if raw_token.startswith("</"):
                    return Token.Close(raw_token, line_nr, f"</{name}>")
                return Token.Open(raw_token, line_nr, f"</{name}>")

        return super().create_token(raw_token, line_nr)

    def create_style_tokens(self, raw_token, line_nr):
        tokens = []
        match = re.match(r"(?s)(<.*?>)(.*)(</style>)", raw_token)

        tokens.append(Token.Open(match.group(1), line_nr))
        tokens.append(Token.Newline())
        tokens.append(Token.Recursive(match.group(2)[1:], line_nr + 1, mode=DjCSS))
        tokens.append(Token.Newline())
        tokens.append(Token.Close(match.group(3), line_nr + raw_token.count("\n")))

        return tokens

    def create_script_tokens(self, raw_token, line_nr):
        tokens = []
        match = re.match(r"(?s)(<.*?>)(.*)(</script>)", raw_token)

        tokens.append(Token.Open(match.group(1), line_nr))
        tokens.append(Token.Newline())
        if re.match(r'<script[^>]+type="text/template"', raw_token):
            tokens.append(Token.Recursive(match.group(2)[1:], line_nr + 1, mode=DjHTML))
        else:
            tokens.append(Token.Recursive(match.group(2)[1:], line_nr + 1, mode=DjJS))
        tokens.append(Token.Newline())
        tokens.append(Token.Close(match.group(3), line_nr + raw_token.count("\n")))

        return tokens


class DjCSS(DjText):
    """
    Mode for indenting CSS.

    """

    BRACES = r"[\{\}]"
    COMMENT = r"/\*.*?\*/"
    TOKEN = re.compile(DjText.TOKEN.pattern + f"|({BRACES})|({COMMENT})")

    def indent(self, tabwidth):
        lines = self.tokenize(tabwidth)
        self.parse(lines)
        for line in lines:
            if isinstance(line, Line) and line.text.startswith("*/"):
                line.offset = 1

        return "".join([str(line) for line in lines])

    def create_tokens(self, raw_token, line_nr):
        if re.search(r"\n.*\n", raw_token) and raw_token.startswith("/*"):
            return self.create_noop_tokens(raw_token, line_nr)

        if raw_token == "{":
            return [Token.Open(raw_token, line_nr, "{")]
        if raw_token == "}":
            return [Token.Close(raw_token, line_nr, "{")]

        return super().create_tokens(raw_token, line_nr)


class DjJS(DjText):
    """
    Mode for indenting Javascript.

    """

    STRING1 = r'".*?"'
    STRING2 = r"'.*?'"
    STRING3 = r"`.*?`"
    BRACES = r"[\{\[\(\)\]\}]"
    COMMENT = DjCSS.COMMENT
    TOKEN = re.compile(
        DjText.TOKEN.pattern
        + f"|({STRING1})|({STRING2})|({STRING3})|({BRACES})|({COMMENT})"
    )

    def indent(self, tabwidth):
        lines = self.tokenize(tabwidth)
        self.parse(lines)
        for line in lines:
            if isinstance(line, Line):
                if line.text.startswith("."):
                    line.offset = tabwidth
                if line.text.startswith("*/"):
                    line.offset = 1
        return "".join([str(line) for line in lines])

    def create_tokens(self, raw_token, line_nr):
        if re.search(r"\n.*\n", raw_token):
            if raw_token.startswith("/*"):
                return self.create_noop_tokens(raw_token, line_nr)
            if raw_token.startswith("`"):
                return self.create_noop_tokens(raw_token, line_nr)

        if raw_token.startswith(('"', "'")):
            return super().create_tokens(raw_token, line_nr)
        if raw_token == "{":
            return [Token.Open(raw_token, line_nr, "}")]
        if raw_token == "}":
            return [Token.Close(raw_token, line_nr, "}")]
        if raw_token == "[":
            return [Token.Open(raw_token, line_nr, "]")]
        if raw_token == "]":
            return [Token.Close(raw_token, line_nr, "]")]
        if raw_token == "(":
            return [Token.Open(raw_token, line_nr, "]")]
        if raw_token == ")":
            return [Token.Close(raw_token, line_nr, "]")]

        return super().create_tokens(raw_token, line_nr)


class DjNoOp(DjText):
    """
    Mode that does nothing. Used for comments.

    """

    def indent(self, *args):
        return self.source
