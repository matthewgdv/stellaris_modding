from __future__ import annotations

from typing import Optional

from miscutils import Version, ReprMixin
from pathmagic import File
from subtypes import Str, Frame

from .mod import Mod
from .mod_collection import UserModCollection, ModCollection
from . import config

OptInt = Optional[int]


class ModManager(ReprMixin):
    ADDITIONAL_SEARCH_PATHS = [
        config.MOD_REPO_DIR
    ]

    def __init__(self, version: tuple[OptInt, OptInt, OptInt], author: str = "Mett"):
        self.version, self.author = Version(*version, wildcard="*"), author
        self.mods = UserModCollection()
        self.workshop_mods = ModCollection()

        self._parse_mods()

    def new_mod(self, name: str, tags: set[str] = None) -> Mod:
        processed_name = f"[{self.author}] {name}"
        self.mods.current.append(mod := Mod.from_params(name=processed_name, version=self.version,
                                                        tags=tags, root=config.USER_MOD_DIR.new_dir(Str(processed_name).case.snake())))
        return mod

    def diff_mods_against_reference(self) -> None:
        matches: list[tuple[File, File]] = []
        for mod in self.mods.current.values():
            mod.diff_against_reference()

    def diff_collisions_with_workshop_mods(self) -> None:
        for mod in self.mods.current.values():
            for workshop_mod in self.workshop_mods.current.values():
                mod.diff_against(workshop_mod)

    def collisions_with_workshop_mods(self) -> Frame:
        collisions: dict[tuple[Mod, Mod], list[tuple[File, File]]] = {}

        for mod in self.mods.current.values():
            for workshop_mod in self.workshop_mods.current.values():
                collisions[(mod, workshop_mod)] = mod.collisions_against(workshop_mod)

        data = [(my_mod.name, other_mod.name, str(my_file.path.relative_to(my_mod.root)), str(other_file.path.relative_to(other_mod.root)))
                for (my_mod, other_mod), matchfiles in collisions.items() for my_file, other_file in matchfiles]
        return Frame(data, columns=["my_mod", "workshop_mod", "my_file", "workshop_file"])

    def _parse_mods(self) -> None:
        for file in config.USER_MOD_DIR.files:
            if file.extension == "mod":
                try:
                    mod = Mod(info=file)
                except FileNotFoundError:
                    continue

                owner = self.workshop_mods if mod.root < config.WORKSHOP_DIR else self.mods
                collection = owner.current if mod.version >= self.version else owner.outdated
                collection[Str(mod.name).case.identifier()] = mod

        for dir in self.ADDITIONAL_SEARCH_PATHS:
            for file in dir.files:
                if file.extension == "mod" and file.stem != "descriptor":
                    mod = Mod(info=file)
                    self.mods.staging[Str(mod.name).case.identifier()] = mod
