import ahkutils as ahk

class AutoComplete(object):
    scriptBuilder = None

    def __init__(self, builder):
        if isinstance(builder, ahk.ScriptBuilder):
            self.scriptBuilder = builder
        else:
            raise "Can't create Menu instance! ScriptBuilder is null!"

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
        self.scriptBuilder.addAutoComplete("m dt", "mvn dependency:tree > tree")

        self.scriptBuilder.ifApplication_AutoComplete("ConsoleWindowClass")
        self.scriptBuilder.addAutoComplete("ver", "less pom.xml | grep <version>")
        self.scriptBuilder.ifApplication_AutoComplete("PuTTY")
        self.scriptBuilder.addAutoComplete("ver", "less pom.xml | grep <version>")
        self.scriptBuilder.endIfApplication_AutoComplete()

    def insertCommonGitAliases(self):
        self.scriptBuilder.addAutoComplete("git st", "git status")
        self.scriptBuilder.addAutoComplete("git co", "git checkout ")
        self.scriptBuilder.addAutoComplete("git ma", "git checkout master")
        self.scriptBuilder.addAutoComplete("git st", "git checkout 12.06.5")
        self.scriptBuilder.addAutoComplete("git fe", "git fetch --all")
        self.scriptBuilder.addAutoComplete("git ci", "git commit ")
        self.scriptBuilder.addAutoComplete("git br", "git branch ")
        self.scriptBuilder.addAutoComplete("git rs", "git reset --hard HEAD")
        self.scriptBuilder.addAutoComplete("git ad", "git add --interactive") #provides a menu for adding, updating, reverting, and more

        self.scriptBuilder.addAutoComplete("git cp", "git cherry-pick ")
        self.scriptBuilder.addAutoComplete("git fix", "git commit --amend -C HEAD") #git fix FILE1 FILE2;
        self.scriptBuilder.addAutoComplete("git rb", "git rebase ")
        self.scriptBuilder.addAutoComplete("git rbc", "git rebase --continue")
        self.scriptBuilder.addAutoComplete("git rbs", "git rebase --skip")
        self.scriptBuilder.addAutoComplete("git un", "git git reset --soft HEAD~1")
        self.scriptBuilder.addAutoComplete("git ren", "git branch -m old new")
        self.scriptBuilder.addAutoComplete("git l", "git log --graph --abbrev-commit --date=relative")
        self.scriptBuilder.addAutoComplete("git dif", "git log -p")

        self.scriptBuilder.addAutoComplete("git pop", "git stash pop")

    def insertCurrentDate_Time(self):
        self.scriptBuilder.addAutoCompleteTime("1date", "yyyy-MM-dd")
        self.scriptBuilder.addAutoCompleteTime("1time", "hh:mm:sstt")

class CommonScripts(object):
    scriptBuilder = None

    def __init__(self, builder):
        if isinstance(builder, ahk.ScriptBuilder):
            self.scriptBuilder = builder
        else:
            raise "Can't create Menu instance! ScriptBuilder is null!"

    def invertMouseScrollWheel(self):
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

    def htmlEditCommons(self):
#        self.scriptBuilder.bindKey("^sc030", "Send, ^{sc02E}<b>^{sc02F}</b>", ret=False) #Wrap text example
        self.scriptBuilder.addAutoComplete("$val", "$('#').val();")
        self.scriptBuilder.addAutoComplete("$html", "$('#').html();")
        self.scriptBuilder.addAutoComplete("$ex", "$('#').length;")
        self.scriptBuilder.addAutoComplete("$clk", "$('#form-submit:first').trigger('click');")
        self.scriptBuilder.addAutoComplete("$chk", "$('#').attr('checked', true);")
        self.scriptBuilder.addAutoComplete("$dd", "$('# option:last').attr('selected', 'selected');")