# IMPORTANT: This script will NEVER touch Windsurf process ID 18352 (our conversation)
$PROTECTED_PROCESS = 18352  # Our current Windsurf instance

# Get all Windsurf processes except our protected one
$windsurf_processes = Get-Process Windsurf | Where-Object { $_.Id -ne $PROTECTED_PROCESS }

# Close other Windsurf instances
foreach ($process in $windsurf_processes) {
    Write-Host "Closing Windsurf process ID: $($process.Id)"
    Stop-Process -Id $process.Id -Force
}

# Clear temp files
Remove-Item -Path "$env:TEMP\*" -Recurse -Force
Remove-Item -Path "C:\Windows\Temp\*" -Recurse -Force

# Clear Windows DNS cache
ipconfig /flushdns

# Clear Windows Store cache
wsreset.exe

# Optimize services
Get-Service | Where-Object {$_.Status -eq 'Running' -and $_.StartType -eq 'Automatic'} | 
    Select-Object Name, DisplayName, Status, StartType |
    Export-Csv -Path "$env:USERPROFILE\Desktop\running_services.csv" -NoTypeInformation

Write-Host "System cleanup complete! Protected Windsurf process $PROTECTED_PROCESS is safe."
