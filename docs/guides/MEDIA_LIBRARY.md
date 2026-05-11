# Media Library Guide

**Server:** Plex on Gen8 (http://192.158.1.243:32400)  
**Media root:** /mnt/x/media/ (NAS X: drive)  
**Quality target:** 4K UHD Remux → 4K → 1080p Remux → 1080p

---

## Quality Hierarchy

| Quality | File Size (movie) | Use When |
|---------|-------------------|----------|
| 4K Remux | 50-120 GB | Best possible, no compression |
| 4K HDR10/DV | 20-60 GB | 4K with some compression, still excellent |
| 1080p Remux | 20-40 GB | Best 1080p, no compression |
| 1080p BluRay | 8-20 GB | Compressed but excellent |
| 1080p WEB-DL | 4-8 GB | Good for streaming releases |
| 720p | 2-4 GB | Fallback only |

**Jonathan's Roku TV:** TCL 55" 4K HDR10 — supports 4K H.265, HDR10, Dolby Vision
**Rule:** Always grab 4K if available. Storage is cheap on a 13TB NAS.

---

## Naming Convention (Plex-required)

### Movies
```
/mnt/x/media/movies/
└── Movie Title (Year).mkv
    Examples:
    The Matrix (1999).mkv
    Dune Part Two (2024).mkv
    Oppenheimer (2023).mkv
```

### TV Shows
```
/mnt/x/media/tv/
└── Show Name/
    └── Season 01/
        └── Show Name - S01E01 - Episode Title.mkv
        Examples:
        Breaking Bad - S01E01 - Pilot.mkv
        Severance - S02E01 - Hanging.mkv
```

### Music
```
/mnt/x/media/music/
└── Artist Name/
    └── Album Name (Year)/
        ├── 01 - Track Title.flac
        └── cover.jpg
```

---

## Adding New Media Workflow

### Step 1: Find the torrent
Use Stremio to discover → note the name/year
Or search directly: 1337x.to, rarbg mirrors, YTS (movies only, 1080p)

For 4K specifically: search "[Movie Name] 2160p" or "[Movie Name] 4K Remux"

### Step 2: Add to TorBox
Option A — Stremio: just stream it, TorBox caches automatically
Option B — Manual: torbox.app → Add Torrent → paste magnet

### Step 3: Download to NAS
```bash
# Check what's cached and ready
cd ~/ai-stack && python3 scripts/media_download.py list

# Download a movie (interactive, handles naming)
python3 scripts/media_download.py movie "Movie Title" --year 2024 --id TORBOX_ID

# Or direct wget into movies folder
wget -c -O "/mnt/x/media/movies/Movie Title (Year).mkv" "DOWNLOAD_URL"
```

### Step 4: Plex picks it up automatically
Plex scans every few minutes. New items appear in ~2-5 minutes.
Manual scan: Plex web UI → library → ... → Scan Library Files

---

## Plex Library Categories (Current)

| Library | Path | Content |
|---------|------|---------|
| Movies | /media/movies | Feature films, documentaries |
| TV Shows | /media/tv | Series, mini-series |
| Music | /media/music | Albums (Plexamp) |

## Future Libraries (add as content grows)

When you have 10+ items in a category, add a separate library:
- **Anime** → /media/anime (Plex handles anime naming differently)
- **Documentaries** → /media/documentaries
- **Concerts** → /media/concerts
- **Stand-up** → /media/standup
- **Kids** → /media/kids

---

## Format Notes

**Best container:** MKV — supports all codecs, subtitles, multiple audio tracks
**Best video codec:** H.265/HEVC — half the size of H.264 at same quality
**Best audio:** DTS-HD Master Audio or TrueHD Atmos for remux, 
               EAC3 Atmos for compressed, AAC for web sources

**Subtitles:** Look for "SDH" (Subtitles for Deaf/Hard of hearing) — 
includes all dialogue plus sound effects. Best for foreign language films.
Prefer embedded SRT/ASS over separate files.

---

## Torrent Name Decoder

```
Movie.Name.2024.2160p.UHD.BluRay.REMUX.HDR.HEVC.TrueHD.Atmos-GROUP
                │       │         │     │    │      │        │
                │       │         │     │    │      │        └ Release group
                │       │         │     │    │      └ Audio codec
                │       │         │     │    └ Video codec
                │       │         │     └ HDR format
                │       │         └ REMUX = no re-encoding, original disc
                │       └ Source: UHD BluRay (best)
                └ Resolution: 2160p = 4K

Good signs: REMUX, BluRay, WEB-DL, HDR, HEVC, TrueHD, DTS-HD
Bad signs: CAM, TS, TC, HDCAM (pre-release cinema recordings)
```

---

## Client Apps

| Device | App | Notes |
|--------|-----|-------|
| iPhone | Plex (App Store) | Video + photos |
| iPhone | Plexamp (App Store) | Music only, excellent |
| Mac | Plexamp (plexamp.com) | Music |
| Mac | Plex (browser or app) | Video |
| Roku | Plex (Channel Store) | Video, good 4K support |

## Plexamp Quick Start

1. Install Plexamp on iPhone/Mac
2. Sign in with Plex account
3. It finds your server at 192.158.1.243 automatically
4. Add music to /mnt/x/media/music/ → Plexamp sees it within minutes
5. Sonic Sage: tap radio icon → describe what you want to hear

---

## TorBox Integration

API key stored in: `~/ai-stack/.env` as `TORBOX_API_KEY`

### Quick Commands

```bash
# List all cached torrents with quality scores
python3 scripts/media_download.py list

# Check active downloads
python3 scripts/media_download.py status

# Download a movie (interactive)
python3 scripts/media_download.py movie "Movie Title" --year 2024 --id 12345

# Download a TV episode
python3 scripts/media_download.py tv "Show Name" --season 1 --episode 1 --id 12345
```

### Quality Scoring

The script auto-scores torrents:
- **150+**: 4K Remux (best)
- **90-150**: 4K or 1080p BluRay
- **60-90**: 1080p WEB-DL
- **<60**: Lower quality or unknown
- **Negative**: CAM/TS (avoid)
