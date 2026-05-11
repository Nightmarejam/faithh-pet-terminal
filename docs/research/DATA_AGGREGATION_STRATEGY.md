# Data Aggregation Strategy

## Target Topics

| Topic | Priority | Est. Size | Source Strategy |
|-------|----------|-----------|-----------------|
| **Programming & System Design** | High | 50-100 GB | LibGen + existing learning_portal |
| **Electronics & Circuits** | High | 20-50 GB | LibGen + audio schematics (done) |
| **Permaculture & Agriculture** | High | 10-30 GB | LibGen + specialized archives |
| **Animal Care & Veterinary** | Medium | 10-20 GB | LibGen |
| **Landworks & Earthworks** | Medium | 5-10 GB | LibGen + construction archives |
| **Architecture & Construction** | Medium | 20-50 GB | LibGen |
| **Audio Engineering** | High | Done | Gyraf schematics (41 MB downloaded) |

## Existing Assets

### Learning Portal (177 GB)
Location: `X:\learning_portal\Learning Portal\`

Already contains:
- Programming (Python, Java, Rust, C++, JavaScript, SQL)
- Network & Security
- Japanese language learning
- Math
- Cosplay/crafting (sewing, armor, props)
- Life skills

### Audio Schematics (41 MB)
Location: `X:\AI\audio_schematics\`

Contains:
- SSL 4000E (bus compressor, input channels, VCA)
- Neumann (isolation amps, faders, mixbus)
- Sony C800G
- VCA datasheets (Aphex, DBX, THAT Corp)
- NTP discrete opamps

### Civic Tech Repos (286 MB)
Location: `E:\civic_tech_repos\`

Contains:
- Decidim (participatory democracy)
- CONSUL (citizen participation)
- Loomio (collaborative decisions)
- DemocracyOS (deliberation)
- Polis (AI-mediated consensus)

## LibGen Strategy

### Option A: Curated Search (Recommended)
1. Search LibGen web interface for specific books
2. Get magnet links for individual books
3. Add to Torbox → download to NAS
4. Index to ChromaDB

**Pros**: Precise, no wasted space
**Cons**: Manual effort per book

### Option B: Topic Torrents
LibGen doesn't organize by topic, but some curated collections exist:
- Archive.org has topic-specific collections
- Reddit r/libgen has curated lists

### Option C: Full Archive Sections
Download specific ID ranges that are known to contain technical content:
- r_2000000-r_2500000: Heavy on technical/engineering (2015-2017 uploads)
- r_3000000-r_3500000: More recent technical content

**Warning**: Each 1000-book torrent is ~50-100 GB

## Recommended Workflow

### Phase 1: Curated Downloads (Now)
1. Create wishlist of specific books per topic
2. Search LibGen for each
3. Add magnets to Torbox
4. Download completed files to NAS

### Phase 2: Bulk Archive (Later)
1. Identify high-value torrent ranges
2. Download via Torbox
3. Filter/organize after download
4. Index relevant content to ChromaDB

## Torbox Integration

API Key: Configured in `scripts/torbox_downloader.py`

Commands:
```bash
# Check account status
python3 scripts/torbox_downloader.py status

# Add a magnet link
python3 scripts/torbox_downloader.py add "magnet:?xt=urn:btih:..."

# List all torrents
python3 scripts/torbox_downloader.py list

# Download all completed
python3 scripts/torbox_downloader.py download-all
```

## Topic-Specific Sources

### Permaculture
- Permaculture Research Institute archives
- Soil Food Web resources
- ATTRA (Appropriate Technology Transfer for Rural Areas)
- Rodale Institute publications

### Animal Care
- Merck Veterinary Manual (available on LibGen)
- Storey's Guides series (goats, chickens, etc.)
- FAO animal husbandry guides

### Electronics
- Art of Electronics (Horowitz & Hill)
- ARRL Handbook
- Forrest Mims notebooks
- Application notes from TI, Analog Devices, Linear Tech

### Architecture
- Architectural Graphic Standards
- Building Construction Illustrated (Ching)
- Pattern Language (Alexander)
- Passive House resources

## NAS Space Budget

Total: 13 TB
Used: 3.3 TB
Free: 9.7 TB

Allocation plan:
- Learning Portal expansion: 2 TB
- Audio schematics: 1 GB (done)
- Civic tech: 1 GB (done)
- LibGen curated: 500 GB
- Future bulk archives: 5 TB reserve
