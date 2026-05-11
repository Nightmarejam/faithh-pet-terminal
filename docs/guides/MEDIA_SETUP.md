# Media Streaming Setup Guide

**Last Updated:** 2026-03-14  
**Purpose:** Configure Plex on desktop and Stremio+Torbox for cross-device streaming

---

## Overview

| Service | Purpose | Devices |
|---------|---------|---------|
| **Plex** | Local media library (permanent collection) | Desktop, any browser |
| **Stremio + Torbox** | Cloud streaming (on-demand) | Roku, Apple TV, Phone, Desktop |

---

## Plex Media Server (Desktop PC)

### Installation

1. Download Plex Media Server: https://www.plex.tv/media-server-downloads/
2. Install on Windows desktop
3. Access at: http://localhost:32400/web

### Media Library Locations

```
Z:/Media/
├── Movies/
├── TV Shows/
└── Music/
```

### Configuration

1. **Add Libraries:**
   - Movies → `Z:\Media\Movies`
   - TV Shows → `Z:\Media\TV Shows`
   - Music → `Z:\Media\Music`

2. **Remote Access:**
   - Enable in Settings → Remote Access
   - Port: 32400 (auto-configured)
   - Accessible via Tailscale when away

3. **Transcoding:**
   - Hardware: RTX 3090 (NVENC)
   - Quality: Original when possible

### Torbox → Plex Workflow

```bash
# 1. Download from Torbox
python scripts/torbox_downloader.py download <torrent_id>

# 2. Move to Plex library
mv ~/Downloads/<media> /mnt/z/Media/Movies/
# or
mv ~/Downloads/<media> /mnt/z/Media/TV\ Shows/<show_name>/

# 3. Plex auto-scans and adds to library
```

---

## Stremio + Torbox (Cross-Device Streaming)

### Why Stremio?
- Works on Roku, Apple TV, iOS, Android, Desktop
- Streams directly from Torbox cloud (no download needed)
- No transcoding required (direct play)
- Instant playback of cached torrents

### Installation

**Desktop:**
1. Download: https://www.stremio.com/downloads
2. Install and create account

**Roku:**
1. Add Stremio channel from Roku Channel Store
2. Sign in with same account

**Apple TV:**
1. Download from App Store
2. Sign in with same account

**Mobile (iOS/Android):**
1. Download from App Store / Play Store
2. Sign in with same account

### Torbox Addon Setup

1. Open Stremio on any device
2. Go to Addons → Community Addons
3. Search for "Torbox" or visit: https://torbox.app/stremio
4. Configure with API key:

```
API Key: 1fab2e70-4cac-4c25-a6c5-4d6da6cb70f1
```

5. Enable addon

### Usage

1. Search for movie/show in Stremio
2. Select Torbox stream source
3. If cached: Instant playback
4. If not cached: Torbox downloads, then streams

### Torbox API Commands

```bash
# Check cached torrents
curl -H "Authorization: Bearer $TORBOX_API_KEY" \
  https://api.torbox.app/v1/api/torrents/mylist

# Add magnet link
curl -X POST -H "Authorization: Bearer $TORBOX_API_KEY" \
  -d "magnet=<magnet_link>" \
  https://api.torbox.app/v1/api/torrents/createtorrent

# Download file
curl -H "Authorization: Bearer $TORBOX_API_KEY" \
  "https://api.torbox.app/v1/api/torrents/requestdl?token=<token>&torrent_id=<id>&file_id=<fid>"
```

---

## Device Compatibility Matrix

| Device | Plex | Stremio | Notes |
|--------|------|---------|-------|
| Windows Desktop | ✅ Server + Client | ✅ | Primary setup |
| MacBook Pro | ✅ Client | ✅ | Via Tailscale |
| Roku TV | ✅ Client | ✅ | Best for Stremio |
| Apple TV | ✅ Client | ✅ | Best for Stremio |
| iPhone/Android | ✅ Client | ✅ | Mobile streaming |
| Gen8 Server | ❌ (no transcoding) | N/A | Not recommended |

---

## Recommended Workflow

### For Movies/Shows You Want to Keep
1. Find on Stremio → Stream via Torbox
2. If you like it, download from Torbox
3. Add to Plex library on Z: drive
4. Available offline, high quality

### For Casual Viewing
1. Use Stremio + Torbox directly
2. No storage needed
3. Works on any device

---

## Troubleshooting

### Plex Not Finding Media
- Check folder permissions
- Verify file naming: `Movie Name (Year).mkv`
- Manual scan: Library → ... → Scan Library Files

### Stremio Buffering
- Check Torbox cache status
- Try different quality stream
- Verify internet speed (need 25+ Mbps for 4K)

### Torbox API Errors
- Verify API key is correct
- Check account status at torbox.app
- Rate limits: 100 requests/minute

---

## Related Documentation
- `NAS_STRUCTURE.md` - Media storage locations
- `scripts/torbox_downloader.py` - Torbox API integration
- `HARDWARE_INVENTORY.md` - Device specs
