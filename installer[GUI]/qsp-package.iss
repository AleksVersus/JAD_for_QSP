; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "QSP Sublime-Package"
#define MyAppVersion "0.12.1"
#define MyAppPublisher "Aleks Versus'GAM'RUS"
#define MyAppURL "https://github.com/AleksVersus/JAD_for_QSP"

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{C67D76A3-2DF9-4572-B335-33AEEFA2F426}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={userappdata}\Sublime Text\Packages\QSP
DisableDirPage=yes
DefaultGroupName=QSP Sublime-Package
DisableProgramGroupPage=yes
; Uncomment the following line to run in non administrative install mode (install for current user only.)
;PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=D:\my\GameDev\QuestSoftPlayer\projects\JAD\installer[GUI]
OutputBaseFilename=install.QSP.sublime-package.{#MyAppVersion}
SetupIconFile=D:\my\run\sc\autorun.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "ukrainian"; MessagesFile: "compiler:Languages\Ukrainian.isl"

[Files]
Source: "D:\my\GameDev\QuestSoftPlayer\projects\JAD\QSP.sublime-package\.python-version"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\my\GameDev\QuestSoftPlayer\projects\JAD\QSP.sublime-package\Comment Intendation.tmPreferences"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\my\GameDev\QuestSoftPlayer\projects\JAD\QSP.sublime-package\Default.sublime-keymap"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\my\GameDev\QuestSoftPlayer\projects\JAD\QSP.sublime-package\Indentation Rules.tmPreferences"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\my\GameDev\QuestSoftPlayer\projects\JAD\QSP.sublime-package\Location in Goto-List.tmPreferences"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\my\GameDev\QuestSoftPlayer\projects\JAD\QSP.sublime-package\Main.sublime-menu"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\my\GameDev\QuestSoftPlayer\projects\JAD\QSP.sublime-package\Markup in Goto-List.tmPreferences"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\my\GameDev\QuestSoftPlayer\projects\JAD\QSP.sublime-package\QSP.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\my\GameDev\QuestSoftPlayer\projects\JAD\QSP.sublime-package\QSP.sublime-build"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\my\GameDev\QuestSoftPlayer\projects\JAD\QSP.sublime-package\qsp.sublime-syntax"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\my\GameDev\QuestSoftPlayer\projects\JAD\QSP.sublime-package\qsp_locations.sublime-syntax"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\my\GameDev\QuestSoftPlayer\projects\JAD\QSP.sublime-package\syntax_test_qsp.qsps"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\my\GameDev\QuestSoftPlayer\projects\JAD\QSP.sublime-package\qSpy\*"; DestDir: "{app}\qSpy"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "D:\my\GameDev\QuestSoftPlayer\projects\JAD\QSP.sublime-package\Snippets\*"; DestDir: "{app}\Snippets"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "D:\my\GameDev\QuestSoftPlayer\projects\JAD\QSP.sublime-package\Completions\*"; DestDir: "{app}\Completions"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

