#autohotkey utils
import codecs
import os
import sys
from utils.configfileparser import Parser
from utils.configfileparser import Validator
from utils.configfileparser import TOKEN
from utils import stringutils as su

includes_dir = os.path.join(sys.path[0], "includes")
config_dir_name = "config"
config_dir = os.path.join(sys.path[0], config_dir_name)
script_file_name="script.ahk"

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
        Parser.loadApplicationSettings()

    def getFileInstance(self):
        return self.ahk_file

    def addHandler(self, text):
        self.handlers.append(text)

    def addAutoCompleteFromFile(self, filename):
        print("[Config] Parsing autocomplete config file: " + Parser.getShortFilePath(filename))
        if not os.path.exists(filename) or not os.path.isfile(filename):
            print("Error! %s file are not exists!" % filename)
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

                    applicationChosen = Parser.getApp(command)
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
            print("Error! %s file are not exists!" % filename)
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
                self.key_bindings.append("\n#IfWinActive " + Parser.getApp(command))
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
        if action == TOKEN.HK_PRINT:
            self.hotKeyPrintText(key, data, pressEnter=False, useKeyDelay=False)
        elif action == TOKEN.HK_PASTE: #TODO will be implemented later, adding stub now
            self.hotKeyPrintText(key, data, pressEnter=False, useKeyDelay=False)
        elif action == TOKEN.HK_WRAP:
#            output = data.replace(TOKEN.SELECTED_TEXT, action) #TODO create new implementation with unlimited usages of [SELECTION]
            if len(data.split(TOKEN.SELECTED_TEXT)) != 2:
                print("Split %s length !=2 when parsing line: %s" % (TOKEN.SELECTED_TEXT ,data))
                return
            (textLeft, textRight) = data.split(TOKEN.SELECTED_TEXT)
            self.hotKeyWrapSelectedText(key, textLeft, textRight, pressEnter=False)
        elif action == TOKEN.HK_INCLUDE_FILE:
            if not key == TOKEN.HK_DEFINED_IN_FILE:
                self.key_bindings.append("\n%s::" % Parser.parseHotKey(key))
            self.key_bindings.append(includeFile(data))

    def hotKeyPrintText(self, key, text, pressEnter=False, useKeyDelay=True):
        Validator.notEmpty(text, "hotKeyPrintText on %s button" % Parser.parseHotKey(key))
        self.key_bindings.append("\n%s::" % Parser.parseHotKey(key))
        if useKeyDelay:
            self.key_bindings.append(setKeyDelay(text))
        self.key_bindings.append("SendRaw "+ text)
        if pressEnter:
            self.key_bindings.append("Send {enter}")
        self.key_bindings.append("return")

    def hotKeyWrapSelectedText(self, key, textLeft, textRight, pressEnter=False):
        Validator.notEmpty(textLeft, "hotKeyWrapSelectedText <textLeft> on %s button" % Parser.parseHotKey(key))
        Validator.notEmpty(textRight, "hotKeyWrapSelectedText <textRight> on %s button" % Parser.parseHotKey(key))
        self.key_bindings.append("\n%s::" % Parser.parseHotKey(key))
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
        print("Writing script file %s..." % script_file_name)
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
        Validator.notEmpty(text, "pasteText")
        self.write("ClipSaved = %ClipboardAll%")
        self.write('clipboard = ' + text)
