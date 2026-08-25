; =============================================================================
; installer\Biesse2Csv_setup.iss
; Project: Biesse2Csv
; Beschrijving: Inno Setup installer voor Intune/Windows-uitrol
; Datum: 2026-08-25
; =============================================================================
;
; Gebruik:
;   ISCC.exe /DMyAppVersion=1.0.0 /DMySourceDir="..\dist\Biesse2Csv_1.0.0" installer\Biesse2Csv_setup.iss
;

#ifndef MyAppVersion
  #define MyAppVersion "1.0.0"
#endif

#ifndef MySourceDir
  #define MySourceDir "..\dist\Biesse2Csv_" + MyAppVersion
#endif

#define MyAppName "Biesse2Csv"
#define MyAppPublisher "Bart Bossuyt"
#define MyAppExeName "Biesse2Csv.exe"
#define MyAppId "{{DFABCC2B-2E51-4BB5-9157-BB371626CA5E}}"

[Setup]
AppId={#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=no
OutputDir=..\dist
OutputBaseFilename=Biesse2Csv_setup_{#MyAppVersion}
SetupIconFile=..\assets\icons\app_icon.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64
ArchitecturesAllowed=x64compatible
UninstallDisplayIcon={app}\{#MyAppExeName}
DirExistsWarning=no
ChangesAssociations=no
DisableDirPage=no
DisableReadyMemo=no
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "dutch"; MessagesFile: "compiler:Languages\Dutch.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Maak een snelkoppeling op het bureaublad"; GroupDescription: "Extra opties:"; Flags: unchecked

[InstallDelete]
Type: filesandordirs; Name: "{app}\_internal"
Type: filesandordirs; Name: "{app}\__pycache__"

[Files]
Source: "{#MySourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{group}\Verwijder {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Description: "Start {#MyAppName}"; Flags: nowait postinstall skipifsilent
