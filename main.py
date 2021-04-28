from stellaris_modding.manager import ModManager


manager = ModManager(version=(3, 0, None))
# manager.diff_mods_against_reference()
# manager.collisions_with_workshop_mods()
# manager.diff_collisions_with_workshop_mods()

manager.workshop_mods.current.expanded_gestalts_forgotten_queens.root.start()
