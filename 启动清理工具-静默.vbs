Option Explicit

Dim shell, fso, scriptDir, command
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)

command = "cmd /c cd /d """ & scriptDir & """ && (pythonw main.py || pyw main.py)"

shell.Run command, 0, False
