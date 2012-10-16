#autohotkey utils
import os
from sets import Set
from utils import stringutils as su

allowed_chars = Set('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_- ')
import sys

#This enum contains 'ahk_class' names of applications
class Application:
    WinConsole = "ConsoleWindowClass"
    Putty = "PuTTY"
    GoogleChrome = "Chrome_WidgetWin_0"
    TortoiseGit = "#32770"
    FireFox = "MozillaWindowClass"
    UnrealCommander = "TxUNCOM"

def sendCopy():
    return "Send, ^{vk43} ; Ctrl+C"

def sendPaste():
    return "Send, ^{vk56} ; Ctrl+V"

#Some applications has poor i/o performance and this delay helps them to get all uncorrupted text data.
#Delay will be added only when input text is too long.
def setKeyDelay(text=""):
    return """
#IfWinActive ahk_class Console_2_Main
SetKeyDelay 1
#IfWinActive
#IfWinNotActive ahk_class Console_2_Main
SetKeyDelay 0
#IfWinActive"""

#Reads and returns content of file
def includeFile(path):
    if not os.path.exists(path):
        print("File " + path + " not exists!")
        sys.exit()

    lines = ""
    file = open(path)
    while 1:
        lines_list = file.readlines(100000)
        if not lines_list:
            break
        for line in lines_list:
            lines += line
    return lines

#Root object with base methods to build ahk script
class ScriptBuilder(object):
    ahk_file = None
    log_file = None
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

        #TODO add submenus
    def addAutoCompleteFromFile(self, filename):
        if not os.path.exists(filename) or not os.path.isfile(filename):
            print("Error! %s file are not exists!")
            return

        array = []
        for line in open(filename, "r"):
            array.append(line)
            command = su.trimComments(line)
            if command:
                if '==' in command:
                    keyAndCommand = command.split('==')
                    if len(keyAndCommand) != 2:
                        print("Error! failed to parse; " + command)
                        continue
                    status = self.addAutoComplete(keyAndCommand[0], keyAndCommand[1])
                else:
                    status = self.addAutoCompleteSmart(command)

    def addAutoCompleteSmart(self, text, ret=True, delay=True):
        name = abbreviate(text)
        if name not in self.abbreviations:
            self.abbreviations.append(name)
            self.addAutoComplete(name, text, ret=True, delay=delay)
            return "%s%s" % (su.defaultCommentStartSequence, name)
        else:
            print("FATAL! " + text + "\tAutoCompleteSmart WAS NOT ADDED")
            return "%s[%s] sequence are already used!" % (su.defaultCommentStartSequence, name)

    #This autocomplete sequence will be available only for selected applications
    def addAutoCompleteForApp(self, *args, **data):
        shortcut = data.get("shortcut")
        data = data.get("data")
        if shortcut and data:
            self.key_bindings.append("\n::" + shortcut + "::")
            for application, text in data.viewitems():
                print 'Key is:', application
                print 'Value is:', text
                self.key_bindings.append('if WinActive("ahk_class %s") {' % application)
                self.addAutoComplete(shortcut, text, ret=False, delay=False, bindHotKey=False)
                self.key_bindings.append('}')
            self.key_bindings.append("Return")
        return shortcut

    #To use autocomplete - type 'shortcut' text and press [Tab]
    #If called directly - this autocomplete sequence will be available for ALL applications
    def addAutoComplete(self, shortcut, text, ret=True, delay=True, bindHotKey=True):
        if bindHotKey:
            self.key_bindings.append("\n::" + shortcut + "::")
        if delay:
            self.key_bindings.append(setKeyDelay(text))
#        else:
#            self.key_bindings.append(setKeyDelay())
        self.key_bindings.append("SendRaw " + text)
        self.logMessage(shortcut + "\tfor '" + text + "'\tAutoComplete was added!")
        if ret:
            self.key_bindings.append("Return")
        return shortcut

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
        self.key_bindings.append(setKeyDelay(text))
        self.key_bindings.append("SendRaw "+ text)
        if pressEnter:
            self.key_bindings.append("Send {enter}")
        self.key_bindings.append("return")

    def hotKeyWrapSelectedText(self, key, textLeft, textRight, pressEnter=False):
