import ahkutils as ahk

import unittest

class MyTestCase(unittest.TestCase):

    def ahk_addAutoComplete_isAhkScriptContains(self, builder, code_sequence):
        sequenceFound = False
        for text in builder.key_bindings:
            if code_sequence in text:
                sequenceFound = True
                break
        self.assertTrue(sequenceFound, msg=code_sequence + " are not found in generated ahk script!")

    def ahk_addAutoCompleteSmart_isGeneratedNameOk(self, input_command, expected_shortcut):
        builder = ahk.ScriptBuilder()
        builder.addAutoCompleteSmart(input_command)
        builder.generateScript()
        self.assertIn(expected_shortcut, builder.abbreviations, msg="FAIL! abbreviate(%s) != %s" % (input_command, expected_shortcut))
        self.ahk_addAutoComplete_isAhkScriptContains(builder, input_command)
        self.ahk_addAutoComplete_isAhkScriptContains(builder, expected_shortcut)

    def test_abbreviate(self):
        self.assertTrue("gss", ahk.abbreviate("git stash save"))
        self.assertTrue("grhH", ahk.abbreviate("git reset --hard HEAD"))
        self.assertTrue("gms", ahk.abbreviate("git merge --strategy=ours"))
        self.assertTrue("tx", ahk.abbreviate("test =====x"))

    def test_addAutoCompleteSmart_Alphanumeric(self):
        self.ahk_addAutoCompleteSmart_isGeneratedNameOk("git checkout master", "gcm")
        self.ahk_addAutoCompleteSmart_isGeneratedNameOk("git status", "gs")
        self.ahk_addAutoCompleteSmart_isGeneratedNameOk("git stash save", "gss")
        self.ahk_addAutoCompleteSmart_isGeneratedNameOk("git rebase master", "grm")

    def test_addAutoCompleteSmart_MinusSymbolIgnored(self):
        self.ahk_addAutoCompleteSmart_isGeneratedNameOk("git reset --hard HEAD", "grhH")
        self.ahk_addAutoCompleteSmart_isGeneratedNameOk("git add --interactive", "gai")
        self.ahk_addAutoCompleteSmart_isGeneratedNameOk("git log -p", "glp")
        self.ahk_addAutoCompleteSmart_isGeneratedNameOk("git rebase --continue", "grc")

#    def test_AhkScriptSuccessfullyGenerated(self):
#        import create-ahk-script as main
#        main.generate()
#        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
