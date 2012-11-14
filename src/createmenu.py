#Author: Artem Mamchych
import ahkutils as ahk
from utils.configfileparser import Parser

if __name__ == "__main__":
    builder = ahk.ScriptBuilder()
    for file in Parser.getCliArgument('--menufiles='):
        ahk.script_file_name = file + ".ahk"
        ahk.Menu.createPrintTextMenuFromFile(file, builder)
    builder.generateScript()