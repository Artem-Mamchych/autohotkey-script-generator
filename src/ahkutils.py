#autohotkey utils
import os
import sys
from utils.configfileparser import Parser
from utils.configfileparser import TOKEN
from utils import stringutils as su
application = dict() #This dict contains 'ahk_class' names of applications
ahk_classes_file = "ahk_classes.txt"
ahk_classes_file_loaded = None
includes_dir = os.path.join(sys.path[0], "includes")
config_dir_name = "config"
config_dir = os.path.join(sys.path[0], config_dir_name)

def getApp(key):
    key = key.replace('[', '').replace(']', '')
    if key.startswith("ahk_"):
        return key
    elif key.upper() in application:
        return 'ahk_class ' + application[key.upper()]
    else:
        error("Application alias '%s' is not defined in file: \n%s"
            "\nAdd it to file or use 'ahk_class AppClassName' syntax" % (key, ahk_classes_file_loaded))

def loadApplicationSettings(filename=os.path.join(sys.path[0], "config", ahk_classes_file)):
    global ahk_classes_file_loaded
    ahk_classes_file_loaded = filename
    for line in open(filename, "r"):
        if line and '=' in line:
            if len(line.split('=')) != 2:
                print("Error! failed to parse ahk_classes.txt line: " + line)
                continue
            (key, app) = line.split('=')
            application[key.upper()] = app.replace('\n', '')

class KeyModifier:
    Ctrl = "^"
    Alt = "~"
    Win = "#"

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
    if not os.path.isdir(path):
        path = os.path.join(includes_dir, path)
    if not os.path.exists(path):
        print("File " + path + " not exists!")
        sys.exit()
    print("File %s was inlined!" % os.path.basename(path))
    lines = ""
    file = open(path)
    while 1:
        lines_list = file.readlines(100000)
        if not lines_list:
            break
        for line in lines_list:
            lines += line
    return lines

def parseHotKey(text):
    if text.startswith("Ctrl+"):
        return text.replace("Ctrl+", KeyModifier.Ctrl)
    elif text.startswith("Alt+"):
        return text.replace("Alt+", KeyModifier.Alt)
    elif text.startswith("Win+"):
        return text.replace("Win+", KeyModifier.Win)
    else:
        return KeyModifier.Win + text

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
        loadApplicationSettings()

    def getFileInstance(self):
        return self.ahk_file

    def addHandler(self, text):
        self.handlers.append(text)

    def addAutoCompleteFromFile(self, filename):
        print("[Config] Parsing autocomplete config file: " + Parser.getShortFilePath(filename))
        if not os.path.exists(filename) or not os.path.isfile(filename):
            print("Error! %s file are not exists!")
            return
        stopParsing = False
        applicationChosen = None
        autoCompleteAppData = None
        for line in open(filename, "r"):
            command = su.trimComments(line)
            if command:
                if command.startswith('[') and command.endswith(']'): #Works only for selected application
                    if Parser.gotIgnoreToken(command, autoCompleteAppData, filename):
                        stopParsing = True
                    if applicationChosen and len(autoCompleteAppData) or stopParsing:
                        print("[addAutoCompleteForApp] writing %s entries" % len(autoCompleteAppData))
                        self.addAutoCompleteForApp(application=applicationChosen, data=autoCompleteAppData)
                        if stopParsing:
                            break
                    if command == TOKEN.END:
                        applicationChosen = None
                        continue

                    applicationChosen = getApp(command)
                    autoCompleteAppData = dict()
                    print("[addAutoCompleteForApp] Section for: " + applicationChosen)
                    continue
                if applicationChosen:
                    if '==' in command:
                        keyAndCommand = command.split('==')
                        if len(keyAndCommand) != 2:
                            print("Error! failed to parse; " + command)
                            continue
                        autoCompleteAppData[keyAndCommand[0]] = keyAndCommand[1]
                    else:
                        name = self.createTextAlias(command)
                        if name:
                            autoCompleteAppData[name] = command
                elif '==' in command: #Works in all applications
                    keyAndCommand = command.split('==')
                    if len(keyAndCommand) != 2:
                        print("Error! failed to parse; " + command)
                        continue
                    status = self.addAutoComplete(keyAndCommand[0], keyAndCommand[1])
                else:
                    status = self.addAutoCompleteSmart(command)

    def createTextAlias(self, text):
        name = abbreviate(text)
        if name not in self.abbreviations:
            self.abbreviations.append(name)
            return name
        return None

    def addAutoCompleteSmart(self, text, ret=True, delay=True):
        name = self.createTextAlias(text)
        if name:
            self.addAutoComplete(name, text, ret=True, delay=delay)
            return "%s%s" % (su.defaultCommentStartSequence, name)
        else:
            print("FATAL! " + text + "\tAutoCompleteSmart WAS NOT ADDED %s[%s] sequence are already used!"% (su.defaultCommentStartSequence, name))
            return "%s[%s] sequence are already used!" % (su.defaultCommentStartSequence, name)

    #This autocomplete sequence will be available only for selected applications
    def addAutoCompleteForApp(self, *args, **data):
        application = data.get("application")
        data = data.get("data")
        if application and data:
            self.key_bindings.append('\n#IfWinActive %s' % application)
            for shortcut, text in data.viewitems():
                self.key_bindings.append("::" + shortcut + "::")
                self.addAutoComplete(shortcut, text, ret=False, delay=False, bindHotKey=False)
                self.key_bindings.append("Return")
            self.key_bindings.append('#IfWinActive')
        return

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

    def addHotKeysFromFile(self, filename):
        print("[Config] Parsing hotkeys config file: " + Parser.getShortFilePath(filename))
        if not os.path.exists(filename) or not os.path.isfile(filename):
            print("Error! %s file are not exists!")
            return
        stopParsing = False
        addedActions = list()
        for line in open(filename, "r"):
            command = su.trimComments(line)
            if not command:
                continue
            if command == TOKEN.END:
                self.key_bindings.append("#IfWinActive")
            elif command.startswith('[') and command.endswith(']'):
                if Parser.gotIgnoreToken(command, addedActions, filename):
                    break
                self.key_bindings.append("\n#IfWinActive " + getApp(command))
            elif command.startswith(TOKEN.BIND):
                if len(command.split(' ', 3)) != 4:
                    print("Error! failed to parse line: " + command)
                    continue
                (bind_token, key, action, data) = command.split(' ', 3)
                self.setHotKeyAction(key, action, data)
                addedActions.append(action)
            else:
                print("[addHotKeysFromFile] Error: Failed to parse string: " + command)

    def setHotKeyAction(self, key, action, data):
        if action == 'print':
            self.hotKeyPrintText(key, data, pressEnter=False, useKeyDelay=False)
        elif action =='paste': #TODO will be implemented later, adding stub now
            self.hotKeyPrintText(key, data, pressEnter=False, useKeyDelay=False)
        elif action =='wrapText':
