#Author: Artem Mamchych
import sys
import os.path
import ahkutils as ahk
from utils.configfileparser import Parser

description='main automation script for easy generating autohotkey menus, hotkey bindings, text autocomplete and more'
version = 0.6
user_branches = list()
user_remotes = list()
menuItem_id = 0

def generate():
    print("Generating AHK Script...")

    builder = ahk.ScriptBuilder()
    for file in getFilesByMask(ahk.config_dir, "hotkeys", ".txt"):
        builder.addHotKeysFromFile(file)
    for file in getFilesByMask(ahk.config_dir, "autocomplete", ".txt"):
        builder.addAutoCompleteFromFile(file)
    for file in menu_files:
        ahk.Menu.createPrintTextMenuFromFile(os.path.join(ahk.config_dir_name, file), builder)

    if os.path.exists("most_useful_autohotkey_scripts.py"):
        import most_useful_autohotkey_scripts as commons
        top_scripts = commons.CommonScripts(builder)
        if Parser.getCliArgument('--invert-wheel'):
            top_scripts.invertMouseScrollWheel()

        autocompl = commons.AutoComplete(builder, user_branches, user_remotes)
        autocompl.insertCurrentDate_Time()
        autocompl.insertCommonGitAliases()

    if os.path.exists("application_specific_bindings.py"):
        import application_specific_bindings as asp
        asp.generate(builder)
    builder.generateScript()

def getFilesByMask(directory, prefix, extension):
    files = list()
    os.chdir(directory)
    for file in os.listdir("."):
        if file.endswith(extension) and prefix in file:
            files.append(os.path.join(ahk.config_dir, file))
    os.chdir(sys.path[0])
    return files

if __name__ == "__main__":
    #List type (--branches=master,develop,experimental) command line arguments are fetched here
    user_branches = Parser.getCliArgument('--branches=')
    user_remotes = Parser.getCliArgument('--remotes=')
    menu_files = Parser.getCliArgument('--menufiles=')
    generate()