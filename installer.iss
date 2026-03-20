; ==========================================
; Captcha Detector PRO Installer Script
; Fully updated for any Inno Setup version
; ==========================================

[Setup]
; Basic app info
AppName=Captcha Detector PRO
AppVersion=1.0
AppPublisher=HabboLens
DefaultDirName={pf}\CaptchaDetectorPRO
DefaultGroupName=Captcha Detector PRO
OutputDir=Output
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64

; Installer icon (optional)
SetupIconFile=assets\icon.ico

; ==========================================
; Files to include in the installer
; ==========================================
[Files]
; Main EXE built by PyInstaller
Source: "C:\Users\geoff\Desktop\Captcha Detector Pro\dist\main.exe"; DestDir: "{app}"; Flags: ignoreversion
; Assets folder (icons, templates)
Source: "C:\Users\geoff\Desktop\Captcha Detector Pro\assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
; Optional settings.json default file
Source: "C:\Users\geoff\Desktop\Captcha Detector Pro\settings.json"; DestDir: "{app}"; Flags: ignoreversion

; ==========================================
; Shortcuts
; ==========================================
[Icons]
Name: "{group}\Captcha Detector PRO"; Filename: "{app}\main.exe"
Name: "{commondesktop}\Captcha Detector PRO"; Filename: "{app}\main.exe"; Tasks: desktopicon

; ==========================================
; Tasks (optional desktop shortcut)
; ==========================================
[Tasks]
Name: desktopicon; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

; ==========================================
; Registry / Uninstaller
; ==========================================
[UninstallDelete]
Type: files; Name: "{app}\*.*"
Type: dirifempty; Name: "{app}"

; ==========================================
; Messages / UI customization
; ==========================================
[Messages]
WelcomeLabel1=Welcome to the Captcha Detector PRO Setup Wizard
InfoBeforeLabel=This will install Captcha Detector PRO on your computer.