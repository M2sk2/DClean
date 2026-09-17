; =====================================================================
; DClean - Inno Setup Compiler Script
; Compiles a single-file Windows installer: DClean-Setup-v1.0.exe
; Requires: Inno Setup 6 (https://jrsoftware.org/isdl.php)
; =====================================================================

#define MyAppName "DClean"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "DClean Team"
#define MyAppURL "https://github.com/M2sk2/DClean"
#define MyAppExeName "dclean.bat"

[Setup]
AppId={{D9B38F72-3E6B-4D88-9F31-4A59A1D019F8}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={localappdata}\Programs\DClean
DisableDirPage=no
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=..\dist
OutputBaseFilename=DClean-Setup-v1.0
SetupIconFile=assets\dclean_icon.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "contextmenu"; Description: "Add 'Clean with DClean' to Windows Explorer right-click menu"; GroupDescription: "Windows Explorer Integration:"

[Files]
; Core application files
Source: "..\pipeline\*"; DestDir: "{app}\pipeline"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\models\*"; DestDir: "{app}\models"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\config\*"; DestDir: "{app}\config"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\installer\*"; DestDir: "{app}\installer"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\requirements.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\installer\dclean_launcher.py"; IconFilename: "{app}\installer\assets\dclean_icon.ico"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\installer\dclean_launcher.py"; IconFilename: "{app}\installer\assets\dclean_icon.ico"; Tasks: desktopicon

[Registry]
; Context menu for .xlsx
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.xlsx\shell\DClean"; ValueType: string; ValueName: ""; ValueData: "Clean with DClean"; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.xlsx\shell\DClean"; ValueType: string; ValueName: "Icon"; ValueData: """{app}\installer\assets\dclean_icon.ico"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.xlsx\shell\DClean\command"; ValueType: string; ValueName: ""; ValueData: """pythonw.exe"" ""{app}\installer\dclean_launcher.py"" ""%1"""; Tasks: contextmenu

; Context menu for .csv
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.csv\shell\DClean"; ValueType: string; ValueName: ""; ValueData: "Clean with DClean"; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.csv\shell\DClean"; ValueType: string; ValueName: "Icon"; ValueData: """{app}\installer\assets\dclean_icon.ico"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.csv\shell\DClean\command"; ValueType: string; ValueName: ""; ValueData: """pythonw.exe"" ""{app}\installer\dclean_launcher.py"" ""%1"""; Tasks: contextmenu

[Run]
Filename: "pythonw.exe"; Parameters: """{app}\installer\dclean_launcher.py"""; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: postinstall nowait skipifsilent
