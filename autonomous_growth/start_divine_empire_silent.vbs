Set WshShell = CreateObject("WScript.Shell")
pythonw = WshShell.ExpandEnvironmentStrings("%CD%") & "\venv\Scripts\pythonw.exe"
guardian = WshShell.ExpandEnvironmentStrings("%CD%") & "\divine_empire\divine_guardian.py"
master = WshShell.ExpandEnvironmentStrings("%CD%") & "\divine_empire\divine_master_controller.py"

' Set environment variable for silent mode
WshShell.Environment("Process").Item("SILENT_MODE") = "True"

' Start Divine Guardian
WshShell.Run """" & pythonw & """ """ & guardian & """", 0, False

' Wait a moment before starting Master Controller
WScript.Sleep 2000

' Start Divine Master Controller
WshShell.Run """" & pythonw & """ """ & master & """", 0, False
