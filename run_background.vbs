Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "c:\Users\Mnvsai\Desktop\Automation"
WshShell.Run """C:\Users\Mnvsai\AppData\Local\Programs\Python\Python312\python.exe"" ""c:\Users\Mnvsai\Desktop\Automation\host.py""", 0, False
