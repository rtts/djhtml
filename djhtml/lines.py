class Line:
    """
    A single output line including the final newline.

    """

    def __init__(self, tabwidth):
        self.tabwidth = tabwidth
        self.tokens = []
        self.level = 0
        self.offset = 0

    def append(self, token):
        """
        Append tokens to the line.

        """
        self.tokens.append(token)

    @property
    def text(self):
        """
        The raw, unindented text of this line.

        """
        return "".join([str(token) for token in self.tokens]).strip()

    def __str__(self):
        """
        The final, indented text of this line. Make sure to set the level
        and optionally offset before calling ``str()``.

        """
        # If the line consists of a recursive token, return its
        # rendered output instead.
        if self.tokens and self.tokens[0].recursive:
            token = self.tokens[0]
            return token.mode(token.text, self.level, token.line_nr).indent(
                self.tabwidth
            )

        if self.text:
            spaces = self.tabwidth * self.level + self.offset
            return " " * spaces + self.text + "\n"
        return "\n"

    def __repr__(self):
        return repr(self.tokens)

    def __bool__(self):
        return bool(self.text)