#        print("Adding WrapSelectedText hotKey on Win+%s button" % key)
#        self.bindKey("#" + key, 'Send, ^{sc02E}%s^{sc02F}%s' % (textLeft, textRight), ret=False)
        self.key_bindings.append("\n#%s::" % key)
        self.key_bindings.append("""
ClipSaved := ClipboardAll
Clipboard =
Send ^x
ClipWait 1
SendInput %s
Send ^v
SendInput %s
Clipboard := ClipSaved
ClipSaved =
Return
""" % (textLeft, textRight))

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
        if self.log_file:
            self.log_file.close()
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
        self.handlers.append(setKeyDelay(text))
        self.handlers.append("SendRaw "+ text)
        if pressEnter:
            self.handlers.append("Send {enter}")
        self.handlers.append("return\n")

    #Writes text to file
    def write(self, mesg):
        if not self.ahk_file:
            self.ahk_file = open("script.ahk", 'w')
            self.ahk_file.write("#SingleInstance force")
            self.ahk_file.write("\n;This file was auto-generated by https://github.com/Artem-Mamchych/autohotkey-script-generator application")
            self.ahk_file.write("\n;DO NOT EDIT THIS FILE, changes will be overwritten the next time the script is run")
        self.ahk_file.write("\n" + str(mesg))

    #Writes text to log file
    def logMessage(self, mesg):
        if not self.log_file:
            self.log_file = open("autocomplete-hints.txt", 'w')
            self.log_file.write("This file was auto-generated. ;DO NOT EDIT THIS FILE, changes will be overwritten the next time the script is run")
            self.log_file.write("\nThis file includes shortcuts for all generated autocomplete aliases and text on which it will be replaced")
        self.log_file.write("\n" + str(mesg))

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
        error(exit=False, message="NamingError: ',' symbol can't be used as name! Invalid name is: %s" % text)

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
            error("Can't create Menu instance! ScriptBuilder is null!")

    #Overrides
    def pasteText(self, text, pressEnter=False):
        pass

    def pasteTextHandler(self, text, sendPaste=False, clipSave=False, beforeReturn=False):
        if clipSave:
            self.builder.handlers.append("clipboard = %ClipSaved%")
    #    handlers.append("ClipWait")
        self.builder.handlers.append('clipboard = ' + text)
    #    handlers.append("ClipWait")
    #    handlers.append("Sleep, 1")
        if sendPaste:
            self.builder.handlers.append(pasteTextCode())
        if beforeReturn:
            self.builder.handlers.append(beforeReturn)
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

    def addSiteBookmark(self, itemName):
        checkName(itemName)
        self.builder.write("Menu, %s, Add, %s, OpenInBrowserMenuHandler" % (self.name, itemName))

    @staticmethod
    def createPrintTextMenuFromFile(filename, builder, deleteOnClick=False):
        if not os.path.exists(filename) or not os.path.isfile(filename):
            print("Error! %s file are not exists!")
            return

        array = []
        menu = None
        for line in open(filename, "r"):
            array.append(line)
            command = su.trimComments(line)
            if command:
                if 'Hotkey=' in command:
                    print(command)
                    hotKey = command.replace('Hotkey=', '')
                    menu = Menu(hotKey, hotKey, builder)
                else:
                    print("line: ")
                    print(command)
                    menu.addPrintText(command, command, deleteOnClick) #label, text
        if menu:
            menu.assignMenuHotKey()

    #Use to type some text
    def addPrintText(self, itemName, text, deleteOnClick=False):
        itemName = itemName.replace(",", "")
        checkName(itemName)
#        return 'Menu "%s" binded on: %s' % (self.name, self.key)
        print("Adding PrintText %s" % text)
        handler = self.createHandlerId()
        self.builder.menu_tree.append("Menu, %s, Add, %s, %s" % (self.name, itemName, handler))
        self.builder.handlers.append(handler + ":")
        self.pasteTextHandler(text, sendPaste=True, clipSave=True, beforeReturn="Menu, %s, delete, %s" % (self.name, itemName))

    #Use to save to clipboard some text
    def addPasteText(self, itemName, text):
        checkName(itemName)
        print("Adding PasteText %s" % text)
        handler = self.createHandlerId()
        self.builder.menu_tree.append("Menu, %s, Add, %s, %s" % (self.name, itemName, handler))
        self.builder.handlers.append(handler + ":")
        self.pasteTextHandler(text, sendPaste=False, clipSave=False)

    #Returns unique handler name
    def createHandlerId(self):
        self.handlerId += 1
        return self.name + 'Handler' + str(self.handlerId)

#returns first letter of each word
#'-' and '=' symbols are skipped
def abbreviate(text):
    words = text.split(" ")
    name = ""
    for word in words:
        if word and len(word) >= 1:
            for char in word:
                if char == '-' or char == '=':
                    continue
                name += char
                break
    return name

def error(message):
    print("\nERROR OCCURRED DURING GENERATING SCRIPT. Error message:")
    print(message)
    if exit:
        sys.exit(1)

#Paste text from clipboard
def pasteTextCode():
    return """SendInput {Raw}%clipboard%"""