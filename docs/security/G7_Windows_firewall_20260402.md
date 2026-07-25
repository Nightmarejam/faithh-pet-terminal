# G7 Windows Firewall Audit — 2026-04-02

Source: live queries from WSL via Windows `cmd.exe` / `powershell.exe` (no prior PowerShell paste in `reports/security/G7_windows_audit_20260402.md`).

## python.exe rules (`netsh advfirewall ... show rule name="python.exe" verbose`)

Six **Enabled** inbound rules (summary):

| Program | Protocol | Local port | Profile | Action |
|---------|----------|------------|---------|--------|
| `C:\Users\jonat\AppData\Local\Programs\Python\Python310\python.exe` | UDP | Any | Private | Allow |
| Same | TCP | Any | Private | Allow |
| `C:\Users\jonat\AppData\Local\Programs\Python\Python311\python.exe` | UDP | Any | (see netsh) | Allow |
| Same | TCP | Any | (see netsh) | Allow |

**Finding:** Inbound **TCP/UDP allow** on **any local port** for Python 3.10 and 3.11. This is broad. Prefer:

- Remove generic rules if not needed, or
- Scope to **specific ports** used by FAITHH/dev servers only, or
- Restrict to **loopback** for local-only tools.

## Remote Assistance rules

Multiple **Remote Assistance** rules; mix of **Enabled** and **Disabled** for duplicate logical paths.

**Inbound enabled examples:** DCOM-In, RA Server TCP-In, PNRP-In, SSDP UDP/TCP-In, TCP-In (one profile enabled).

**Finding:** If you do not use Remote Assistance, disable the **inbound** RA rules group-wide to reduce attack surface.

## File and Printer Sharing (SMB)

Many rules; several **SMB-In** and related rules show **Enabled = True** (including **File and Printer Sharing (SMB-In)**).

**Port 445:** Standard SMB. **Question:** Is SMB server required on this workstation? If the desktop is not sharing folders to the LAN, **disable inbound SMB-In** on the Private profile (or disable Server service) and rely on NAS for SMB.

## Rules with no recognized application name

Not enumerated in this pass (PowerShell one-liner errored). Recommend:

```powershell
Get-NetFirewallApplicationFilter | Where-Object { -not $_.Program -or $_.Program -eq '' } | ...
```

Run from an elevated PowerShell session for a full program-less rule report.

## Recommendations

1. Tighten **python.exe** rules to explicit ports or remove if obsolete.
2. Disable **Remote Assistance** inbound set if unused.
3. Re-evaluate **SMB-In** on the desktop if NAS is the SMB target.
4. Complete `reports/security/G7_windows_audit_20260402.md` with Defender + `Get-NetFirewallProfile` output from Windows.

## Result: **PARTIAL**
