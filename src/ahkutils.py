#autohotkey utils

def sendCopy():
    return "Send, ^{vk43} ; Ctrl+C"

def sendPaste():
    return "Send, ^{vk56} ; Ctrl+V"

#Root object with base methods to build ahk script
class ScriptBuilder(object):
    ahk_file = None
    menu_tree = None
    handlers = None
    menu_key_bindings = None
    key_bindings = None
    abbreviations = None

    def __init__(self, scriptName=None):
        self.menu_tree = list()
        self.handlers = list()
        self.menu_key_bindings = list()
        self.key_bindings = list()
        self.abbreviations = list()

    def getFileInstance(self):
        return self.ahk_file

    def addHandler(self, text):
        self.handlers.append(text)

    def ifApplication_AutoComplete(self, app):
        self.key_bindings.append("#IfWinActive ahk_class " + app)

    def endIfApplication_AutoComplete(self):
        self.key_bindings.append("#IfWinActive")

    def addAutoCompleteSmart(self, text, ret=True):
        name = abbreviate(text)
        if name not in self.abbreviations:
            self.abbreviations.append(name)
            print(name + " for " + text + "\tAutoCompleteSmart was added!")
            self.addAutoComplete(name, text)
        else:
            print("FATAL! " + text + "\tAutoCompleteSmart was not added")

    #To use autocomplete - type 'shortcut' text and press [Tab]
    def addAutoComplete(self, shortcut, text, ret=True):
        self.key_bindings.append("\n::" + shortcut + "::\nSendInput " + text)
        if ret:
            self.key_bindings.append("Return")

    def addAutoCompleteTime(self, shortcut, timeFormat, ret=True):
        self.key_bindings.append("\n::" + shortcut + "::\nFormatTime, T, %A_Now%, " + timeFormat + "\nSendInput %T%")
        if ret:
            self.key_bindings.append("Return")

    def bindKey(self, key, text, ret=True):
        self.key_bindings.append("\n" + key + ":: " + text)
        if ret:
            self.key_bindings.append("Return")

    def hotKeyPrintText(self, key, text, pressEnter=False):
        #TODO check text for empty srt
#        print("Adding PrintText hotKey on Win+%s button" % key)
        self.key_bindings.append("\n#%s::" % key)
        self.key_bindings.append("SetKeyDelay 0")
        self.key_bindings.append("SendRaw "+ text)
        if pressEnter:
            self.key_bindings.append("Send {enter}")
        self.key_bindings.append("return")

    def generateScript(self):
        print("Writing script file...")
        self.addCommonHandlers()
        self.enablePasteInWindowsPrompt()

        for text in self.menu_tree: #1. Write menu structure declarations:
            self.write(text)
        for text in self.handlers: #2. Write popup-menu handlers
            self.write(text)
        for text in self.key_bindings: #3. Write open popup-menu key bindings
            self.write(text)
        for text in self.menu_key_bindings: #4. Write key bindings
            self.write(text)
        self.ahk_file.close()
        print("DONE")

    #Uses system clipboard
    def pasteText(self, text, pressEnter=False): #Menu should use own overrided method
        self.write("ClipSaved = %ClipboardAll%")
        self.write('clipboard = ' + text)
#        self.write("ClipWait")
        self.write(sendPaste())
        self.write("clipboard = %ClipSaved%")
        self.write("return\n")

    #Simulates text typing
    #TODO printTextHandler has issue with losing focus of input, so it is not suitable for popup menus
    def printTextHandler(self, text, pressEnter=False):
        self.handlers.append("SetKeyDelay 0")
        self.handlers.append("SendRaw "+ text)
        if pressEnter:
            self.handlers.append("Send {enter}")
        self.handlers.append("return\n")

    #Writes text to file
    def write(self, mesg):
        if not self.ahk_file:
            self.ahk_file = open("script.ahk", 'w')
            self.ahk_file.write("#SingleInstance force")
        self.ahk_file.write("\n" + str(mesg))

    def addCommonHandlers(self):
        self.addHandler("""
OpenInBrowserMenuHandler:
Run %A_ThisMenuItem%
return""")

    #Enable Ctrl+V for Pasting in the Windows Command Prompt
    def enablePasteInWindowsPrompt(self):
        self.key_bindings.append("""
#IfWinActive ahk_class ConsoleWindowClass
^V::
SendInput {Raw}%clipboard%
return
#IfWinActive
""")

def checkName(text):
    if "," in text:
        raise "NamingError: ',' symbol can't be used as name! Invalid name is: %s" % text

class Menu(object):
    name = None
    key = None
    builder = None

    def __init__(self, name, key, scriptBuilder):
        self.name = name
        self.key = key
        self.handlerId = 0
        if isinstance(scriptBuilder, ScriptBuilder):
            self.builder = scriptBuilder
        else:
            raise "Can't create Menu instance! ScriptBuilder is null!"

    #Overrides
    def pasteText(self, text, pressEnter=False):
        pass

    def pasteTextHandler(self, text, sendPaste=False, clipSave=False):
        if clipSave:
            self.builder.handlers.append("clipboard = %ClipSaved%")
    #    handlers.append("ClipWait")
        self.builder.handlers.append('clipboard = ' + text)
    #    handlers.append("ClipWait")
    #    handlers.append("Sleep, 1")
        if sendPaste:
            self.builder.handlers.append(pasteTextCode())
        if clipSave:
            self.builder.handlers.append("clipboard = %ClipSaved%")
    #    handlers.append("ClipWait")
    #    handlers.append("Sleep, 1")
        self.builder.handlers.append("return\n")

    #Overrides
    def printTextHandler(self, text, pressEnter=False):
        pass

    def assignMenuHotKey(self):
        self.builder.menu_key_bindings.append("#%s::Menu, %s, Show ; i.e. press the Win-%s hotkey to show the menu.\n" % (self.key, self.name, self.key))

    def addMenuSeparator(self):
        self.builder.menu_tree.append("Menu, %s, Add" % self.name)

    def __str__(self):
        return 'Menu "%s" binded on: %s' % (self.name, self.key)

    def addSiteBookmark(self, menuName, itemName): #TODO drop menuName
        checkName(itemName)
        self.builder.write("Menu, %s, Add, %s, OpenInBrowserMenuHandler" % (self.name, itemName))

    #Used to type some text
    def addPrintText(self, itemName, text):
        checkName(itemName)
#        return 'Menu "%s" binded on: %s' % (self.name, self.key)
        print("Adding PrintText %s" % text)
        handler = self.createHandlerId()
        self.builder.menu_tree.append("Menu, %s, Add, %s, %s" % (self.name, itemName, handler))
        self.builder.handlers.append(handler + ":")
        self.pasteTextHandler(text, sendPaste=True, clipSave=True)

    #Returns unique handler name
    def createHandlerId(self):
        self.handlerId += 1
        return self.name + 'Handler' + str(self.handlerId)

def abbreviate(text): #returns first letter of each word
    lines = text.split(" ")
    name = ""
    for i in lines:
        if i and len(i) >= 1:
            name += i[0]
    return name

#Paste text from clipboard
def pasteTextCode():
    return """#IfWinActive ahk_class ConsoleWindowClass
SendInput {Raw}%clipboard%
#IfWinActive
#IfWinNotActive ahk_class ConsoleWindowClass
Send ^{vk56}
#IfWinNotActive"""