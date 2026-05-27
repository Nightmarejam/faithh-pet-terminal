# SensorBridge — Real Hardware Telemetry in a Proxmox Windows VM

**Status:** Working — confirmed on Proxmox VE 7.0, ASRock X570 Steel Legend, Windows 11 guest  
**Purpose:** Expose real host hardware sensor data (temps, fans, voltages) to a Windows VM via WMI  
**Use case:** Authentic hardware telemetry inside a VM — useful for monitoring dashboards, Rainmeter skins, hardware-aware software, or transparent-VM work

---

## Overview

When Windows runs inside a Proxmox KVM guest, it has no visibility into real hardware sensors. Software like HWiNFO64, AIDA64, or Rainmeter that reads fan speeds and temperatures will either show nothing or report virtual/placeholder values.

SensorBridge solves this by running a .NET 8 Windows Service inside the guest that uses LibreHardwareMonitor (LHM) to read real hardware sensors — passed through from the host — and exposes them via a custom WMI class (`root\SensorBridge\LiveSensors`) and a gRPC streaming endpoint. Any Windows software querying WMI sees live, accurate values.

Verified output from inside the VM:

```
CpuTemp:    50.5°C    ← AMD k10temp, real package thermal
VrmTemp:    54°C      ← NCT6798D SuperIO
SystemTemp: 37°C      ← NCT6798D SYSTIN
Vcore:      0.696V    ← NCT6798D in0
Fan2:       1433 RPM
Fan5:       770 RPM
Fan6:       1864 RPM
```

---

## Architecture

```
┌──────────────────────────────────────────────────────┐
│  Windows Guest VM                                    │
│                                                      │
│  SensorBridge.exe  (.NET 8 Windows Service)          │
│  ├── LibreHardwareMonitor reads NCT6798D / k10temp   │
│  ├── Writes WMI → root\SensorBridge\LiveSensors      │
│  └── gRPC streaming server on :9999 (h2c HTTP/2)    │
└───────────────────────────┬──────────────────────────┘
                            │ gRPC TelemetryService.StreamTelemetry()
               ┌────────────┴────────────┐
               │                         │
┌──────────────▼──────────┐  ┌───────────▼──────────────┐
│  PVE Host               │  │  Other network clients    │
│  sensor-bridge.py       │  │  (Gen8, Grafana, etc.)    │
│  Connects, reads JSON   │  │  client.py smoke client   │
│  Re-serves on :9999     │  │  available in repo        │
└─────────────────────────┘  └──────────────────────────┘
```

**Key point:** Windows is the sensor *server*. LHM inside the guest has direct hardware access via the VM's PCI passthrough or paravirtual paths. PVE and any other network clients connect *to* the Windows VM.

---

## Components

### SensorBridge.exe — Windows Service

The core of the system. Installed and running as a Windows Service (`SensorBridge`, display name: "Hardware Sensor Bridge").

- Reads hardware via **LibreHardwareMonitor** bundled in `C:\SensorBridge\LHM\`
- Populates `root\SensorBridge\LiveSensors` WMI class directly
- Runs a **gRPC streaming server** on port 9999
- Optionally writes `current_sensors.json` as a side-channel snapshot

**Service config (`appsettings.json`):**
```json
{
  "SensorBridge": {
    "LegacyTcp": {
      "Enabled": false,
      "Host": "192.158.1.25",
      "Port": 9999
    },
    "SensorMapping": {}
  }
}
```

**gRPC server (`Program.cs`):**
```csharp
options.ListenAnyIP(9999, listen =>
{
    listen.Protocols = HttpProtocols.Http2;  // cleartext h2c — no TLS needed on LAN
});
```

### Protobuf Schema (`SensorBridge.proto`)

```protobuf
service TelemetryService {
  rpc StreamTelemetry(StreamTelemetryRequest) returns (stream TelemetrySnapshot);
}

message TelemetrySnapshot {
  int64  source_timestamp_ticks = 1;
  string board_device_id        = 2;
  CpuTelemetry     cpu          = 10;
  ThermalTelemetry thermals     = 11;
  FanTelemetry     fans         = 12;
  VoltageTelemetry voltages     = 13;
  StorageTelemetry storage      = 14;
}

