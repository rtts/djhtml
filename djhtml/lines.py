class Line:
    """
    A single output line not including the final newline.

    """

    def __init__(self, tokens=None, level=0, offset=0, ignore=False):
        self.tokens = tokens or []
        self.level = level
        self.offset = offset
        self.ignore = ignore

    def append(self, token):
        """
        Append tokens to the line.

        """
        self.tokens.append(token)

    @property
    def text(self):
        """
        The text of this line without leading/trailing spaces.

        """
        return "".join([str(token) for token in self.tokens]).strip()

    def indent(self, tabwidth):
        """
        The final, indented text of this line. Make sure to set the level
        and optionally offset before calling this method.

        """
        if self.ignore:
            return "".join([str(token) for token in self.tokens])
        if self.text:
            spaces = tabwidth * self.level + self.offset
            return " " * spaces + self.text
        return ""

    def __bool__(self):
        return bool(self.tokens)

    def __len__(self):
        return len(self.text)

    def __repr__(self):
        kwargs = ""
        for attr in ["level", "offset", "ignore"]:
            if value := getattr(self, attr):
                kwargs += f", {attr}={value}"
        return f"Line({repr(self.tokens)}{kwargs})"
