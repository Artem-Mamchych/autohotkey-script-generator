#Author: Artem Mamchych
import sys
import os.path
import ahkutils as ahk

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

    if os.path.exists("most_useful_autohotkey_scripts.py"):
        import most_useful_autohotkey_scripts as commons
        top_scripts = commons.CommonScripts(builder)
        if getCliArgument('--invert-wheel'):
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

def getCliArgument(name):
    if '=' not in name:
        if name in sys.argv:
            return True
        else:
            return False
    else:
        output = ""
        #Return list of param=values, [...,]
        for arg in sys.argv:
            if arg.startswith(name):
                if arg.replace(name,''):
                    output = arg.replace(name,'').split(',')
                break
        return output

if __name__ == "__main__":
    #List type (--branches=master,develop,experimental) command line arguments are fetched here
    user_branches = getCliArgument('--branches=')
    user_remotes = getCliArgument('--remotes=')
    menu_files = getCliArgument('--menufiles=')
    generate()