from pathmagic import Dir, File

USER_MOD_DIR = Dir.from_home().join_dir(R"Documents\Paradox Interactive\Stellaris\mod")
STELLARIS_DIR = Dir(R"C:\Program Files (x86)\Steam\steamapps\common\Stellaris")
WORKSHOP_DIR = Dir(R"C:\Program Files (x86)\Steam\steamapps\workshop\content\281990")

MOD_REPO_DIR = File(__file__).parent[1].dirs["mods"]

MELD_EXE = R"C:\Users\matthewgdv\AppData\Local\Programs\Meld\Meld.exe"