#        self.write("ClipWait")
        self.write(sendPaste())
        self.write("clipboard = %ClipSaved%")
        self.write("return\n")

    #Simulates text typing
    #TODO printTextHandler has issue with losing focus of input, so it is not suitable for popup menus
    def printTextHandler(self, text, pressEnter=False):
        Validator.notEmpty(text, "printTextHandler")
        self.handlers.append(setKeyDelay(text))
        self.handlers.append("SendRaw "+ text)
        if pressEnter:
            self.handlers.append("Send {enter}")
        self.handlers.append("return\n")

    #Writes text to file
    def write(self, mesg):
        if not self.ahk_file:
            self.ahk_file = codecs.open(script_file_name, "w", "mbcs") #Windows only: Encode operand according to the ANSI codepage (CP_ACP)
            self.ahk_file.write("#SingleInstance force")
            self.ahk_file.write("\n;This file was auto-generated by https://github.com/Artem-Mamchych/autohotkey-script-generator application")
            self.ahk_file.write("\n;DO NOT EDIT THIS FILE, changes will be overwritten the next time the script is run")
        self.ahk_file.write("\n" + mesg)

    #Writes text to log file
    def logMessage(self, mesg):
        if not self.log_file:
            self.log_file = open(os.path.join(sys.path[0], "autocomplete-hints.txt"), 'w')
            self.log_file.write("This file was auto-generated. ;DO NOT EDIT THIS FILE, changes will be overwritten the next time the script is run")
            self.log_file.write("\nThis file includes shortcuts for all generated autocomplete aliases and text on which it will be replaced")
        self.log_file.write("\n" + mesg)

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
        error("[Menu.pasteText] NOT IMPLEMENTED!")

    def pasteTextHandler(self, text, sendPaste=False, clipSave=False, beforeReturn=False):
        Validator.notEmpty(text, "Menu.pasteTextHandler")
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
        error("[Menu.printTextHandler] NOT IMPLEMENTED!")

    def assignMenuHotKey(self):
        self.builder.menu_tree.append("return  ; End of menu tree definition section.")
        self.builder.menu_key_bindings.append("%s::Menu, %s, Show ; i.e. press the Win-%s hotkey to show the menu.\n" % (Parser.parseHotKey(self.key), self.name, self.key))

    def addMenuSeparator(self):
        self.builder.menu_tree.append("Menu, %s, Add" % self.name)

    def __str__(self):
        return 'Menu "%s" binded on: %s' % (self.name, self.key)

    def addSiteBookmark(self, itemName):
        Validator.checkName(itemName)
        self.builder.write("Menu, %s, Add, %s, OpenInBrowserMenuHandler" % (self.name, itemName))

    @staticmethod
    def createPrintTextMenuFromFile(filename, builder):
        print("[Config] Parsing menu config file: " + Parser.getShortFilePath(filename))
        if not os.path.exists(filename) or not os.path.isfile(filename):
            print("Error! %s file are not exists!" % filename)
            return

        menu = None
        deleteOnClick = False
        method = None
        import json
        data = json.loads(Parser.readFileAsString(filename))
        if not len(data['MenuItems']):
            error("Invalid JSON file [%s] MenuItems dictionary is empty or invalid!" % filename)

        if data['MenuSettings'] and data['MenuSettings']['Hotkey']:
            hotKey = data['MenuSettings']['Hotkey']
            menu = Menu(hotKey, hotKey, builder)
        else:
            error("Invalid JSON file [%s] MenuSettings.Hotkey value is not provided!" % filename)

        if data['MenuSettings']['deleteOnClick'] == 'true':
            deleteOnClick = True
        elif data['MenuSettings']['deleteOnClick'] == 'false':
            deleteOnClick = False
        else:
            error("Invalid JSON file [%s] MenuSettings.deleteOnClick value is not provided!")

        if data['MenuSettings']['mode'] == 'print':
            method = menu.addPrintText
        elif data['MenuSettings']['mode'] == 'clipboard':
            method = menu.addPasteText
        else:
            error("Invalid JSON file [%s] MenuSettings.mode value is not provided!")

        for key, subMenu in data['MenuItems'].iteritems():
            if key == 'MenuSettings':
                continue
            if isinstance(subMenu, dict):
                for itemName, itemValue in subMenu.iteritems():
                    method(itemName, itemValue, subMenuName=key, deleteOnClick=deleteOnClick)
                menu.attachSubMenu(hotKey, key, key)
            if isinstance(subMenu, list):
                for item in subMenu:
                    method(item, item, subMenuName=key, deleteOnClick=deleteOnClick)
                menu.attachSubMenu(hotKey, key, key)
        if menu:
            menu.assignMenuHotKey()

    def attachSubMenu(self, rootMenuName, subMenuName, subMenuObj):
        if subMenuName and subMenuObj:
            self.builder.menu_tree.append("Menu, %s, Add, %s, :%s" % (rootMenuName, subMenuName, subMenuObj))

    #Use to type some text
    def addPrintText(self, itemName, text, subMenuName=None, deleteOnClick=False):
        Validator.notEmpty(text, "addPrintText for itemName %s " % itemName)
        itemName = Parser.filterMenuItemName(itemName)
        print("[PrintText] %s" % text)
        handler = self.createHandlerId()
        if not subMenuName:
            subMenuName=self.name
        self.builder.menu_tree.append("Menu, %s, Add, %s, %s" % (subMenuName, itemName, handler))
        self.builder.handlers.append(handler + ":")
        beforeReturn = ""
        if deleteOnClick:
            beforeReturn="Menu, %s, delete, %s" % (subMenuName, itemName)
        self.pasteTextHandler(text, sendPaste=True, clipSave=True, beforeReturn=beforeReturn)

    #Use to save to clipboard some text
    def addPasteText(self, itemName, text, subMenuName=None, deleteOnClick=False):
        Validator.notEmpty(text, "addPasteText for itemName %s " % itemName)
        itemName = Parser.filterMenuItemName(itemName)
        print("[PasteText] %s" % text)
        handler = self.createHandlerId()
        if not subMenuName:
            subMenuName=self.name
        self.builder.menu_tree.append("Menu, %s, Add, %s, %s" % (subMenuName, itemName, handler))
        self.builder.handlers.append(handler + ":")
        self.pasteTextHandler(text, sendPaste=False, clipSave=False)

    #Returns unique handler name
    def createHandlerId(self):
        self.handlerId += 1
        return self.name + 'Handler' + unicode(self.handlerId)

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
    sys.exit(1)

#Paste text from clipboard
def pasteTextCode():
    return """SendInput {Raw}%clipboard%"""