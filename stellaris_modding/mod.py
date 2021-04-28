from __future__ import annotations

import textwrap
from pathlib import Path

from miscutils import Version, ReprMixin
from pathmagic import File, Dir
from subtypes import Frame, Str, Process

from .defines.document import DefinesDocument
from . import config


class Mod(ReprMixin):
    def __init__(self, info: File) -> None:
        self.info = info
        self.name, self.tags, self.version, self.root = self.parse_attrs_from_modinfo()

    def __repr__(self) -> str:
        return f"""{type(self).__name__}(name={repr(self.name)}, tags={repr(self.tags)}, version={repr(self.version)}, root={repr(self.root)})"""

    def __enter__(self) -> Mod:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.write_attrs_to_modinfo()

    def parse_attrs_from_modinfo(self) -> tuple[str, set[str], Version, Dir]:
        content = Str(self.info.read())

        name = content.re.search(r'name="(.+?)"').group(1)
        tags = {tag.strip().strip('"') for tag in (content.re.search(r'tags=\{(.*?)}').group(1).split(", "))}
        version = Version.from_string(content.re.search(r'supported_version="((?:\d+|\*)\.(?:\d+|\*)\.?(?:\d+|\*)?)"').group(1), wildcard="*")

        try:
            raw_path = content.re.search(r'path="(.+?)"').group(1)
        except AttributeError:
            raise FileNotFoundError

        root = Dir(path if (path := Path(raw_path)).is_absolute() else self.info.parent.join_dir(path))

        return name, tags, version, root

    def write_attrs_to_modinfo(self):
        self.write_attrs_to_file(info=self.info, name=self.name, tags=self.tags, version=self.version,
                                 root=self.root.path.relative_to(self.info.parent) if self.info.parent > self.root else self.root)

    def deploy(self) -> Mod:
        info = config.USER_MOD_DIR.new_file(self.info.name)
        self.write_attrs_to_file(info=info, name=self.name, tags=self.tags, version=self.version, root=self.root)
        return type(self)(info=info)

    def undeploy(self) -> None:
        if self.info not in config.USER_MOD_DIR:
            raise FileNotFoundError(f"Cannot undeploy a mod that isn't already deployed to '{config.USER_MOD_DIR}'")

        if self.root < config.WORKSHOP_DIR:
            raise PermissionError(f"Cannot undeploy a mod that was installed using the steam workshop")

        self.info.delete()

    def diff_against(self, mod: Mod) -> None:
        for _, files in self.root.compare_tree(mod.root):
            for my_file, other_file in files:
                if my_file.extension == "txt":
                    Process([config.MELD_EXE, my_file, other_file], verbose=True).wait()

    def diff_against_reference(self) -> None:
        for dir_name in ("common", "events"):
            if dir_name in self.root.dirs:
                for _, files in self.root.dirs[dir_name].compare_tree(config.STELLARIS_DIR.dirs[dir_name]):
                    for my_file, other_file in files:
                        if my_file.extension == "txt":
                            Process([config.MELD_EXE, my_file, other_file], verbose=True).wait()

    def collisions_against(self, mod: Mod) -> list[tuple[File, File]]:
        return [
            (my_file, other_file)
            for _, files in self.root.compare_tree(mod.root)
            for my_file, other_file in files
            if my_file.extension == "txt"
        ]

    def sync_defines_to_reference(self) -> None:
        for defines_file in self.root.d.common.d.defines.files:
            defines_file.write(DefinesDocument.from_defines_file(defines_file).sync_against_reference())

    @staticmethod
    def write_attrs_to_file(info: File, name: str, tags: set[str], version: Version, root: Dir) -> None:
        clean_root = str(root).replace('\\', '/')

        info.write(textwrap.dedent(
            f'''\
            name="{name}"
            tags={{
                {'"balance"' if tags is None else ", ".join(f'"{tag}"' for tag in sorted(tags))}
            }}
            supported_version="{version}"
            path="{clean_root}"
            '''
        ))

    @classmethod
    def from_params(cls, name: str, tags: set[str], version: Version, root: Dir):
        info = config.USER_MOD_DIR.new_file(Str(name).case.snake())
        cls.write_attrs_to_file(info=info, name=name, tags=tags, version=version, root=root)

        return cls(info)
