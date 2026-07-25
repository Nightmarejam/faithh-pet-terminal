# Proxmox Windows 11 VM (101) — GPU/USB passthrough & recovery runbook
Extracted 2026-07-02 from April 2026 sessions (conversation pipeline stage-3).
Tier: procedures **confirmed in-session** on PVE 6.17.13-4 kernel / X570 Steel Legend;
IPs and VM state are **asserted** — verify against the live host before relying on them.

## VM 101 target config (known-good snapshot: `stable-pre-avb`)
- Machine q35/OVMF, `cpu: host,hidden=1`, `affinity: 2-9,14-21`, hugepages, NUMA,
  boot `order=virtio0`, `scsihw: virtio-scsi-single`, e1000 NIC (replaced VirtIO NIC).
- GPU: GTX 1080 Ti (09:00.0) passed through for display/gaming; RTX 3090 (0e:00.0)
  stays host-side for inference. 3090 is on the direct CPU PCIe 4.0 x16 path; the
  1080 Ti routes through the Matisse chipset switch (~PCIe 3.0 x8).
- The `error writing '1' to /sys/bus/pci/devices/.../reset: Inappropriate ioctl`
  messages on `qm start` are **expected warnings** on this chipset, not failures.

## SMBIOS/host-identity spoof (WMI-clean VM)
```
qm set 101 --args "-smbios type=0,vendor=AMI,version=P5.67,date=06/24/2025 \
  -smbios type=1,manufacturer=ASRock,product=X570SteelLegend,version=P5.67,serial=<board-serial>"
qm set 101 --vmgenid 0
```
Verify from Windows: `Get-WmiObject Win32_BIOS / Win32_BaseBoard / Win32_ComputerSystem`.
Notes: type=0 fixes the "Proxmox EDK II" vendor string; put the BIOS version in type=1
too or `SMBIOSBIOSVersion` stays empty. Custom CPU flags (hv_* enlightenments, kvm=off)
must ALSO live in `--args` — `qm set --cpu` rejects them on this Proxmox version.
Residual VirtIO PnP IDs (`VEN_1AF4` disk/serial) still leak; EAC-hardened titles were
not defeated and that effort was parked (SensorBridge review drew the same line).

## QEMU guest agent (fixes `qm shutdown` timeouts)
1. `qm set 101 --ide3 local:iso/virtio-win-0.1.285.iso,media=cdrom`
2. In Windows run `virtio-win-guest-tools.exe` (the all-in-one; NOT the plain driver MSI).
3. Verify: `Get-Service QEMU-GA` → Running/Automatic; from PVE `qm agent 101 ping`.
4. `qm set 101 --delete ide3`.

## Boot-failure recovery (0xc0000001 / 0x7B INACCESSIBLE_BOOT_DEVICE)
Causes hit in April: adding `serial=` to virtio0 changed the disk identity (0x7B —
revert the serial to fix); boot order silently set to `net0`; BCD corruption.
Recovery path that worked:
1. `qm stop 101`; revert disk line: `qm set 101 --virtio0 local-lvm:vm-101-disk-2,size=953872M`
2. Attach BOTH ISOs before booting WinPE (hotplug into a running recovery env does not work):
   `qm set 101 --ide2 local:iso/Win11_25H2_English_x64_v2.iso,media=cdrom`
   `qm set 101 --ide3 local:iso/virtio-win-0.1.285.iso,media=cdrom`
   `qm set 101 --boot order=ide2` ; `qm start 101`
3. WinPE cannot see the virtio disk (`bootrec /scanos` → 0 installs) until you load the
   driver: `drvload <virtio-iso>:\vioscsi\w11\amd64\vioscsi.inf`, then bootrec repairs.
4. Restore `qm set 101 --boot order=virtio0` immediately after repair, detach ISOs.
Snapshot before risky config changes: `qm snapshot 101 <name> --description "..."`.

## USB controller passthrough
Right controller on this board: **10:00.3 AMD Matisse USB 3.0** — alone in IOMMU group 31
(0a:00.1/0a:00.3 were the wrong ones; remove those hostpci entries).
Find grouping: `find /sys/kernel/iommu_groups/*/devices/ -name "0000:10:00.3"`.
WARNING: once the VM claims it, the PVE host loses local keyboard/mouse.

## Related
- Bare-metal era config of the same box: homelab repo,
  docs/hardware/baremetal-dual-gpu-and-gen8-snapshot.md (private).
- Full source threads: "GPU passthrough and system stability" (04-29, 322 msgs),
  "USB controller passthrough" (04-20, 378), "Windows VM boot recovery" (04-29, 212).
