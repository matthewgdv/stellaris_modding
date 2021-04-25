from __future__ import annotations

from subtypes import Dict, Str

from .element import LexicalElement


class DefinesParser:
    def __init__(self, text: str) -> None:
        self.text = text

    def parse(self) -> dict[str, list[LexicalElement]]:
        self.chars = [char for char in self.text]
        parse_result: Dict[str, list[LexicalElement]] = Dict()

        while "".join(self.chars).strip():
            key = self.next_key()
            section = self.next_section()
            parse_result[key] = self.parse_section(section)

        return parse_result

    def next_key(self) -> str:
        key = ""
        while True:
            if (char := self.chars.pop(0)) == "=":
                return key.strip()
            else:
                key += char

    def next_section(self) -> str:
        section = ""
        depth = 0

        while True:
            section += (char := self.chars.pop(0))

            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if not depth:
                    return section.strip()

    def parse_section(self, text: str) -> list[LexicalElement]:
        if not text.startswith("{") and text.endswith("}"):
            raise ValueError(f"Malformed pattern. Must be enclosed in braces:\n\n{text}")

        section = Str(text[1:-1].strip())

        return [
            LexicalElement.from_text(match.group().strip())
            for match in section.re.findall(r"^[ \t]*#.*?$|^[^=\n]+=[^\n]+\{.+?}[^\n]*$|^[^=\n]+=[^\n{]+$|^\s*?$")
        ]
