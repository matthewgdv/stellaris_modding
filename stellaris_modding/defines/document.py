from __future__ import annotations

from miscutils import ReprMixin
from pathmagic import File
from subtypes import Dict

from .element import Comment, LexicalElement
from .section import DefinesSection
from .parser import DefinesParser

from .. import config


class DefinesDocument(ReprMixin):
    def __init__(self, parse_result: dict[str, list[LexicalElement]]) -> None:
        self.parse_result = parse_result

        self.sections: Dict[str, DefinesSection] = Dict({
            (name := "NCamera"): DefinesSection(name=name, lexical_elements=parse_result.get(name)),
            (name := "NGraphics"): DefinesSection(name=name, lexical_elements=parse_result.get(name)),
            (name := "NInterface"): DefinesSection(name=name, lexical_elements=parse_result.get(name)),
            (name := "NGameplay"): DefinesSection(name=name, lexical_elements=parse_result.get(name)),
            (name := "NSpecies"): DefinesSection(name=name, lexical_elements=parse_result.get(name)),
            (name := "NShip"): DefinesSection(name=name, lexical_elements=parse_result.get(name)),
            (name := "NCombat"): DefinesSection(name=name, lexical_elements=parse_result.get(name)),
            (name := "NPop"): DefinesSection(name=name, lexical_elements=parse_result.get(name)),
            (name := "NArmy"): DefinesSection(name=name, lexical_elements=parse_result.get(name)),
            (name := "NEconomy"): DefinesSection(name=name, lexical_elements=parse_result.get(name)),
            (name := "NAI"): DefinesSection(name=name, lexical_elements=parse_result.get(name))
        })

    def __str__(self) -> str:
        return "\n\n".join(str(section) for section in self.sections.values())

    def sync_against_reference(self) -> DefinesDocument:
        document = type(self).from_defines_file(config.STELLARIS_DIR.d.common.d.defines.f._00_defines)
        document.comment()

        difference = document.difference(self)

        for section_name, keys in difference.items():
            defines_section = document.sections[section_name]

            for key in keys:
                define = self.sections[section_name].defines[key]
                define.comment = Comment(text="="*150)

                index = defines_section.lexical_elements.index(defines_section.defines[key])
                defines_section.lexical_elements.insert(index + 1, define)

        return document

    def difference(self, other: DefinesDocument) -> dict[str, set[str]]:
        return {
            section_name: self.sections[section_name].difference(other.sections[section_name])
            for section_name in self.sections
        }

    def comment(self) -> None:
        for section in self.sections.values():
            section.comment()

    def uncomment(self) -> None:
        for section in self.sections.values():
            section.uncomment()

    @classmethod
    def from_defines_file(cls, defines_file: File) -> DefinesDocument:
        parse_result = DefinesParser(defines_file.content).parse()
        return cls(parse_result=parse_result)
