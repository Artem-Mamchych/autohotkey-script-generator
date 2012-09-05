import ahkutils as ahk
from ahkutils import Application

class AutoComplete(object):
    scriptBuilder = None
    user_branches = None
    user_remotes = None

    def insertMavenAliases(self):
        self.scriptBuilder.addAutoComplete("m dep", "mvn clean deploy -U -Dmaven.test.skip=true -DskipTests -Dshould.deploy.to.TEST=true")
        self.scriptBuilder.addAutoComplete("m cl", "mvn -o clean")
        self.scriptBuilder.addAutoComplete("m t", "mvn -o clean test")
        self.scriptBuilder.addAutoComplete("m tt", "mvn -o clean test -Dmaven.surefire.debug -Dsurefire.useFile=false -Dtest=")
        self.scriptBuilder.addAutoComplete("m i", "mvn -o clean install")
        self.scriptBuilder.addAutoComplete("m it", "mvn clean install -Dmaven.test.skip=true")
        self.scriptBuilder.addAutoComplete("m jt", "mvn -o clean jetty:run -Ddev.env=test")
        self.scriptBuilder.addAutoComplete("m js", "mvn -o clean jetty:run -Ddev.env=stage")
        self.scriptBuilder.addAutoComplete("m cv", "mvn -o cobertura:cobertura")
        self.scriptBuilder.addAutoComplete("m r", "mvn dependency:resolve dependency:resolve-plugins")
        self.scriptBuilder.addAutoCompleteForApp(shortcut="m dt", data={Application.WinConsole : "mvn dependency:tree > tree"})

        self.scriptBuilder.addAutoCompleteForApp(shortcut="ver", data={Application.Putty : "less pom.xml | grep description -B 6 -A 3"})
        self.scriptBuilder.addAutoCompleteForApp(shortcut="cls", data={Application.Putty : "clear"})

    def insertCommonGitAliases(self):
        self.scriptBuilder.addAutoComplete("g'", "git commit -a -m ''")
        self.scriptBuilder.addAutoComplete("gl", "git log --graph --abbrev-commit --date=relative")
        #TODO: ahk escape % | AutoHotkey's default escape character is accent/backtick (`)
        self.scriptBuilder.addAutoComplete("gll", "git log --graph --pretty=format':`%C(yellow)`%h`%C(red)`%d`%Creset `%s `%C(white) `%an, `%ar`%Creset'")
        self.scriptBuilder.addAutoComplete("g1", "git log -p HEAD~..HEAD")
        self.scriptBuilder.addAutoComplete("gchk", "git fsck --full --strict --unreachable")
        self.scriptBuilder.addAutoComplete("git cp", "git cherry-pick")
        self.scriptBuilder.addAutoComplete("git fix", "git commit --amend -C HEAD") #git fix FILE1 FILE2;
        self.scriptBuilder.addAutoComplete("git ren", "git branch -m old new")
        self.scriptBuilder.addAutoComplete("git lastcgh", "git rev-list -n 1 HEAD -- [file_path]") #shows hash of last change of file
        self.scriptBuilder.addAutoComplete("git unrm", "git checkout [deleting_commit]^ -- [file_path]")
        self.scriptBuilder.addAutoComplete("git deleted", "git log --diff-filter=D --summary") #get all the commits which have deleted files 
        self.addGitAliasesSpecificForUserBranches()

    def addGitAliasesSpecificForUserBranches(self):
        if not self.user_remotes:
            self.user_remotes='origin'
        if not self.user_branches:
            self.user_branches = list()
        if 'master' not in self.user_branches:
            self.user_branches.append('master')

        for branch in self.user_branches:
            self.scriptBuilder.addAutoCompleteSmart("git checkout %s" % branch)
            self.scriptBuilder.addAutoCompleteSmart("git rebase %s" % branch)
        for remote in self.user_remotes:
            self.scriptBuilder.addAutoCompleteSmart("git remote add %s url" % remote)
            self.scriptBuilder.addAutoCompleteSmart("git fetch %s" % remote)
            for branch in self.user_branches:
                self.scriptBuilder.addAutoCompleteSmart("git push --progress %s %s:%s" % (remote, branch, branch))
                self.scriptBuilder.addAutoCompleteSmart("git push --progress %s %s:%s --force " % (remote, branch, branch))

    def insertLinuxShellAliases(self):
        self.scriptBuilder.addAutoComplete("diskfree", "du -s ./* | sort -nr| cut -f 2-|xargs -i du -sh {}")

    def insertCurrentDate_Time(self):
        self.scriptBuilder.addAutoCompleteTime("1date", "yyyy-MM-dd")
        self.scriptBuilder.addAutoCompleteTime("1time", "hh:mm:sstt")

    def __init__(self, builder, user_branches=None, user_remotes=None):
        if isinstance(builder, ahk.ScriptBuilder):
            self.scriptBuilder = builder
        else:
            ahk.error("Can't create Menu instance! ScriptBuilder is null!")
        self.user_branches = user_branches
        self.user_remotes = user_remotes

