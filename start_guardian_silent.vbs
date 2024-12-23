Set WshShell = CreateObject("WScript.Shell")
pythonw = WshShell.ExpandEnvironmentStrings("%CD%") & "\venv\Scripts\pythonw.exe"
guardian = WshShell.ExpandEnvironmentStrings("%CD%") & "\divine_empire\divine_guardian.py"
WshShell.Run """" & pythonw & """ """ & guardian & """", 0, False
