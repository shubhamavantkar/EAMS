Unregister-ScheduledTask -TaskName "EAMSAgent" -Confirm:$false -ErrorAction SilentlyContinue
Write-Host "EAMS startup task removed (if present)."