class CommonScripts(object):
    scriptBuilder = None

    def __init__(self, builder):
        if isinstance(builder, ahk.ScriptBuilder):
            self.scriptBuilder = builder
        else:
            ahk.error("Can't create Menu instance! ScriptBuilder is null!")

    def invertMouseScrollWheel(self):
        print("Mouse wheel scrolling is inverted! (MacOs style)")
        self.scriptBuilder.bindKey("WheelUp", "Send {WheelDown}")
        self.scriptBuilder.bindKey("WheelDown", "Send {WheelUp}")

# Google text from any app
# from http://superuser.com/questions/7271/most-useful-autohotkey-scripts/165220#165220
    def googleTextFromAnyApp(self, key):
        self.scriptBuilder.bindKey(key, """
MyClip := ClipboardAll
Clipboard = ; empty the clipboard
Send, ^c
ClipWait, 2
if ErrorLevel ; ClipWait timed out.
{
    return
}
if RegExMatch(Clipboard, "^(https?://|www\.)[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(/\S*)?$")
{
    Run % Clipboard
}
else
{
; Modify some characters that screw up the URL
; RFC 3986 section 2.2 Reserved Characters (January 2005): !*'();:@&=+$,/?#[]
    StringReplace, Clipboard, Clipboard, `r`n, %A_Space%, All
    StringReplace, Clipboard, Clipboard, #, `%23, All
    StringReplace, Clipboard, Clipboard, &, `%26, All
    StringReplace, Clipboard, Clipboard, +, `%2b, All
    StringReplace, Clipboard, Clipboard, ", `%22, All
    Run % "http://www.google.com/#hl=en&q=" . clipboard ; uriEncode(clipboard)
}
Clipboard := MyClip
""")

    def googleTranslateSelectedText(self, key):
        self.scriptBuilder.bindKey(key, """
MyClip := ClipboardAll
Clipboard = ; empty the clipboard
Send, ^c
ClipWait, 2
if ErrorLevel ; ClipWait timed out.
{
    return
}
StringReplace, Clipboard, Clipboard, `%, `%25, All ; has to come first
StringReplace, Clipboard, Clipboard, `r`n, `%0A, All
Run % "http://translate.google.com/#auto|uk|" . clipboard ; uriEncode(clipboard)
Clipboard := MyClip
""")

#It requires installing of additional software.
#See: http://tech.xster.net/tips/quake-style-drop-down-terminal-for-windows/
    def addQuakeStyleShell(self):
        print("Quake style shell support based on Console2 is added. Hotkey is: [Ctrl]+[`]")
        self.scriptBuilder.key_bindings.append(ahk.includeFile("includes/QuakeTerminal.ahk"))

    def htmlEditCommons(self):
#        self.scriptBuilder.bindKey("^sc030", "Send, ^{sc02E}<b>^{sc02F}</b>", ret=False) #Wrap text example
        self.scriptBuilder.addAutoComplete("$val", "$('#').val();")
        self.scriptBuilder.addAutoComplete("$html", "$('#').html();")
        self.scriptBuilder.addAutoComplete("$ex", "$('#').length;")
        self.scriptBuilder.addAutoComplete("$clk", "$('#form-submit:first').trigger('click');")
        self.scriptBuilder.addAutoComplete("$chk", "$('#').attr('checked', true);")
        self.scriptBuilder.addAutoComplete("$dd", "$('# option:last').attr('selected', 'selected');")