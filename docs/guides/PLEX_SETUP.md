# Plex Media Server Setup

**Server:** Gen8 (192.158.1.243)  
**Port:** 32400  
**Web UI:** http://192.158.1.243:32400 (Gen8 LAN; use Plex remote access or VPN when off-LAN)  
**Plex Account:** Required — Jonathan has lifetime Plex Pass  
**Started:** 2026-03-15

## Media Library Locations on NAS

| Library | NAS Path | Plex Path |
|---------|----------|-----------|
| Movies | /mnt/x/media/movies | /media/movies |
| TV Shows | /mnt/x/media/tv | /media/tv |
| Music | /mnt/x/media/music | /media/music |

## First-Time Library Setup

After Plex starts, open http://192.158.1.243:32400 in browser:
1. Sign in with Plex account
2. Add Library → Movies → /media/movies
3. Add Library → TV Shows → /media/tv
4. Add Library → Music → /media/music

## NAS Mount on Gen8 (Required for Media Access)

The NAS must be mounted on Gen8 for Plex to see media files:

```bash
ssh jonat@192.158.1.243
sudo apt-get install -y cifs-utils
sudo mkdir -p /mnt/nas/media
sudo mount -t cifs //192.158.1.65/AI/media /mnt/nas/media -o guest,uid=1000,gid=1000,file_mode=0644,dir_mode=0755

# Make persistent across reboots
echo "//192.158.1.65/AI/media /mnt/nas/media cifs guest,uid=1000,gid=1000,file_mode=0644,dir_mode=0755,iocharset=utf8,_netdev 0 0" | sudo tee -a /etc/fstab
```

## Client Apps (all free with Plex Pass)

| Device | App | Notes |
|--------|-----|-------|
| iPhone | Plex app (App Store) | Full playback, Plex Pass unlocked |
| Mac | Plex app (Mac App Store) or browser | Browser works fine |
| Roku TV | Plex channel (Channel Store) | Native app, search "Plex" |

## Plexamp (Music Only)

Separate app for music library:
- iPhone: App Store → "Plexamp"
- Mac: https://plexamp.com → download
- Sign in with Plex account → finds server automatically
- Features: AI radio, 10-band EQ, headphone presets, offline sync

## Adding Media Workflow

1. Download from TorBox → save to /mnt/x/media/downloads/
2. Rename to Plex convention:
   - Movies: `Movie Name (Year).mkv` 
   - TV: `Show Name/Season 01/Show Name - S01E01 - Episode Title.mkv` 
3. Move to /mnt/x/media/movies/ or /mnt/x/media/tv/
4. Plex auto-scans within minutes

## Managing the Server

```bash
# SSH into Gen8
ssh -i ~/.ssh/servicebox_ed25519 jonat@192.158.1.243

# Check status
docker ps | grep plex
docker logs plex --tail 50

# Restart
cd ~/services/plex && docker-compose restart plex

# Update to latest Plex version
cd ~/services/plex && docker-compose pull && docker-compose up -d
```

## Remote access

Plex remote access works via Plex’s own relay / account features. The LAN URL above only works from networks that can reach `192.158.1.243` (same LAN, VPN, or a routed path from WSL — see `docs/security/UDM_SSH_routing_20260402.md` if pings fail from WSL).

## Uptime Kuma Monitoring

Add monitor at http://192.158.1.243:3001:
- Type: HTTP(s)
- URL: http://localhost:32400/identity
- Name: Plex

## Jellyfin (Fallback Option)

If Plex becomes unsatisfactory, Jellyfin can be deployed on Gen8 pointing
at the exact same /media folders. No data migration needed — just point
Jellyfin at /mnt/nas/media/ and it rebuilds metadata from scratch.
See: https://jellyfin.org/docs/general/installation/container/
