class Line:
    """
    A single output line not including the final newline.

    """

    def __init__(self, tokens=None, level=0, offset=0, ignore=False):
        """
        Lines are currently never instantiated with arguments, but
        that doesn't mean they can't.

        """
        self.tokens = tokens or []
        self.level = level
        self.offset = offset
        self.ignore = ignore

    def append(self, token):
        """
        Append token to line.

        """
        self.tokens.append(token)

    @property
    def text(self):
        """
        The text of this line including the original
        leading/trailing spaces.

        """
        return "".join([token.text for token in self.tokens])

    @property
    def first_token(self):
        """
        The first non-empty token of this line.

        """
        for token in self.tokens:
            if token.text.strip():
                return token

    @property
    def indents(self):
        """
        Whether this line has more opening than closing tokens.

        """
        return len([token for token in self.tokens if token.indents]) > len(
            [token for token in self.tokens if token.dedents]
        )

    def indent(self, tabwidth):
        """
        The final, indented text of this line.

        """
        if self.ignore:
            return self.text
        if self.text:
            spaces = tabwidth * self.level + self.offset
            return " " * spaces + self.text.strip()
        return ""

    def __len__(self):
        """
        The length of the line (so far), excluding the whitespace
        at the beginning. Be careful calling len() because it might
        result in trailing spaces being counted that will be removed
        by indent().

        """
        return len(self.text.lstrip())

    def __repr__(self):
        kwargs = ""
        for attr in ["level", "offset", "ignore"]:
            if value := getattr(self, attr):
                kwargs += f", {attr}={value}"
        return f"Line({repr(self.tokens)}{kwargs})"
