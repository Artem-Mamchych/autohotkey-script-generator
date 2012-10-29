#Author: Artem Mamchych
import sys
import os.path
import ahkutils as ahk

description='main automation script for easy generating autohotkey menus, hotkey bindings, text autocomplete and more'
version = 0.5
user_branches = list()
user_remotes = list()
menuItem_id = 0

def generate():
    print("Generating AHK Script...")

    builder = ahk.ScriptBuilder()
    generateGitShortcutsMenu(builder)

    builder.addAutoCompleteFromFile('config/autocomplete.txt')
    builder.addAutoCompleteFromFile('config/autocomplete-git.txt')
    if os.path.exists("most_useful_autohotkey_scripts.py"):
        import most_useful_autohotkey_scripts as commons
        top_scripts = commons.CommonScripts(builder)
        if getCliArgument('--invert-wheel'):
            top_scripts.invertMouseScrollWheel()
        if getCliArgument('--quake-shell'):
            top_scripts.addQuakeStyleShell()
#        top_scripts.googleTextFromAnyApp('#g')
        top_scripts.googleTranslateSelectedText('#t')

        autocompl = commons.AutoComplete(builder, user_branches, user_remotes)
        autocompl.insertCurrentDate_Time()
        autocompl.insertCommonGitAliases()

    if os.path.exists("application_specific_bindings.py"):
        import application_specific_bindings as asp
        asp.generate(builder)
    builder.generateScript()

def generateGitShortcutsMenu(builder):
    print("generatePrivatePartOfScript")
    git = ahk.Menu("Git", "g", builder)
    git.addPrintText("dependency:tree > tree", "mvn dependency:tree > tree")
    git.addPrintText("rebase", "git rebase master")
    git.addPrintText("status", "git status")
    git.addPrintText("cherry-pick", "git cherry-pick 5d3e1b6")
    git.addPrintText("stash save", "git stash save message")
    git.addPrintText("stash apply", "git stash apply")
    git.addPrintText("blame lines", "git blame -L 160,+10 Hello.java")
    git.addPrintText("push", "git push origin master")
    git.addPrintText("delete remote branch", "git push origin :br")
    git.addPrintText("delete local branch", "git branch -d br")
    git.addPrintText("uncommit", "git reset --soft HEAD~1")
    git.addPrintText("reset --hard", "git reset --hard HEAD")
    git.addPrintText("squash", "git merge --squash --progress artem/tag-ok")
    git.addPrintText("merge --theirs", "git merge upstream --theirs")
    git.addPrintText("fetch remote br", "git fetch origin [remote-branch]:[new-local-branch]")
    git.addPrintText("checkout remote br", "git checkout -b 12.04.0 origin/12.04.0")

    git.addPrintText("deploy.to.TEST/skipTests", "mvn -U clean deploy -Dmaven.test.skip=true -DskipTests -Dshould.deploy.to.TEST=true")
    git.addPrintText("deploy to mvn/skipTests", "mvn -U clean deploy -Dmaven.test.skip=true -DskipTests -Dshould.deploy.to.TEST=false")
    git.addPrintText("run tests/deploy to mvn", "mvn -U clean deploy -Dshould.deploy.to.TEST=false")
    git.assignMenuHotKey()

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