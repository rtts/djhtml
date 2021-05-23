class Line:
    """
    A single output line including the final newline.

    """

    def __init__(self, nr=1):
        self.nr = nr
        self.tokens = []
        self.level = 0

    def append(self, token):
        """
        Append tokens to the line.

        """
        token.line_nr = self.nr
        self.tokens.append(token)

    @property
    def text(self):
        """
        The unindented text of this line without leading/trailing spaces.

        """
        return "".join([str(token) for token in self.tokens]).strip()

    def indent(self, tabwidth):
        """
        The final, indented text of this line. Make sure to set the level
        and optionally offset before calling this method.

        """
        if self.tokens:
            if self.tokens[0].ignore:
                return "".join([str(token) for token in self.tokens]) + "\n"
            elif self.text:
                offset = self.tokens[0].offset * tabwidth
                spaces = tabwidth * self.level + offset
                return " " * spaces + self.text + "\n"
        return "\n"

    def __repr__(self):
        return repr(self.tokens)

    def __bool__(self):
        return bool(self.tokens and self.text)

    def __next__(self):
        return Line(nr=self.nr + 1)
