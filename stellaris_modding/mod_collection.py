from __future__ import annotations

from miscutils import ReprMixin
from subtypes import Dict

from .mod import Mod


class ModCollection(ReprMixin):
    def __init__(self) -> None:
        self.current: Dict[str, Mod] = Dict()
        self.outdated: Dict[str, Mod] = Dict()

    @property
    def deployed(self) -> Dict[str, Mod]:
        return self.current | self.outdated


class UserModCollection(ModCollection):
    def __init__(self) -> None:
        super().__init__()
        self.staging: Dict[str, Mod] = Dict()
