class Token:
    """
    Container class for token types.

    """

    class _Base:
        indents = False
        dedents = False
        ignore = False
        is_hard = False

        def __init__(self, text, kind="", offset=0):
            self.text = text
            self.kind = kind
            self.offset = offset

        def __str__(self):
            return self.text

        def __repr__(self):
            return f"({self.__class__.__name__}:{repr(self.text)})"

    class Text(_Base):
        pass

    class Ignore(_Base):
        ignore = True

    class Open(_Base):
        indents = True

    class OpenHard(Open):
        is_hard = True

    class Close(_Base):
        dedents = True

    class CloseHard(Close):
        is_hard = True

    class OpenAndClose(_Base):
        indents = True
        dedents = True
