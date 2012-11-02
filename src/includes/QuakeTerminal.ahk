;^`:: ;Hotkey commented

DetectHiddenWindows, on
IfWinExist ahk_class Console_2_Main
{
	IfWinActive ahk_class Console_2_Main
	  {
			WinHide ahk_class Console_2_Main
			WinActivate ahk_class Shell_TrayWnd
		}
	else
	  {
	    WinShow ahk_class Console_2_Main
	    WinActivate ahk_class Console_2_Main
	  }
}
else
	
	Run Console.exe

DetectHiddenWindows, off
return

; hide Console on "esc".
#IfWinActive ahk_class Console_2_Main
esc::
{
   	WinHide ahk_class Console_2_Main
   	WinActivate ahk_class Shell_TrayWnd
}
return

#IfWinActive ahk_class Console_2_Main
^V::
Send, {Click Middle} ;Middle mouse click is default Console2 hotkey to paste text
return
#IfWinActive