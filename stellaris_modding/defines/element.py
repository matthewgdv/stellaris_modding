from __future__ import annotations

from typing import Type

from miscutils import ReprMixin
from subtypes import Str


class LexicalElementMeta(type):
    registry: dict[str, Type[LexicalElement]] = {}

    def __init__(cls: Type[LexicalElement], name: str, bases: tuple, namespace: dict) -> None:
        cls.registry[name] = cls


class LexicalElement(ReprMixin, metaclass=LexicalElementMeta):
    def __init__(self, text: str) -> None:
        pass

    @classmethod
    def from_text(cls, text: str) -> LexicalElement:
        valid_elements = [element_cls for element_cls in cls.registry.values() if element_cls.is_valid(text)]
        if len(valid_elements) == 1:
            return valid_elements[0](text)
        elif not valid_elements:
            raise ValueError(f"Don't know how to parse '{text}' into a valid {LexicalElement.__name__}")
        else:
            raise ValueError(f"Element is ambiguous. Could be: {', '.join(element.__name__ for element in valid_elements)}:\n\n'{text}'")

    @classmethod
    def is_valid(self, text: str) -> bool:
        return False


class BlankLine(LexicalElement):
    def __str__(self) -> str:
        return ""

    @classmethod
    def is_valid(self, text: str) -> bool:
        return not text.strip()


class Comment(LexicalElement):
    def __init__(self, text: str) -> None:
        self.text = Str(text).slice.after_first(r"#").strip() if text.count("#") else text.strip()

    def __str__(self) -> str:
        return f"# {self.text}"

    @classmethod
    def is_valid(self, text: str) -> bool:
        return text.strip().startswith("#")


class Define(LexicalElement):
    def __init__(self, text: str) -> None:
        left, _, right = text.partition("=")
        value, _, comment = Str(right).strip().re.sub(r"\s+", " ").partition("#")

        self.key = left.strip()
        self.value = Str(value).strip()
        self.comment = None if not (clean_comment := comment.strip()) else Comment(clean_comment)
        self.commented = False

    def __str__(self) -> str:
        define = f"{'# ' if self.commented else ''}{self.key} = {self.value}"
        return define if self.comment is None else f"{define.ljust(69)} {self.comment}"

    @classmethod
    def is_valid(self, text: str) -> bool:
        return bool(Str(text.strip()).re.search(r"^[^#]+=[^#]+.*"))
