import re

from .lines import Line
from .tokens import Token


class DjTXT:
    """
    Mode for indenting text files that contain Django/Jinja template tags.
    Also serves as the base class for the other modes:

    - DjHTML
    - DjCSS
    - DjJS

    """

    RAW_TOKENS = [
        r"\n",
        r"{%[-\+]?.*?[-\+]?%}",
        r"{#.*?#}",
        r"{#",
    ]
    OPENING_AND_CLOSING_TAGS = [
        "elif",
        "else",
        "empty",
        "plural",
    ]
    AMBIGUOUS_BLOCK_TAGS = {
        # token_name: (regex_if_block, regex_if_not_block)
        "set": (None, " = "),
        "video": (" as ", None),
    }
    FMT_ON = r"{# fmt:on #}"
    FMT_OFF = r"{# fmt:off #}"
    OPENING_TAG = r"{%[-\+]? *(\w+).*?[-\+]?%}"

    def __init__(self, source="", return_mode=None):
        self.source = source
        self.return_mode = return_mode or self
        self.token_re = compile_re(self.RAW_TOKENS)

    def indent(self, tabwidth):
        """
        Return the indented text as a single string.

        """
        self.tokenize()
        self.parse()
        return "".join([line.indent(tabwidth) for line in self.lines])

    def parse(self):
        """
        You found the top-secret indenting algorithm!

        """
        stack = []
        for line in self.lines:
            first_token = True
            for token in line.tokens:
                opening_token = None

                # When a dedenting token is found, match it with the
                # token at the top of the stack.
                if token.dedents:
                    try:
                        if stack[-1].kind == token.kind and stack[-1].is_hard == token.is_hard:
                            opening_token = stack.pop()
                        elif token.kind == "django":
                            opening_token = stack.pop()
                            while opening_token.kind != token.kind:
                                opening_token = stack.pop()
                        elif first_token:
                            # This closing token could not be matched.
                            # Instead of erroring out, set the line level
                            # to what it would have been with a
                            # regular text token.

                            # If there is any OpenHard token in the set and current token is CloseHard
                            # then let's move back to OpenHard.
                            if token.is_hard and any(t.is_hard and t.indents for t in stack):
                                s = stack.pop()
                                while not s.is_hard or not s.indents:
                                    s = stack.pop()

                            line.level = stack[-1].level + 1
                    except IndexError:
                        line.level = 0

                    # If this dedenting token is the first in line,
                    # set the line level to the line level of the
                    # corresponding opening token.
                    if first_token and opening_token:
                        line.level = opening_token.level

                # If the first token is not a dedenting token, the
                # line level will be one higher than that of the token
                # at the top of the stack.
                elif first_token:
                    line.level = stack[-1].level + 1 if stack else 0

                # Push indenting tokens onto the stack. Note that some
                # tokens can be both indenting and dedenting (e.g.,
                # ``{% else %}``), hence the if instead of elif.
                if token.indents:
                    token.level = opening_token.level if opening_token else line.level
                    stack.append(token)

                # Subsequent tokens have no effect on the line level
                # (but tokens with only spaces don't count).
                if token.text.strip():
                    first_token = False

    def tokenize(self):
        """
        Split the source text into tokens and place them on lines.

        """
        self.lines = []
        line = Line()
        mode = self
        src = self.source

        while True:
            try:
                # Split the source at the first occurrence of one of
                # the current mode's raw tokens.
                head, raw_token, tail = mode.token_re.split(src, maxsplit=1)

            except ValueError:
                # We've reached the final line!
                if src:
                    line.append(mode.create_token(src, ""))
                if line:
                    self.lines.append(line)
                break

            if head:
                # Create a token from the head. This will always be a
                # text token (and the next mode will always be the
                # current mode), but we don't assume that here.
                line.append(mode.create_token(head, raw_token + tail))
                mode = next(mode)

            if raw_token == "\n":
                self.lines.append(line)
                line = next(line)

            else:
                # Ask the mode to create a token and to provide a new
                # mode for the next iteration of the loop.
                line.append(mode.create_token(raw_token, tail))
                mode = next(mode)

            # Set the new source to the old tail for the next iteration.
            src = tail

    def create_token(self, raw_token, src):
        """
        Given a raw token string, return a single token (and internally
        set the next mode).

        """
        kind = "django"
        self.next_mode = self
        token = Token.Text(raw_token)

        tag = re.match(self.OPENING_TAG, raw_token)
        if tag:
            name = tag.group(1)
            if name in ["comment", "verbatim", "raw"]:
                token = Token.Open(raw_token, kind)
                self.next_mode = Comment(
                    r"{%[-\+]? *end" + name + r"(?: .*?|)%}", self, kind
                )
            elif self._has_closing_token(name, raw_token, src):
                token = Token.Open(raw_token, kind)
            elif name in self.OPENING_AND_CLOSING_TAGS:
                token = Token.OpenAndClose(raw_token, kind)
            elif name.startswith("end"):
                token = Token.Close(raw_token, kind)
            return token

        if re.match(self.FMT_OFF, raw_token):
            token = Token.Open(raw_token, kind)
            self.next_mode = Comment(self.FMT_ON, self, kind)
            return token

        if raw_token == "{#":
            token = Token.Open(raw_token, kind)
            self.next_mode = Comment(r"#\}", self, kind)

        return token

    def _has_closing_token(self, name, raw_token, src):
        if not re.search(f"{{%[-\\+]? *end{name}(?: .*?|)%}}", src):
            return False
        regex = self.AMBIGUOUS_BLOCK_TAGS.get(name)
        if regex:
            if regex[0]:
                return re.search(regex[0], raw_token)
            if regex[1]:
                return not re.search(regex[1], raw_token)
        return True

    def debug(self):
        self.tokenize()
        return "\n".join(
            [" ".join([repr(token) for token in line.tokens]) for line in self.lines]
        )

    def __next__(self):
        return self.next_mode


