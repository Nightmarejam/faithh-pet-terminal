# NAS Structure Documentation

**Last Updated:** 2026-07-25
**Purpose:** Document the NAS folder structure across all shares

> ⚠️ **Reorganized 2026-07-24.** Everything below the "Historical layout" heading describes
> the *old* eleven-share arrangement and is kept for reference only — those shares were
> migrated and deleted. Current layout is the table immediately below.

## Current layout (2026-07-25)

| Share | Size | Purpose |
|-------|------|---------|
| **media** | 1.2 TB | The only share Plex mounts. `Movies` · `Tv Shows` · `Anime` · `Anime Movies` · `Music` · `Master Lessons` · `comics` · `downloads/` |
| **homelab** | 844 GB | Everything private/technical: `ai/` (models, knowledge, archives) · `audio/` (Tomcat Sound) · `backups/` · `personal/` (incl. `private/`) · `projects/` · `archive/` · `triage/` |
| **pve** | 489 GB | Hypervisor: `dump/` (vzdumps + VM configs) · `template/iso/` |
| **homes** | 2.5 GB | DSM-managed user homes (required for Synology Drive) |

Key path changes for code and docs:

| Old | New |
|---|---|
| `/volume1/AI/models` | `/volume1/homelab/ai/models` |
| `/volume1/AI/knowledge` | `/volume1/homelab/ai/knowledge` |
| `/volume1/raw_ingest/gov_api` | `/volume1/homelab/projects/civic-data` |
| `/volume1/projects/<name>` | `/volume1/homelab/projects/<name>` |
| `/volume1/Personal/*` | `/volume1/homelab/personal/*` |
| `/volume1/Personal/videos/library/*` | `/volume1/media/*` |
| `/volume1/pve-iso` | `/volume1/pve/template/iso` |

Privacy invariant: the Plex container mounts **only** `//nas/media`, so
`homelab/personal/private` is unreachable from the media server by construction.

---

## Historical layout (pre-2026-07-24) — reference only

## Full NAS Overview (Synology DS220j - 13TB)

| Share | Size | Purpose |
|-------|------|---------|
| **Personal** | 1.4TB | Personal videos, photos, documents |
| **Backups** | 1010GB | System backups (legacy, Windows) |
| **AI** (X: drive) | 339GB | Projects, knowledge, media, infrastructure |
| **Audio** | 167GB | Tom Cat Sound production + software |
| **Archive** | 32GB | ISOs, software archive |
| **homes** | 2.5GB | User home directories |
| **Inbox_Sorted** | 1.4GB | Remaining unsorted downloads |

---

## AI Share (X: Drive - 339GB)
**Mount:** `\\nas.taileb8c60.ts.net\AI` → `/mnt/x/`

### Folder Structure

```
X:/
├── projects/                    # Active project repositories
│   ├── faithh/                  # FAITHH AI assistant
│   ├── tomcat-sound/            # Tom Cat Sound LLC (business docs)
│   ├── floating-garden/         # Floating Garden Soundworks
│   ├── constella/               # Constella family system
│   └── inner-monologue/         # Inner Monologue Engine
│
├── knowledge/                   # Curated knowledge base (~140GB)
│   ├── programming/             # Programming books, tutorials
│   ├── languages/               # Language learning (French, Japanese, English)
│   ├── math/                    # Mathematics
│   ├── writing/                 # Writing guides
│   ├── crafts/                  # Cosplay, sewing, DIY
│   ├── personal/                # Life skills, fitness, memory
│   ├── reference/               # The All-Embracing Library (134GB)
│   ├── electronics/             # Schematics, datasheets, DIY kits
│   ├── audio-engineering/       # Audio production, acoustics
│   ├── permaculture/            # Sustainable living, gardening, land dev
│   ├── business/                # Business, finance, legal
│   ├── philosophy/              # Philosophy, psychology
│   └── research/                # Research papers, studies
│
├── media/                       # Plex media library (35 movies)
│   ├── movies/                  # 35 movies (Dark Knight, Disney, Pixar, etc.)
│   ├── tv/                      # TV shows
│   └── music/                   # Billy Joel, MCR, Daft Punk, etc.
│
├── infrastructure/              # System infrastructure
│   ├── docker/                  # Docker configs
│   ├── scripts/                 # Utility scripts
│   ├── configs/                 # Configuration files
│   └── backups/                 # Project backups, archives
│
├── models/                      # AI models (4.5GB)
├── langflow/                    # Langflow workflows
└── learning_portal/             # Japanese Mega Learning Pack (38GB)
```

---

## Other Shares

### Personal (1.4TB)
```
/volume1/Personal/
├── videos/          # 1.3TB - Personal video collection
├── photos/          # 70GB - Photos + Pictures.7z archive
├── documents/       # 19GB - Personal documents, tax returns
├── private/         # 12GB - Private files
└── music/           # 1.4GB - Original music (copied to Plex)
```

