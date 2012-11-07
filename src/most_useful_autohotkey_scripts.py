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
            ahk.error("Can't create CustomAutoComplete instance! ScriptBuilder is null!")
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
