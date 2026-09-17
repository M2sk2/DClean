; =====================================================================
; DClean - Inno Setup Compiler Script
; Packages standalone PyInstaller distribution into a single-file installer:
; dist\DClean-Setup-v1.0.exe
; Requires: Inno Setup 6 (https://jrsoftware.org/isdl.php)
; =====================================================================

#define MyAppName "DClean"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "DClean Team"
#define MyAppURL "https://github.com/M2sk2/DClean"
#define MyAppExeName "DClean.exe"

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
; Standalone PyInstaller application bundle
Source: "..\dist\DClean\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Windows Start Menu (Indexed by Windows Search)
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\installer\assets\dclean_icon.ico"
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\installer\assets\dclean_icon.ico"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"

; Desktop Shortcut
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\installer\assets\dclean_icon.ico"; Tasks: desktopicon

[Registry]
; Context menu for .xlsx
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.xlsx\shell\DClean"; ValueType: string; ValueName: ""; ValueData: "Clean with DClean"; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.xlsx\shell\DClean"; ValueType: string; ValueName: "Icon"; ValueData: """{app}\installer\assets\dclean_icon.ico"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.xlsx\shell\DClean\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Tasks: contextmenu

; Context menu for .csv
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.csv\shell\DClean"; ValueType: string; ValueName: ""; ValueData: "Clean with DClean"; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.csv\shell\DClean"; ValueType: string; ValueName: "Icon"; ValueData: """{app}\installer\assets\dclean_icon.ico"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.csv\shell\DClean\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Tasks: contextmenu

; Context menu for .xlsm
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.xlsm\shell\DClean"; ValueType: string; ValueName: ""; ValueData: "Clean with DClean"; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.xlsm\shell\DClean"; ValueType: string; ValueName: "Icon"; ValueData: """{app}\installer\assets\dclean_icon.ico"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.xlsm\shell\DClean\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Tasks: contextmenu

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: postinstall nowait skipifsilent
