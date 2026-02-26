[Setup]
AppName=Docker-for-School
AppVersion=1.0.0
DefaultDirName={autopf}\Docker-for-School
DefaultGroupName=Docker-for-School
OutputDir=.
OutputBaseFilename=Docker-for-School-Setup
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
DisableProgramGroupPage=yes

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Files]
Source: "..\docker-compose.yml"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\homepage-data\*"; DestDir: "{app}\homepage-data"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\vscode-docker\*"; DestDir: "{app}\vscode-docker"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "start-docker-for-school.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "start-docker-for-school.cmd"; DestDir: "{app}"; Flags: ignoreversion

[Dirs]
Name: "{app}\vscode-data"; Flags: uninsalwaysuninstall
Name: "{app}\vscode-config"; Flags: uninsalwaysuninstall
Name: "{app}\windowsserver2022"; Flags: uninsalwaysuninstall
Name: "{app}\debian"; Flags: uninsalwaysuninstall

[Icons]
Name: "{group}\Docker-for-School starten"; Filename: "{app}\start-docker-for-school.cmd"; WorkingDir: "{app}"
Name: "{commondesktop}\Docker-for-School"; Filename: "{app}\start-docker-for-school.cmd"; WorkingDir: "{app}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Desktop-Verknüpfung erstellen"; Flags: unchecked

[Run]
Filename: "{app}\start-docker-for-school.cmd"; WorkingDir: "{app}"; Description: "Docker-for-School starten"; Flags: nowait postinstall skipifsilent
