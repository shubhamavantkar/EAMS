param(
  [string]$PythonExe = "python",
  [string]$ProjectDir = (Resolve-Path "$PSScriptRoot\\..").Path
)

$action = New-ScheduledTaskAction -Execute $PythonExe -Argument "-m eams.main" -WorkingDirectory $ProjectDir
$trigger = New-ScheduledTaskTrigger -AtLogOn
Register-ScheduledTask -TaskName "EAMSAgent" -Action $action -Trigger $trigger -Description "EAMS Startup Task" -Force
Write-Host "Scheduled task EAMSAgent created."
