from __future__ import annotations

from typing import Optional

from miscutils import Version, ReprMixin
from pathmagic import File
from subtypes import Str, Frame, Process

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
        self.collisions: dict[tuple[Mod, Mod], list[tuple[File, File]]] = {}

        self._parse_mods()
        self._identify_collisions()

    def new_mod(self, name: str, tags: set[str] = None) -> Mod:
        processed_name = f"{self.author}'{'' if self.author.endswith('s') else 's'} {name}"
        self.mods.current.append(mod := Mod.from_params(name=processed_name, version=self.version,
                                                        tags=tags, root=config.USER_MOD_DIR.new_dir(Str(processed_name).case.snake())))
        return mod

    def diff_all_mods(self) -> None:
        matches: list[tuple[File, File]] = []
        for mod in self.mods.current.values():
            for dir_match, file_matches in mod.root.compare_tree(config.STELLARIS_DIR):
                for match in file_matches:
                    if match[0].extension == "txt":
                        matches.append(match)

        for override, original in matches:
            Process([config.MELD_EXE, override, original]).wait()

    def _parse_mods(self) -> None:
        for file in config.USER_MOD_DIR.files:
            if file.extension == "mod":
                try:
                    mod = Mod(info=file)
                except FileNotFoundError:
                    continue

                owner = self.workshop_mods if mod.root > config.WORKSHOP_DIR else self.mods
                collection = owner.current if mod.version >= self.version else owner.outdated
                collection[Str(mod.name).case.identifier()] = mod

        for dir in self.ADDITIONAL_SEARCH_PATHS:
            for file in dir.files:
                if file.extension == "mod":
                    mod = Mod(info=file)
                    self.mods.staging[Str(mod.name).case.identifier()] = mod

    def _identify_collisions(self) -> None:
        for mod in self.mods.current.values():
            for workshop_mod in self.workshop_mods.current.values():
                for dirs, files in mod.root.compare_tree(workshop_mod.root):
                    if collisions := list(files):
                        self.collisions.setdefault((mod, workshop_mod), []).extend(collisions)

    def list_collisions_with_workshop_mods(self) -> None:
        my_word, their_word = "mod", R"mod\workshop"
        data = [(my_mod.info.name, their_mod.info.name, Str(my_file).slice.after(my_word), Str(their_file).slice.after(their_word))
                for (my_mod, their_mod), matchfiles in self.collisions.items() for my_file, their_file in matchfiles]
        frame = Frame(data, columns=["My Mod", "Workshop Mod", "My Override", "Workshop Override"]).to_ascii()
        print(frame)

    def diff_collisions_with_workshop_mods(self) -> None:
        for pair in self.collisions.values():
            for mine, theirs in pair:
                Process([config.MELD_EXE, mine, theirs]).wait()
