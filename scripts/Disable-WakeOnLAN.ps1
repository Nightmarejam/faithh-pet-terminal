# Disable Wake-on-LAN for Intel I211 NIC
# Run as Administrator: Right-click -> Run with PowerShell
# Or from elevated terminal: powershell -ExecutionPolicy Bypass -File Disable-WakeOnLAN.ps1

Write-Host "Disabling Wake-on-LAN on Intel I211..." -ForegroundColor Cyan

# Method 1: powercfg
powercfg /devicedisablewake "Intel(R) I211 Gigabit Network Connection"

# Method 2: Registry (belt and suspenders)
$adapters = Get-NetAdapter | Where-Object { $_.InterfaceDescription -like "*I211*" }
foreach ($a in $adapters) {
    Set-NetAdapterAdvancedProperty -Name $a.Name -RegistryKeyword "*WakeOnMagicPacket" -RegistryValue 0 -ErrorAction SilentlyContinue
    Set-NetAdapterAdvancedProperty -Name $a.Name -RegistryKeyword "*WakeOnPattern" -RegistryValue 0 -ErrorAction SilentlyContinue
    Write-Host "  Disabled WoL on: $($a.Name) ($($a.InterfaceDescription))" -ForegroundColor Yellow
}

# Verify
Write-Host "`nWake-armed devices after change:" -ForegroundColor Green
powercfg /devicequery wake_armed

Write-Host "`nDone. Intel I211 should no longer wake your PC." -ForegroundColor Green
Read-Host "Press Enter to close"
