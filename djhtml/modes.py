import re

from .lines import Line
from .tokens import Token


class DjTXT:
    """
    Mode for indenting Django/Jinja template tags.
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
        r"{{.*?}}",
    ]
    CLOSING_AND_OPENING_TAGS = [
        "elif",
        "else",
        "empty",
        "plural",
    ]
    COMMENT_TAGS = [
        "comment",
        "verbatim",
        "raw",
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
        self.offsets = {"relative": 0, "absolute": 0}
        self.previous_offsets = []

    def indent(self, tabwidth):
        """
        Return the indented text as a single string.

        """
        self.tokenize()
        self.parse()
        return "\n".join([line.indent(tabwidth) for line in self.lines])

    def parse(self):
        """
        You found the top-secret indenting algorithm!

        """
        stack = []
        for line in self.lines:
            first_token = True
            for token in line.tokens:
                opening_token = None
                if stack:
                    # When a dedenting token is found, match it with
                    # the token at the top of the stack. To find out
                    # what each statement does, uncomment it and see
                    # which unittests fail.
                    if token.dedents:
                        if stack[-1].mode is token.mode:
                            opening_token = stack.pop()
                            if stack and opening_token.is_double:
                                opening_token = stack.pop()
                        elif token.mode is DjTXT:
                            opening_token = stack.pop()
                            while opening_token.mode is not DjTXT:
                                opening_token = stack.pop()
                        elif first_token:
                            line.level = stack[-1].level + 1

                        # Dedent!
                        if first_token and opening_token:
                            line.level = opening_token.level

                    else:
                        # Indent!
                        if token.is_double and stack[-1].is_double:
                            opening_token = stack.pop()
                        if stack and first_token:
                            line.level = stack[-1].level + 1

                if first_token:
                    line.level = line.level + token.relative
                    line.offset = token.absolute
                    line.ignore = token.ignore

                # Push indenting tokens onto the stack.
                if token.indents:
                    token.level = opening_token.level if opening_token else line.level
                    stack.append(token)

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
                    token, _ = mode.create_token(src, "", line)
                    line.append(token)
                self.lines.append(line)
                break

            if head:
                # Create a token from the head.
                token, mode = mode.create_token(head, raw_token + tail, line)
                line.append(token)

            if raw_token == "\n":
                self.lines.append(line)
                line = Line()

            else:
                # Create a token from the tail
                token, mode = mode.create_token(raw_token, tail, line)
                line.append(token)

            # Set the new source to the old tail for the next iteration.
            src = tail

    def create_token(self, raw_token, src, line):
        """
        Given a raw token string, return a single token and the
        next mode.

        """
        mode = self

        if tag := re.match(self.OPENING_TAG, raw_token):
            name = tag.group(1)
            if name in self.COMMENT_TAGS:
                token, mode = Token.Open(raw_token, mode=DjTXT, ignore=True,), Comment(
                    r"{%[-\+]? *end" + name + r"(?: .*?|)%}",
                    mode=DjTXT,
                    return_mode=self,
                )
            elif self._has_closing_token(name, raw_token, src):
                self.previous_offsets.append(self.offsets["relative"])
                token = Token.Open(raw_token, mode=DjTXT, **self.offsets)
                self.offsets["relative"] = 0
            elif name in self.CLOSING_AND_OPENING_TAGS:
                token = Token.CloseAndOpen(raw_token, mode=DjTXT, **self.offsets)
            elif name.startswith("end"):
                token = Token.Close(raw_token, mode=DjTXT, **self.offsets)
                try:
                    self.offsets["relative"] = self.previous_offsets.pop()
                except IndexError:
                    self.offsets["relative"] = 0
            else:
                token = Token.Text(raw_token, mode=DjTXT, **self.offsets)
        elif re.match(self.FMT_OFF, raw_token):
            token, mode = Token.Open(raw_token, mode=DjTXT, ignore=True), Comment(
                self.FMT_ON, mode=DjTXT, return_mode=self
            )
        elif raw_token == "{#":
            token, mode = Token.Open(raw_token, mode=DjTXT, ignore=True), Comment(
                r"#\}", mode=DjTXT, return_mode=self
            )
        else:
            token = Token.Text(raw_token, mode=self.__class__, **self.offsets)

        return token, mode

    def _has_closing_token(self, name, raw_token, src):
        if not re.search(f"{{%[-\\+]? *end{name}(?: .*?|)%}}", src):
            return False
        if regex := self.AMBIGUOUS_BLOCK_TAGS.get(name):
            if regex[0]:
                return re.search(regex[0], raw_token)
            if regex[1]:
                return not re.search(regex[1], raw_token)
        return True

    def debug(self):
        self.tokenize()
        self.parse()
        return "\n".join([repr(line) for line in self.lines])


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

    def create_token(self, raw_token, src, line):
        mode = self

        if raw_token == "<":
            if tag := re.match(r"([\w\-\.:]+)", src):
                token, mode = Token.Open(raw_token, mode=DjHTML), InsideHTMLTag(
                    tag[1], line, self
                )
            else:
                token = Token.Text(raw_token, mode=DjHTML)
        elif raw_token == "<!--":
            token, mode = Token.Open(raw_token, mode=DjHTML, ignore=True), Comment(
                "-->", mode=DjHTML, return_mode=self
            )
        elif re.match("<pre.*?>", raw_token):
            token, mode = Token.Open(raw_token, mode=DjHTML, ignore=True), Comment(
                "</pre>", mode=DjHTML, return_mode=self
            )
        elif raw_token.startswith("</"):
            token = Token.Close(raw_token, mode=DjHTML)
            if tagname := re.search(r"\w+", raw_token):
                if tagname[0].lower() in self.IGNORE_TAGS:
                    token = Token.Text(raw_token, mode=DjHTML)
        else:
            token, mode = super().create_token(raw_token, src, line)

        return token, mode


class DjCSS(DjTXT):
    """
    Mode for indenting CSS.

    """

    RAW_TOKENS = DjTXT.RAW_TOKENS + [
        r"</style>",
        r"[\{\(\)\}]",
        r"/\*",
        r"[\w-]+: ",
        r";",
    ]

    def create_token(self, raw_token, src, line):
        mode = self

        if raw_token in "{(":
            self.previous_offsets.append(self.offsets["relative"])
            token = Token.Open(raw_token, mode=DjCSS, **self.offsets)
            self.offsets["relative"] = 0
        elif raw_token in "})":
            token = Token.Close(raw_token, mode=DjCSS, **self.offsets)
            try:
                self.offsets["relative"] = self.previous_offsets.pop()
            except IndexError:
                self.offsets["relative"] = 0
        elif raw_token.endswith(": "):
            token = Token.Open(raw_token, mode=DjCSS, **self.offsets)
            self.offsets["relative"] = -1
            self.offsets["absolute"] = len(raw_token)
        elif raw_token == ";":
            self.offsets["relative"] = 0
            self.offsets["absolute"] = 0
            token = Token.Close(raw_token, mode=DjCSS, **self.offsets)
        elif raw_token == "/*":
            token, mode = Token.Open(raw_token, mode=DjCSS, ignore=True), Comment(
                r"\*/", mode=DjCSS, return_mode=self
            )
        elif raw_token == "</style>":
            token, mode = (
                Token.Close(raw_token, mode=self.return_mode.__class__),
                self.return_mode,
            )
        else:
            token, mode = super().create_token(raw_token, src, line)

        return token, mode


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

    def create_token(self, raw_token, src, line):
        mode = self

        if raw_token in "{[(":
            token = Token.Open(raw_token, mode=DjJS, **self.offsets)
        elif raw_token in ")]}":
            token = Token.Close(raw_token, mode=DjJS, **self.offsets)
        elif raw_token == "`":
            token, mode = Token.Open(raw_token, mode=DjJS, ignore=True), Comment(
                "`", mode=DjJS, return_mode=self
            )
        elif raw_token == "/*":
            token, mode = Token.Open(raw_token, mode=DjJS, ignore=True), Comment(
                r"\*/", mode=DjJS, return_mode=self
            )
        elif not line and raw_token.lstrip().startswith("."):
            self.offsets["relative"] = 1
            token = Token.Text(raw_token, mode=DjJS, **self.offsets)
        elif raw_token.lstrip().startswith(("case ", "default:")):
            token = Token.OpenDouble(raw_token, mode=DjJS)
            return token, mode
        elif raw_token == "</script>":
            token, mode = (
                Token.Close(raw_token, mode=self.return_mode.__class__),
                self.return_mode,
            )
        else:
            token, mode = super().create_token(raw_token, src, line)

        # Reset relative offset after creating first token in line.
        if not line:
            self.offsets["relative"] = 0

        return token, mode


# The following are "special" modes with different constructors.


class Comment(DjTXT):
    """
    Mode to create ignore tokens until an end tag is encountered.

    """

    def __init__(self, endtag, *, mode, return_mode):
        self.endtag = endtag
        self.mode = mode
        self.return_mode = return_mode
        self.token_re = compile_re([r"\n", endtag])

    def create_token(self, raw_token, src, line):
        if re.match(self.endtag, raw_token):
            return Token.Close(raw_token, mode=self.mode, ignore=True), self.return_mode
        return Token.Text(raw_token, mode=Comment, ignore=True), self


class InsideHTMLTag(DjTXT):
    """
    Welcome to the wondrous world between "<" and ">".

    """

    RAW_TOKENS = DjTXT.RAW_TOKENS + [r"/?>", r"[^ ='\">/]+=", r'"']

    def __init__(self, tagname, line, return_mode):
        self.tagname = tagname
        self.return_mode = return_mode
        self.token_re = compile_re(self.RAW_TOKENS)
        self.inside_attr = False
        self.offsets = dict(relative=-1, absolute=len(line) + len(tagname) + 2)
        self.previous_offsets = []

        # Pff...
        self.additional_offset = -len(tagname) - 1

    def create_token(self, raw_token, src, line):
        mode = self

        if line:
            self.additional_offset += len(raw_token)
        else:
            self.additional_offset = 0

        if "text/template" in raw_token:
            self.tagname = ""

        if raw_token == '"':
            if self.inside_attr:
                self.inside_attr = False
                self.offsets["absolute"] -= 1
                token = Token.Text(raw_token, mode=InsideHTMLTag, **self.offsets)
                self.offsets["absolute"] = self.previous_offset
            else:
                self.inside_attr = True
                self.previous_offset = self.offsets["absolute"]
                self.offsets["absolute"] += self.additional_offset
                token = Token.Text(raw_token, mode=InsideHTMLTag, **self.offsets)
        elif not self.inside_attr and raw_token == "/>":
            token, mode = Token.Close(raw_token, mode=DjHTML), self.return_mode
        elif not self.inside_attr and raw_token == ">":
            if self.tagname.lower() in DjHTML.IGNORE_TAGS:
                token, mode = Token.Close(raw_token, mode=DjHTML), self.return_mode
            elif self.tagname == "style":
                token, mode = Token.CloseAndOpen(raw_token, mode=DjHTML), DjCSS(
                    return_mode=self.return_mode
                )
            elif self.tagname == "script":
                token, mode = Token.CloseAndOpen(raw_token, mode=DjHTML), DjJS(
                    return_mode=self.return_mode
                )
            else:
                token, mode = (
                    Token.CloseAndOpen(raw_token, mode=DjHTML),
                    self.return_mode,
                )
        else:
            token, mode = super().create_token(raw_token, src, line)

        return token, mode


def compile_re(raw_tokens):
    return re.compile("(" + "|".join(raw_tokens) + ")")
