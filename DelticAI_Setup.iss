[Setup]
AppName=Deltic AI
AppVersion=1.0.0
AppPublisher=Deltic
DefaultDirName={localappdata}\DelticAI
DefaultGroupName=Deltic AI
OutputDir=installer
OutputBaseFilename=DelticAI_Setup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest
WizardStyle=modern

[Files]
Source: "backend\*"; DestDir: "{app}\backend"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "client\*"; DestDir: "{app}\client"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "database\*"; DestDir: "{app}\database"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "sample-data\*"; DestDir: "{app}\sample-data"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "start_deltic.bat"; DestDir: "{app}"; Flags: ignoreversion

[Dirs]
Name: "{app}\uploads"

[Icons]
Name: "{group}\Deltic AI"; Filename: "{app}\start_deltic.bat"; WorkingDir: "{app}"
Name: "{autodesktop}\Deltic AI"; Filename: "{app}\Start_Deltic.bat"; WorkingDir: "{app}"

[Run]
Filename: "{app}\start_deltic.bat"; Description: "Launch Deltic AI"; \
    Flags: postinstall nowait skipifsilent
