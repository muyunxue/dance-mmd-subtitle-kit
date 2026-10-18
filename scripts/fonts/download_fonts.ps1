# Download the open-source fonts used by the kit into scripts/fonts/.
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$dir = Join-Path $PSScriptRoot ""
$base = "https://raw.githubusercontent.com/google/fonts/main"
$files = @(
  @("ofl/anton/Anton-Regular.ttf", "Anton-Regular.ttf"),
  @("ofl/archivoblack/ArchivoBlack-Regular.ttf", "ArchivoBlack-Regular.ttf"),
  @("ofl/bebasneue/BebasNeue-Regular.ttf", "BebasNeue-Regular.ttf"),
  @("ofl/bungee/Bungee-Regular.ttf", "Bungee-Regular.ttf"),
  @("ofl/monoton/Monoton-Regular.ttf", "Monoton-Regular.ttf"),
  @("apache/permanentmarker/PermanentMarker-Regular.ttf", "PermanentMarker-Regular.ttf"),
  @("ofl/rubikglitch/RubikGlitch-Regular.ttf", "RubikGlitch-Regular.ttf"),
  @("ofl/silkscreen/Silkscreen-Regular.ttf", "Silkscreen-Regular.ttf"),
  @("ofl/pirataone/PirataOne-Regular.ttf", "PirataOne-Regular.ttf"),
  @("ofl/unifrakturcook/UnifrakturCook-Bold.ttf", "UnifrakturCook-Bold.ttf")
)
foreach ($f in $files) {
  $out = Join-Path $dir $f[1]
  if (Test-Path $out) { Write-Host "skip $($f[1])"; continue }
  try {
    Invoke-WebRequest -Uri "$base/$($f[0])" -OutFile $out -TimeoutSec 40 -UseBasicParsing
    Write-Host "ok   $($f[1])"
  } catch { Write-Host "FAIL $($f[1])" }
}
Write-Host "Done. System fonts needed: Georgia / Georgia Italic / Microsoft YaHei (Windows)."
