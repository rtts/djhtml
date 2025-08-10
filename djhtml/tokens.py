from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .modes import BaseMode


class Token:
    """
    Container class for token types.

    """

    class BaseToken:
        indents = False
        dedents = False
        ignore = False
        is_double = False

        def __init__(
            self,
            text: str,
            *,
            mode: type["BaseMode"],
            level: int = 0,
            relative: int = 0,
            absolute: int = 0,
            ignore: bool = False,
        ) -> None:
            """
            Tokens must have a text and a mode class. The level
            represents the line level of opening tokens and is set
            afterwards by the parser. This violates the principle of
            encapsulation, but makes sense because the line level can
            only be determined after the tokenization is complete.

            """
            self.text = text
            self.mode = mode
            self.level = level
            self.relative = relative
            self.absolute = absolute
            self.ignore = ignore

        def __repr__(self) -> str:
            kwargs = f", mode={self.mode.__name__}"
            for attr in ["level", "relative", "absolute", "ignore"]:
                if value := getattr(self, attr):
                    kwargs += f", {attr}={value!r}"
            return f"{self.__class__.__name__}({self.text!r}{kwargs})"

    class Text(BaseToken):
        pass

    class Open(BaseToken):
        indents = True

    class OpenDouble(BaseToken):
        indents = True
        is_double = True

    class Close(BaseToken):
        dedents = True

    class CloseDouble(BaseToken):
        dedents = True
        is_double = True

    class CloseAndOpen(BaseToken):
        indents = True
        dedents = True
