#IfWinActive ahk_class TxUNCOM
#s::
ClipSaved := ClipboardAll
SetKeyDelay 0
Send, ^{vk43}
SendRaw cmd /c ""C:\\Git\\bin\\sh.exe" --login -i"
Send {enter}
Clipboard := ClipSaved
return
#IfWinActive