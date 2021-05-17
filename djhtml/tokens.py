class Token:
    """
    Container class for token types.

    """

    class _Base:
        indents = False
        dedents = False
        newline = False
        recursive = False

        def __init__(self, text, line_nr, expect=""):
            self.text = text
            self.line_nr = line_nr
            self.expect = expect

        def __bool__(self):
            return bool(self.text)

        def __str__(self):
            return self.text

        def __repr__(self):
            return f"({self.__class__.__name__}:{repr(self.text)})"

    class Newline(_Base):
        newline = True

        def __init__(self):
            pass

    class Recursive(_Base):
        recursive = True

        def __init__(self, text, line_nr, mode):
            self.text = text
            self.line_nr = line_nr
            self.mode = mode

    class Text(_Base):
        pass

    class Open(_Base):
        indents = True

    class Close(_Base):
        dedents = True

    class OpenAndClose(_Base):
        indents = True
        dedents = True
