#IfWinActive ahk_class TxUNCOM
#a::
ClipSaved := ClipboardAll
SetKeyDelay 0
Send, ^{vk43}
SendRaw cmd /c "cmd.exe"
Send {enter}
Clipboard := ClipSaved
return
#IfWinActive