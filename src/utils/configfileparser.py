import os
import ahkutils as ahk

#TODO all config parser code will me moved here

#All reserved words used in config files
class TOKEN(object):
    IGNORE = '[Ignore]'
    END = '[end]'
    BIND = 'bind'
    HOTKEY = 'Hotkey='

class Parser(object):
    file = None

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
    def getShortFilePath(filename):
        return os.path.join(ahk.config_dir_name, os.path.basename(filename))