#            output = data.replace('[SELECTION]', action) #TODO create new implementation with unlimited usages of [SELECTION]
            if len(data.split('[SELECTION]')) != 2:
                print("Split [SELECTION] length !=2 when parsing line:" + data)
                return
            (textLeft, textRight) = data.split('[SELECTION]')
            self.hotKeyWrapSelectedText(key, textLeft, textRight, pressEnter=False)
        elif action == 'INCLUDE_FILE':
            if not key == 'DEFINED_IN_FILE':
                self.key_bindings.append("\n%s::" % parseHotKey(key))
            self.key_bindings.append(includeFile(data))
        elif action == 'AHK_CODE':
            error("Not implemented!" + action)

    def hotKeyPrintText(self, key, text, pressEnter=False, useKeyDelay=True):
        #TODO check text for empty srt
#        print("Adding PrintText hotKey on Win+%s button" % key)
        self.key_bindings.append("\n%s::" % parseHotKey(key))
        if useKeyDelay:
            self.key_bindings.append(setKeyDelay(text))
        self.key_bindings.append("SendRaw "+ text)
        if pressEnter:
            self.key_bindings.append("Send {enter}")
        self.key_bindings.append("return")

    def hotKeyWrapSelectedText(self, key, textLeft, textRight, pressEnter=False):
#        print("Adding WrapSelectedText hotKey on Win+%s button" % key)
#        self.bindKey("#" + key, 'Send, ^{sc02E}%s^{sc02F}%s' % (textLeft, textRight), ret=False)
        self.key_bindings.append("\n%s::" % parseHotKey(key))
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
            self.log_file = open(os.path.join(sys.path[0], "autocomplete-hints.txt"), 'w')
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
        self.builder.menu_key_bindings.append("%s::Menu, %s, Show ; i.e. press the Win-%s hotkey to show the menu.\n" % (parseHotKey(self.key), self.name, self.key))

    def addMenuSeparator(self):
        self.builder.menu_tree.append("Menu, %s, Add" % self.name)

    def __str__(self):
        return 'Menu "%s" binded on: %s' % (self.name, self.key)

    def addSiteBookmark(self, itemName):
        checkName(itemName)
        self.builder.write("Menu, %s, Add, %s, OpenInBrowserMenuHandler" % (self.name, itemName))

    @staticmethod
    def createPrintTextMenuFromFile(filename, builder, deleteOnClick=False): #TODO add submenus support
        print("[Config] Parsing menu config file: " + Parser.getShortFilePath(filename))
        if not os.path.exists(filename) or not os.path.isfile(filename):
            print("Error! %s file are not exists!")
            return

        array = []
        menu = None
        for line in open(filename, "r"):
            array.append(line)
            command = su.trimComments(line)
            if command:
                if TOKEN.HOTKEY in command:
                    print(command)
                    hotKey = command.replace(TOKEN.HOTKEY, '')
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
        beforeReturn = ""
        if deleteOnClick:
            beforeReturn="Menu, %s, delete, %s" % (self.name, itemName)
        self.pasteTextHandler(text, sendPaste=True, clipSave=True, beforeReturn=beforeReturn)

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