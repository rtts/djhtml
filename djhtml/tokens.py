class Token:
    """
    Container class for token types.

    """

    class _Base:
        indent = False
        dedent = False
        newline = False
        recursive = False

        def __init__(self, text):
            self.text = text

        def __str__(self):
            return self.text

        def __repr__(self):
            return f"({self.__class__.__name__}:{repr(self.text)})"

    class Newline(_Base):
        newline = True
        text = "\n"

        def __init__(self):
            pass

    class Recursive(_Base):
        recursive = True

        def __init__(self, text, mode):
            super().__init__(text)
            self.mode = mode

    class Text(_Base):
        pass

    class Open(_Base):
        indent = True

    class Close(_Base):
        dedent = True

    class OpenAndClose(_Base):
        indent = True
        dedent = True
