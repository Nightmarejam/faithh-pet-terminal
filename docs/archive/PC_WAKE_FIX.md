# PC Wake Fix Commands
**Run these as Administrator in PowerShell before sleep:**

## Disable Mouse/Keyboard Wake
```powershell
# Disable all mouse devices from waking PC
powercfg /devicedisablewake "HID-compliant mouse (002)"
powercfg /devicedisablewake "HID-compliant mouse (004)"
powercfg /devicedisablewake "HID-compliant mouse (005)"
powercfg /devicedisablewake "HID-compliant mouse (006)"

# Disable all keyboard devices from waking PC
powercfg /devicedisablewake "HID Keyboard Device (001)"
powercfg /devicedisablewake "HID Keyboard Device (004)"
```

## Disable Network Wake
```powershell
powercfg /devicedisablewake "Intel(R) I211 Gigabit Network Connection"
```

## Check What Can Wake PC
```powershell
powercfg /devicequery wake_armed
```

## Check Last Wake Source
```powershell
powercfg /lastwake
```

## Disable Automatic Maintenance
```powershell
# Disable automatic maintenance wake
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Schedule\Maintenance" /v WakeUp /t REG_DWORD /d 0 /f

# Disable Windows Update wake
reg add "HKLM\SOFTWARE\Microsoft\WindowsUpdate\UX" /v IsConvergedUpdateModeEnabled /t REG_DWORD /d 0 /f
```

## Additional Power Settings
```powershell
# Disable hybrid sleep
powercfg /setactive SCHEME_CURRENT
powercfg /change standby-timeout-ac 0
powercfg /change standby-timeout-dc 0

# Disable hibernate
powercfg /hibernate off
```

## To Re-enable if Needed
```powershell
# Re-enable mouse wake (replace with your device name)
powercfg /deviceenablewake "HID-compliant mouse (002)"
```
