from __future__ import annotations

from typing import Optional

from subtypes import Dict
from miscutils import ReprMixin

from .element import Comment, LexicalElement, Define


class DefinesSection(ReprMixin):
    NEWLINE = "\n"
    TAB = "    "

    def __init__(self, name: str, lexical_elements: Optional[list[LexicalElement]]) -> None:
        self.name = name
        self.lexical_elements = lexical_elements if lexical_elements is not None else []
        self.defines: Dict[str, Define] = Dict(
            {element.key: element for element in lexical_elements if isinstance(element, Define)}
            if lexical_elements is not None else Dict()
        )

    def __str__(self) -> str:
        elements = "\n".join(f"{self.TAB}{element}" for element in self.lexical_elements)
        return f"{self.name} = {{{self.NEWLINE}{elements}{self.NEWLINE}}}"

    def difference(self, other: DefinesSection) -> set[str]:
        unequal: set[str] = set()

        for define in self.defines.values():
            if (other_define := other.defines.get(define.key)) is not None:
                if define.value != other_define.value:
                    unequal.add(define.key)

        return unequal

    def union(self, other: DefinesSection) -> set[str]:
        return set(self.defines) | set(other.defines)

    def comment(self) -> None:
        for element in self.lexical_elements:
            if isinstance(element, Define):
                element.commented = True

    def uncomment(self) -> None:
        for element in self.lexical_elements:
            if isinstance(element, Define):
                element.commented = False
