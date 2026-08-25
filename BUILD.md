# Biesse2Csv — Build, signing en installer

Deze buildstraat volgt hetzelfde patroon als de aangeleverde templates:

```text
app/version.py
    ↓
bump_version.py / read_version.py
    ↓
PyInstaller onedir
    ↓
Biesse2Csv.exe
    ↓
SignTool / Authenticode
    ↓
Inno Setup
    ↓
Biesse2Csv_setup_<versie>.exe
    ↓
SignTool / Authenticode
    ↓
Intune
```

## Bestanden

Plaats in de projectroot:

```text
Biesse2Csv.spec
build.bat
build_and_publish.ps1
bump_version.py
read_version.py
requirements-build.txt
BUILD.md
```

Plaats:

```text
app/version.py
installer/Biesse2Csv_setup.iss
```

## Signing

Net zoals in de template gebruikt de build standaard:

```text
signtool sign /fd SHA256 /td SHA256 /tr http://timestamp.digicert.com /a
```

`/a` laat SignTool automatisch een geschikt code-signingcertificaat uit de
Windows certificate store kiezen.

Er wordt géén PFX-bestand of wachtwoord in de repository opgeslagen.

Na signing wordt elk bestand gecontroleerd met:

```text
signtool verify /pa /v
```

Dit past bij een beheerde build-pc waarop het bedrijfs-code-signingcertificaat
beschikbaar is.

## Build uitvoeren

Interactief:

```powershell
.\build_and_publish.ps1
```

of rechtstreeks:

```powershell
.\build.bat
```

Bij `build_and_publish.ps1` is signing standaard `J`.

## Output

Voor versie 1.0.1:

```text
dist/
├─ Biesse2Csv_1.0.1/
│  ├─ Biesse2Csv.exe
│  ├─ _internal/
│  └─ version.txt
│
└─ Biesse2Csv_setup_1.0.1.exe
```

## SignTool

De build zoekt SignTool automatisch:

1. via `PATH`;
2. onder de geïnstalleerde Windows SDK x64-mappen;
3. via de App Certification Kit.

Wanneer signing verplicht is, controleer vooraf:

```powershell
Get-ChildItem Cert:\CurrentUser\My -CodeSigningCert
Get-ChildItem Cert:\LocalMachine\My -CodeSigningCert
```

## Intune

De Inno Setup-installer:

- installeert onder `Program Files\Biesse2Csv`;
- vereist administratorrechten;
- gebruikt een vaste AppId zodat upgrades dezelfde applicatie herkennen;
- installeert alle PyInstaller onedir-bestanden;
- maakt een Startmenu-snelkoppeling;
- heeft een optionele desktopsnelkoppeling;
- ondersteunt silent install/uninstall;
- schrijft geen gebruikersinstellingen naar `Program Files`.

De applicatie zelf gebruikt:

```text
%APPDATA%\Biesse2Csv\settings.json
```

Voor Intune kan de installer silent worden uitgevoerd met:

```powershell
Biesse2Csv_setup_1.0.1.exe /VERYSILENT /SUPPRESSMSGBOXES /NORESTART
```

De uninstall string wordt door Inno Setup in Windows geregistreerd.
