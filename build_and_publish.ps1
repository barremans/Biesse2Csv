# build_and_publish.ps1 - Biesse2Csv
# Vraagt alle build-parameters vooraf, voert build.bat niet-interactief uit
# en kan daarna optioneel publish.ps1 starten.
#
# Run vanuit repo root:
#   .\build_and_publish.ps1

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

$buildBat = Join-Path $Root "build.bat"
$publishPs = Join-Path $Root "publish.ps1"

if (-not (Test-Path $buildBat)) {
    throw "Niet gevonden: $buildBat"
}

Write-Host ""
Write-Host "============================================================"
Write-Host "  Biesse2Csv - Build + Installer + Signing"
Write-Host "============================================================"
Write-Host ""

$bumpPart = ""
while ($bumpPart -notin @("patch", "minor", "major")) {
    $bumpPart = Read-Host "Versie verhogen? [patch/minor/major] (Enter = patch)"
    if ($bumpPart -eq "") {
        $bumpPart = "patch"
    }
}
Write-Host "[OK] Versie-bump: $bumpPart"

$makeInstaller = ""
while ($makeInstaller -notin @("J", "N", "j", "n")) {
    $makeInstaller = Read-Host "Inno Setup installer bouwen? [J/N] (Enter = J)"
    if ($makeInstaller -eq "") {
        $makeInstaller = "J"
    }
}
$makeInstaller = $makeInstaller.ToUpper()
Write-Host "[OK] Installer: $makeInstaller"

$doSign = ""
while ($doSign -notin @("J", "N", "j", "n")) {
    $doSign = Read-Host "EXE en installer signen? [J/N] (Enter = J)"
    if ($doSign -eq "") {
        $doSign = "J"
    }
}
$doSign = $doSign.ToUpper()
Write-Host "[OK] Signing: $doSign"

$doPublish = "N"
if (Test-Path $publishPs) {
    while ($doPublish -notin @("J", "N", "j", "n")) {
        $doPublish = Read-Host "Publiceren via publish.ps1 na build? [J/N] (Enter = N)"
        if ($doPublish -eq "") {
            $doPublish = "N"
        }
    }
    $doPublish = $doPublish.ToUpper()
}

Write-Host ""
Write-Host "------------------------------------------------------------"
Write-Host "  Samenvatting:"
Write-Host "    Versie-bump : $bumpPart"
Write-Host "    Installer   : $makeInstaller"
Write-Host "    Signing     : $doSign"
Write-Host "    Publiceren  : $doPublish"
Write-Host "------------------------------------------------------------"

$bevestig = Read-Host "Starten? [J/N]"
if ($bevestig.ToUpper() -ne "J") {
    Write-Host "Afgebroken."
    exit 0
}

$wrapperPath = Join-Path $Root "_build_wrapper.bat"
$wrapperContent = "@echo off`r`n"
$wrapperContent += "set B2C_BUMP_PART=$bumpPart`r`n"
$wrapperContent += "set B2C_MAKE_INSTALLER=$makeInstaller`r`n"
$wrapperContent += "set B2C_DO_SIGN=$doSign`r`n"
$wrapperContent += "call `"$buildBat`"`r`n"
$wrapperContent += "exit /b %ERRORLEVEL%`r`n"

[System.IO.File]::WriteAllText(
    $wrapperPath,
    $wrapperContent,
    [System.Text.Encoding]::ASCII
)

try {
    & cmd.exe /c "`"$wrapperPath`""
    $buildExitCode = $LASTEXITCODE
}
finally {
    Remove-Item $wrapperPath -ErrorAction SilentlyContinue
}

if ($buildExitCode -ne 0) {
    throw "Build faalde (exitcode $buildExitCode)."
}

Write-Host "[OK] Build geslaagd."

if ($doPublish -eq "J") {
    if ($makeInstaller -ne "J") {
        Write-Host "[WARN] Installer niet gebouwd - publiceren overgeslagen."
    }
    else {
        & powershell -ExecutionPolicy Bypass -File $publishPs

        if ($LASTEXITCODE -ne 0) {
            throw "Publish faalde (exitcode $LASTEXITCODE)."
        }
    }
}

Write-Host ""
Write-Host "============================================================"
Write-Host "[DONE] Biesse2Csv build afgerond."
Write-Host "============================================================"
