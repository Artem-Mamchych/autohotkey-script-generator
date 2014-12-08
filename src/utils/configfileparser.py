import os
import sys
import ahkutils as ahk
import codecs

#TODO all config parser code will me moved here

application = dict() #This dict contains 'ahk_class' names of applications
ahk_classes_file = "ahk_classes.txt"
ahk_classes_file_loaded = None

#All reserved words used in config files
class TOKEN(object):
    IGNORE = '[Ignore]'
    END = '[end]'
    BIND = 'bind'
    HOTKEY = 'Hotkey='
    HK_PRINT = 'print'
    HK_PASTE = 'paste'
    HK_WRAP = 'wrapText'
    SELECTED_TEXT = '[SELECTION]'
    HK_INCLUDE_FILE = 'INCLUDE_FILE'
    HK_DEFINED_IN_FILE = 'DEFINED_IN_FILE'

class Validator(object):
    @staticmethod
    def notEmpty(text, caused_by):
        if not text:
            ahk.error("[%s] got empty text argument" % caused_by)

    @staticmethod
    def checkName(text):
        if "," in text:
            ahk.error("NamingError: ',' symbol can't be used as name! Invalid name is: %s" % text)

class KeyModifier:
    Ctrl = "^"
    Alt = "!"
    Win = "#"
    Shift = "+"

class Parser(object):
    @staticmethod
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

    @staticmethod
    def readFileAsString(filename):
        file = codecs.open(filename, "r", "mbcs")
        return file.read()

    @staticmethod
    def parseHotKey(text):
        if text.startswith("Ctrl+"):
            return text.replace("Ctrl+", KeyModifier.Ctrl)
        elif text.startswith("Alt+"):
            return text.replace("Alt+", KeyModifier.Alt)
        elif text.startswith("Win+"):
            return text.replace("Win+", KeyModifier.Win)
        else:
            return KeyModifier.Win + text

    @staticmethod
    def gotIgnoreToken(command, collection, filename):
        if command == TOKEN.IGNORE:
            if collection and len(collection):
                print("[Config] Rest of file %s is ignored! only %s items is processed" % ((os.path.basename(filename)), len(collection)))
                return True
            else:
                print("[Config] File %s is ignored" % os.path.basename(filename))
                return True

    @staticmethod
    def filterMenuItemName(name):
        """Removes/escapes invalid characters for menu item name"""
        if not name:
            return None
        name = name.replace(",", "")
        if Parser.getCliArgument('--translit'):
            import trans
            name = name.encode('trans')
        return name

    @staticmethod
    def getShortFilePath(filename):
        return os.path.join(ahk.config_dir_name, os.path.basename(filename))

    @staticmethod
    def getApp(key):
        key = key.replace('[', '').replace(']', '')
        if key.startswith("ahk_"):
            return key
        elif key.upper() in application:
            return 'ahk_class ' + application[key.upper()]
        else:
            ahk.error("Application alias '%s' is not defined in file: \n%s"
                "\nAdd it to file or use 'ahk_class AppClassName' syntax" % (key, ahk_classes_file_loaded))

    @staticmethod
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