message CpuTelemetry     { double package_temp_c = 1; }
message ThermalTelemetry { double system_temp_c = 1;  double vrm_temp_c = 2; }
message FanTelemetry     { double fan2_rpm = 1; double fan5_rpm = 2; double fan6_rpm = 3; }
message VoltageTelemetry { double vcore_v = 1; double v12_v = 2; double v5_v = 3; double v3_3_v = 4; }
message StorageTelemetry { double nvme_temp_c = 1; }
```

### PVE Client (`/usr/local/bin/sensor-bridge.py`)

A lightweight Python script on the Proxmox host that connects to the Windows VM's gRPC endpoint and re-serves data for any PVE-side consumers. Managed by `sensor-bridge.service` (systemd, starts at boot).

### Gen8 Smoke Client (`scripts/gen8_smoke_client/client.py`)

A Python gRPC streaming client for dashboards or monitoring services on other machines on the network. Connects directly to the Windows VM's :9999 endpoint.

---

## WMI Interface

Query from inside the Windows VM:

```powershell
Get-WmiObject -Namespace "root/SensorBridge" -Class "LiveSensors" | Select-Object *
```

The WMI class is defined by `sensors.mof` and `sensors_std.mof` in the repo root. The .NET service populates it directly — no intermediate script or scheduled task is involved.

### Sensor Sources

| WMI Field | Source Chip | Notes |
|-----------|-------------|-------|
| `CpuTemp` | AMD k10temp | Package Tctl |
| `SystemTemp` | NCT6798D | SYSTIN |
| `VrmTemp` | NCT6798D | SMBUSMASTER 1 |
| `Vcore` | NCT6798D | in0 |
| `Fan2Rpm` | NCT6798D | fan2 |
| `Fan5Rpm` | NCT6798D | fan5 |
| `Fan6Rpm` | NCT6798D | fan6 |

> **Note on voltages:** The `v12` field in `current_sensors.json` maps to NCT6798D `in2`, which reads ~3.47V on this board — not the actual 12V rail. The NCT6798D voltage rail assignments vary by motherboard. Verify your own mapping with `sensors -j` on the PVE host before relying on voltage readings.

---

## Discovering Sensors on Your Board

Before deploying on different hardware, run the built-in discovery mode:

```powershell
# In the VM, from C:\SensorBridge\
.\service\SensorBridge.exe --dump-sensors
```

This triggers `TelemetrySampleProvider.ProbeAndLogHardwareTree()` and logs the full LHM hardware tree — every sensor name, type, and current value. Use this output to update the sensor mappings in `appsettings.json` or `SensorMappingOptions.cs`.

On the PVE host side:

```bash
sensors -j | python3 -m json.tool
```

Look for your SuperIO chip (e.g. `nct6798-isa-0290`), CPU temp source (`k10temp-pci-00c3`), and NVMe controller. The ISA address in the chip name (e.g. `0290`) may differ.

---

## Why This Matters for Transparent VMs

In a standard Proxmox VM, hardware sensor queries return nothing or QEMU placeholder values. This is a fingerprinting surface — software that expects sensor data and finds none (or finds QEMU artifacts) can infer virtualization.

SensorBridge closes that surface. WMI sensor queries inside the VM return the same values they would on bare metal hardware.

**What SensorBridge does NOT address:** Anti-cheat systems using kernel driver fingerprinting, RDTSC timing analysis, or PCIe topology inspection operate below the WMI layer. This covers the sensor data detection surface specifically — it's one piece of a larger transparency effort.

---

## Current Status

| Component | Status |
|-----------|--------|
| `SensorBridge` Windows Service | ✅ Running |
| WMI `root\SensorBridge\LiveSensors` populated | ✅ Verified live |
| gRPC server on :9999 | ✅ Working |
| PVE `sensor-bridge.service` (systemd) | ✅ Running |
| Survives VM reboot | ✅ Confirmed (Windows Service auto-start) |
| `SyncWMI.ps1` | ⚠️ Superseded — .NET service writes WMI directly |
| `current_sensors.json` | ⚠️ Written but not consumed — stale artifact |
| Voltage rail mapping (v12, v5, v3_3) | ⚠️ Needs board-specific verification |

---

## Pre-Post Checklist

- [ ] Verify service survives snapshot/restore cycles (not just clean reboots)
- [ ] Confirm correct voltage rail mapping for NCT6798D on X570 Steel Legend
- [ ] Clean up repo: remove or archive `SyncWMI.ps1` and document it as superseded
- [ ] Test `--dump-sensors` output and document the discovery workflow end-to-end
- [ ] Rebuild and verify after hardware migration (PM9A1 install)

---

## File Layout

```
C:\SensorBridge\
├── service\                    ← Deployed binaries (runs as Windows Service)
│   └── SensorBridge.exe
├── SensorBridge\               ← Source (.NET 8)
│   ├── Program.cs
│   ├── TelemetrySampleProvider.cs
│   ├── TelemetryServiceImpl.cs
│   ├── SensorMappingOptions.cs
│   ├── LegacyTcpTelemetryOptions.cs
│   ├── appsettings.json
│   └── Protos\SensorBridge.proto
├── LHM\                        ← LibreHardwareMonitor binaries
├── scripts\gen8_smoke_client\
│   └── client.py               ← Python gRPC client
├── sensors.mof                 ← WMI class definition
├── sensors_std.mof
├── SyncWMI.ps1                 ← Legacy — superseded by direct WMI write in service
└── current_sensors.json        ← Written by service; not consumed by anything active
```