class DjHTML(DjTXT):
    """
    This mode is the entrypoint of DjHTML. Usage:

    >>> DjHTML(input_string).indent(tabwidth=4)

    """

    RAW_TOKENS = DjTXT.RAW_TOKENS + [
        r"<pre.*?>",
        r"</.*?>",
        r"<!--",
        r"<",
    ]

    IGNORE_TAGS = [
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

    def create_token(self, raw_token, src):
        kind = "html"
        self.next_mode = self

        if raw_token == "<":
            tag = re.match(r"(\w+)[^:]", src)
            if tag:
                token = Token.Open(raw_token, kind)
                self.next_mode = InsideHTMLTag(tag[1], self)
            else:
                token = Token.Text(raw_token)
            return token

        if raw_token == "<!--":
            self.next_mode = Comment("-->", self, kind)
            return Token.Open(raw_token, kind)

        if re.match("<pre.*?>", raw_token):
            self.next_mode = Comment("</pre>", self, kind)
            return Token.Open(raw_token, kind)

        if raw_token.startswith("</"):
            tagname = re.search(r"\w+", raw_token)
            if tagname:
                if tagname[0].lower() in self.IGNORE_TAGS:
                    return Token.Text(raw_token)
            return Token.Close(raw_token, kind)

        return super().create_token(raw_token, src)


class DjCSS(DjTXT):
    """
    Mode for indenting CSS.

    """

    RAW_TOKENS = DjTXT.RAW_TOKENS + [
        r"</style>",
        r"{",
        r"}",
        r"/\*",
    ]

    def create_token(self, raw_token, src):
        kind = "css"
        self.next_mode = self

        if raw_token == "{":
            return Token.Open(raw_token, kind)
        if raw_token == "}":
            return Token.Close(raw_token, kind)
        if raw_token == "/*":
            self.next_mode = Comment(r"\*/", self, kind)
            return Token.Open(raw_token, kind)
        if raw_token == "</style>":
            self.next_mode = self.return_mode
            return Token.Close(raw_token, "html")

        return super().create_token(raw_token, src)


class DjJS(DjTXT):
    """
    Mode for indenting Javascript.

    """

    RAW_TOKENS = DjTXT.RAW_TOKENS + [
        r"</script>",
        r'".*?"',
        r"'.*?'",
        r"`.*?`",
        r"`",
        r"[\{\[\(\)\]\}]",
        r"//.*",
        r"/\*",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hard_indents = 0
        self.opened_brackets = 0

    def create_token(self, raw_token, src):
        kind = "javascript"
        self.next_mode = self

        if raw_token.strip() == "switch":
            self.hard_indents = self.hard_indents + 1

        if self.hard_indents:
            if raw_token == "{":
                self.opened_brackets += 1
                if self.opened_brackets == self.hard_indents:
                    return Token.OpenHard(raw_token, kind)
            elif raw_token == "}":
                if self.opened_brackets == self.hard_indents:
                    self.opened_brackets -= 1
                    self.hard_indents -= 1
                    return Token.CloseHard(raw_token, kind)
                self.opened_brackets -= 1

        if raw_token in "{[(":
            return Token.Open(raw_token, kind)
        if raw_token in ")]}":
            return Token.Close(raw_token, kind)
        if raw_token == "`":
            self.next_mode = Comment("`", self, kind)
            return Token.Open(raw_token, kind)
        if raw_token == "/*":
            self.next_mode = Comment(r"\*/", self, kind)
            return Token.Open(raw_token, kind)
        if raw_token.lstrip().startswith("."):
            return Token.Text(raw_token, offset=1)
        if raw_token.lstrip().startswith("case "):
            return Token.OpenAndClose(raw_token, kind)
        if raw_token.lstrip().startswith("default:"):
            return Token.OpenAndClose(raw_token, kind)
        if raw_token == "</script>":
            self.next_mode = self.return_mode
            return Token.Close(raw_token, "html")

        return super().create_token(raw_token, src)


# The following are "special" modes with different constructors.


class Comment(DjTXT):
    """
    Mode to create ignore tokens until an end tag is encountered.

    """

    def __init__(self, endtag, return_mode, kind):
        self.endtag = endtag
        self.return_mode = return_mode
        self.kind = kind
        self.token_re = compile_re([r"\n", endtag])

    def create_token(self, raw_token, src):
        self.next_mode = self
        if re.match(self.endtag, raw_token):
            self.next_mode = self.return_mode
            return Token.Close(raw_token, self.kind)
        return Token.Ignore(raw_token)


class InsideHTMLTag(DjTXT):
    """
    Welcome to the wondrous world between "<" and ">".

    """

    RAW_TOKENS = DjTXT.RAW_TOKENS + [r"/?>"]

    def __init__(self, tagname, return_mode):
        self.tagname = tagname
        self.return_mode = return_mode
        self.token_re = compile_re(self.RAW_TOKENS)

    def create_token(self, raw_token, src):
        kind = "html"
        self.next_mode = self

        if raw_token == "/>":
            self.next_mode = self.return_mode
            return Token.Close(raw_token, kind)
        elif raw_token == ">":
            if self.tagname.lower() in DjHTML.IGNORE_TAGS:
                self.next_mode = self.return_mode
                return Token.Close(raw_token, kind)
            else:
                if self.tagname == "style":
                    self.next_mode = DjCSS(return_mode=self.return_mode)
                elif self.tagname == "script":
                    self.next_mode = DjJS(return_mode=self.return_mode)
                else:
                    self.next_mode = self.return_mode
                return Token.OpenAndClose(raw_token, kind)
        elif "text/template" in raw_token:
            self.tagname = ""

        return super().create_token(raw_token, src)


def compile_re(raw_tokens):
    return re.compile("(" + "|".join(raw_tokens) + ")")
