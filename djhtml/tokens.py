class Token:
    """
    Container class for token types.

    """

    class _Base:
        indents = False
        dedents = False
        ignore = False
        is_double = False

        def __init__(
            self, text, *, mode, level=0, relative=0, absolute=0, ignore=False
        ):
            self.text = text
            self.mode = mode
            self.level = level
            self.relative = relative
            self.absolute = absolute
            self.ignore = ignore

        def __str__(self):
            return self.text

        def __repr__(self):
            kwargs = f", mode={self.mode.__name__}"
            for attr in ["level", "relative", "absolute", "ignore"]:
                if value := getattr(self, attr):
                    kwargs += f", {attr}={value}"
            return f"{self.__class__.__name__}('{self.text}'{kwargs})"

    class Text(_Base):
        pass

    class Open(_Base):
        indents = True

    class OpenDouble(_Base):
        indents = True
        is_double = True

    class Close(_Base):
        dedents = True

    class CloseAndOpen(_Base):
        indents = True
        dedents = True
