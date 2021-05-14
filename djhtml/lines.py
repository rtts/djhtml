class Line:
    """
    A single output line including the final newline.

    """

    def __init__(self, tabwidth):
        self.tabwidth = tabwidth
        self.text = ""

    def append(self, text):
        self.text += text

    def finish(self, level):
        self.level = level

    def __str__(self):
        if self.text:
            return " " * self.tabwidth * self.level + self.text + "\n"
        return "\n"

    def __repr__(self):
        text = self.text.replace("\n", r"\n")
        return f'"{text}"'
