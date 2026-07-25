# PC Wake Diagnostics Script
# Run as Administrator in PowerShell

Write-Host "=== PC WAKE DIAGNOSTICS ===" -ForegroundColor Yellow
Write-Host ""

# 1. Check current power plan
Write-Host "1. Current Power Plan:" -ForegroundColor Cyan
powercfg /getactivescheme
Write-Host ""

# 2. Check sleep settings
Write-Host "2. Sleep Settings:" -ForegroundColor Cyan
powercfg /query SCHEME_CURRENT SUB_SLEEP
Write-Host ""

# 3. Check what devices can wake PC
Write-Host "3. Devices that can wake PC:" -ForegroundColor Cyan
powercfg /devicequery wake_armed
Write-Host ""

# 4. Check last wake source
Write-Host "4. Last wake source:" -ForegroundColor Cyan
powercfg /lastwake
Write-Host ""

# 5. Check active wake timers
Write-Host "5. Active wake timers:" -ForegroundColor Cyan
powercfg /waketimers
Write-Host ""

# 6. Check what's preventing sleep
Write-Host "6. Power requests (preventing sleep):" -ForegroundColor Cyan
powercfg /requests
Write-Host ""

# 7. Check recent wake events
Write-Host "7. Recent system events (last 24 hours):" -ForegroundColor Cyan
$events = Get-WinEvent -FilterHashtable @{LogName='System'; StartTime=(Get-Date).AddHours(-24)} | Where-Object {$_.Id -eq 1 -or $_.Id -eq 42 -or $_.Id -eq 12} | Select-Object -First 10
foreach ($event in $events) {
    Write-Host "  [$($event.TimeCreated)] $($event.Id): $($event.Message -split '`n' | Select-Object -First 1)"
}
Write-Host ""

# 8. Check scheduled tasks that can wake
Write-Host "8. Scheduled tasks set to wake PC:" -ForegroundColor Cyan
$tasks = Get-ScheduledTask | Where-Object {$_.Settings.WakeToRun -eq $true}
if ($tasks) {
    $tasks | Select-Object TaskName, State
} else {
    Write-Host "  No tasks set to wake PC"
}
Write-Host ""

# 9. Check sleep study
Write-Host "9. Generating sleep study report..." -ForegroundColor Cyan
try {
    powercfg /sleepstudy /output "$env:USERPROFILE\Desktop\sleep-study-report.html"
    Write-Host "  Report saved to Desktop: sleep-study-report.html"
} catch {
    Write-Host "  Failed to generate sleep study report"
}
Write-Host ""

# 10. Check system power report
Write-Host "10. Generating system power report..." -ForegroundColor Cyan
try {
    powercfg /systempowerreport /output "$env:USERPROFILE\Desktop\system-power-report.html"
    Write-Host "  Report saved to Desktop: system-power-report.html"
} catch {
    Write-Host "  Failed to generate system power report"
}
Write-Host ""

Write-Host "=== DIAGNOSTICS COMPLETE ===" -ForegroundColor Yellow
Write-Host "Check your Desktop for the HTML reports for detailed analysis"
