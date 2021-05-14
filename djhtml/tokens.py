import enum


class Types(enum.Enum):
    TEXT = enum.auto()
    DJANGO = enum.auto()
    HTML = enum.auto()
    CSSJS = enum.auto()


class Token:
    """
    Container class for token types.

    """

    class _Base:
        indent = False
        dedent = False

        def __init__(self, text, line_nr, mode=None):
            self.text = text
            self.line_nr = line_nr
            self.mode = mode

        def __repr__(self):
            return f"({self.__class__.__name__}:{repr(self.text)})"

    class Text(_Base):
        type = Types.TEXT

    class BlockOpen(_Base):
        type = Types.DJANGO
        indent = True

    class BlockClose(_Base):
        type = Types.DJANGO
        dedent = True

    class BlockOpenAndClose(_Base):
        type = Types.DJANGO
        indent = True
        dedent = True

    class TagOpen(_Base):
        type = Types.HTML
        indent = True

    class TagClose(_Base):
        type = Types.HTML
        dedent = True

    class BraceOpen(_Base):
        type = Types.CSSJS
        indent = True

    class BraceClose(_Base):
        type = Types.CSSJS
        dedent = True

    class Style(_Base):
        type = Types.HTML

    class Script(_Base):
        type = Types.HTML
