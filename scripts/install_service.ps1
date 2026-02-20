param(
  [string]$PythonExe = "python",
  [string]$ProjectDir = (Resolve-Path "$PSScriptRoot\\..").Path
)

Write-Host "For MVP, install via NSSM or Task Scheduler."
Write-Host "Command example: $PythonExe -m eams.main"