### Audio (167GB) - Tom Cat Sound Production
```
/volume1/Audio/
├── tomcat/          # 128GB - Active production projects
├── archive/         # 13GB - Completed projects
├── backups/         # 11GB - Project backups
├── stems/           # 446MB - Stems library
└── software/        # ~5GB - Audio plugins & installers (UAD, Steinberg, etc.)
```

### Backups (1010GB)
```
/volume1/Backups/
├── legacy/          # 489GB - 10 years of mixed files (237K files)
│                    # Contains: 27K photos, 8K music, 2K videos, 1.8K docs
│                    # Plus system junk to be cleaned
├── windows_host/    # 413GB - Windows backup
└── windows_legacy/  # 109GB - Old Windows backup
```

### Archive (32GB)
```
/volume1/Archive/
├── iso_library/     # 11GB - OS installers (Ubuntu, pfSense)
├── software_archive/# 10GB - Software installers, AI tools
├── media/broll/     # 6.9GB - B-roll video footage
├── gaming/          # 52MB - Game saves/configs
└── admin_configs/   # 4KB - Admin configurations
```

---

## Session Log (2026-03-15)

### Cleanup Completed

| Item | Size | Action |
|------|------|--------|
| Inbox_Sorted consolidation | 66GB → 1.4GB | ✅ Sorted |
| Elemental (2023) movie | 18GB | ✅ Moved to Plex |
| Personal/music | 1.4GB | ✅ Copied to Plex |
| homes/Nightmarejam junk | 17 files | ✅ Deleted |
| Root TomCatSound_LLC | 32KB | ✅ Deleted (empty) |
| Outdated installers | ~15GB | ✅ Deleted |
| Duplicate zips | ~5GB | ✅ Deleted |
| Audio software | ~8GB | ✅ Moved to Audio/software |
| Knowledge docs | ~200MB | ✅ Moved to knowledge/* |

**Space Recovered This Session:** ~65GB

### Remaining Work

| Task | Details |
|------|---------|
| Backups/legacy (489GB) | 237K files - extract photos/music/docs, delete system junk |
| ~79 movies in legacy | Move to Plex (35 done, ~79 remaining) |
| FAITHH_20250929T110020Z | Review before deletion (~30GB, mostly duplicates) |
| rmlint cleanup | Review /volume1/AI/rmlint_cleanup.sh before running |

---

## Native Tools (SynoCommunity synocli-file)

PATH: `/volume1/@appstore/synocli-file/bin/`

| Tool | Purpose |
|------|---------|
| **jdupes** | Fast duplicate finder (v1.30.0) |
| **rmlint** | Advanced duplicate/lint detection (v2.10.3) |
| **rg** | ripgrep - fast file search (v15.1.0) |
| **fd** | Fast find alternative |
| **tree** | Directory tree view |
| **sqlite3** | SQLite database CLI |
| **pigz** | Parallel gzip |
| **zstd** | Fast compression |

rclone: `/volume1/@appstore/rclone/bin/rclone` (v1.73.0)

### Dedup Reports

| Report | Location | Size |
|--------|----------|------|
| jdupes | /volume1/AI/jdupes_report.txt | 28MB (33.5GB duplicates) |
| rmlint JSON | /volume1/AI/rmlint_report.json | 92MB (50.9GB duplicates) |
| rmlint cleanup | /volume1/AI/rmlint_cleanup.sh | 44MB (DO NOT RUN without review) |

---

## Access Methods

### From Windows
```powershell
# X: drive is mapped
net use X: \\nas.taileb8c60.ts.net\AI /persistent:yes

# Z: drive needs to be mapped if using Windows
net use Z: \\nas.taileb8c60.ts.net\<share_name> /persistent:yes
```

### From WSL
```bash
# Drives auto-mount via /etc/wsl.conf
ls /mnt/x/
ls /mnt/z/
```

### From Tailscale (Remote)
```bash
# Access via Tailscale IP
ssh jonat@100.115.225.100  # Windows desktop
# Then access via WSL or mapped drives
```

---

## Maintenance

### Duplicate Detection
```bash
# Run fdupes on specific folders
fdupes -r -S /mnt/x/archives /mnt/x/backups > /tmp/duplicates.txt
```

### Backup Strategy
- FAITHH state files: Daily export to infrastructure/backups/
- Project repos: Git push to Gitea (Gen8)
- Media: Torbox cloud + local Plex library

---

## SSH Access (Direct NAS)

SSH enabled on DS220j. Passwordless via key:

```bash
ssh nas                          # via ~/.ssh/synology_ed25519
ssh Nightmarejam@nas.taileb8c60.ts.net    # direct
```

NAS volume path: `/volume1/AI/` = X: drive = `/mnt/x/` in WSL

---

## Related Documentation
- `HARDWARE_INVENTORY.md` - Hardware specs including NAS
- `MEDIA_SETUP.md` - Plex and Stremio configuration
- `INFRASTRUCTURE.md` - Full infrastructure overview
- `NAS_OFFSITE_BACKUP.md` - rclone + Backblaze B2 backup guide
