import ahkutils as ahk

class AutoComplete(object):
    scriptBuilder = None
    user_branches = None
    user_remotes = None

    def insertCommonGitAliases(self):
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
