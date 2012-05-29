#Author: Artem Mamchych
import sys
import os.path
import ahkutils as ahk

description='main automation script for easy generating autohotkey menus and more'
version = 0.3

def generate():
    print("Generating AHK Script...")

    builder = ahk.ScriptBuilder()
    generateGitShortcutsMenu(builder)

    if os.path.exists("most_useful_autohotkey_scripts.py"):
        import most_useful_autohotkey_scripts as commons
        top_scripts = commons.CommonScripts(builder)
        if len(sys.argv) >= 2 and sys.argv[1] == '--invert-wheel':
            top_scripts.invertMouseScrollWheel()
        top_scripts.googleTextFromAnyApp('#w')
        top_scripts.googleTranslateSelectedText('#t')

        autocompl = commons.AutoComplete(builder)
        autocompl.insertCurrentDate_Time()
        autocompl.insertCommonGitAliases()
        autocompl.insertMavenAliases()

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

if __name__ == "__main__":
    generate()