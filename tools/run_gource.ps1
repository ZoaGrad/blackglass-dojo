$gourcePaths = @(
    "C:\Program Files\Gource\gource.exe",
    "C:\Program Files (x86)\Gource\gource.exe",
    "$env:LOCALAPPDATA\Programs\Gource\gource.exe",
    "$env:ProgramData\chocolatey\bin\gource.exe"
)

$gourceExe = $null

foreach ($path in $gourcePaths) {
    if (Test-Path $path) {
        $gourceExe = $path
        break
    }
}

if ($gourceExe) {
    Write-Host "[*] Found Gource at: $gourceExe"
    # Run Gource in fullscreen with key
    & $gourceExe -s 1 --key --title "ZoaGrad Genesis: Blackglass Shard Alpha" --date-format "%Y-%m-%d" --auto-skip-seconds 1
}
else {
    Write-Error "[!] Gource executable not found. Please ensure it is installed correctly."
    # Fallback to winget location check if possible
    winget show Gource.Gource
}
