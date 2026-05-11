# Chip Consolidation Report
**Generated:** 2026-04-11 14:59:35  
**Duration:** 5.3s  
**Input:** 646 micro-topics  
**Output:** 15 macro-chips  
**Assigned:** 572 micro-topics (35,534 docs)  
**Unassigned:** 74 micro-topics (2,947 docs)  

## Macro-Chips

| Rank | Chip | Docs | Micro-Topics | Top Keywords |
|------|------|------|-------------|-------------|
| 1 | **FAITHH Core System** | 5,502 | 83 | faithh langflow, ws, chip, bullets, setup install |
| 2 | **LLM & AI Tools** | 4,902 | 77 | langflow, torch, langflow langflow, langflow ui, tts |
| 3 | **Infrastructure & Docker** | 3,728 | 64 | pihole, pi hole, pi, hole, volume1 docker |
| 4 | **ChromaDB & RAG Indexing** | 3,658 | 69 | messages_en json, messages messages_en, messages_en, json handling, json file |
| 5 | **Tom Cat Sound / Audio** | 2,939 | 33 | fgsjson, mastering, 2024, audio, jonat floating_gardens_soundworks |
| 6 | **Git & Version Control** | 2,596 | 56 | 7077, 7077 processed, processed, rosetta stone, rosetta |
| 7 | **File Organization & Archives** | 2,285 | 44 | kb, whl, robocopy, py3 whl, py3 |
| 8 | **Constella Framework** | 1,852 | 34 | civic, astris, celestial, v1, celestial equilibrium |
| 9 | **Hardware & System Config** | 1,711 | 22 | usb, ilo, thunderbolt, dock, boot |
| 10 | **Philosophy & Worldview** | 1,473 | 18 | earth, resonance, energy, resonant, universe |
| 11 | **Health & Wellness** | 1,283 | 8 | yeah, lets, sounds, okay, let |
| 12 | **Desktop App Development** | 1,135 | 19 | staticresource, grid, margin, stackpanel, border |
| 13 | **Networking & Security** | 1,020 | 20 | current device, block supported, supported current, supported, device block |
| 14 | **PowerShell & Windows Scripts** | 1,007 | 16 | 100644 backup_20250830_172701, create mode, copy backup_20250830_172701, 100644, mode 100644 |
| 15 | **Gen8 Server & Homelab** | 443 | 9 | ssh, tailscale, gen8, udm, vaultwarden |

## Unassigned Micro-Topics (Top 20)

| Topic ID | Name | Docs | Keywords |
|----------|------|------|----------|
| 62 | Multiple / Expected Actual / Blank Lines | 113 | multiple, expected actual, blank lines, blanks |
| 75 | 24 12 / 09 24 / Com | 97 | 24 12, 09 24, com, www baidu |
| 100 | Scroll / Review / Packet | 82 | scroll, review, packet, review scroll |
| 123 | Resume / Tech / Skills | 75 | resume, tech, skills, degree |
| 146 | False / Title Case False / Title Case | 68 | false, title_case false, title_case, true title_case |
| 152 | Schemas / Type String / Ref | 66 | schemas, type string, ref, type |
| 170 | 32Gb / Gmktec / K10 | 63 | 32gb, gmktec, k10, 64gb |
| 175 | 22 2025 / Png / 12 02 | 62 | 22 2025, png, 12 02, png 22 |
| 191 | Lake / County / Campground | 58 | lake, county, campground, resort |
| 194 | Cover Note / Deployment / Cover | 58 | cover note, deployment, cover, pdf |
| 197 | Ba / Bath / Albany | 57 | ba, bath, albany, apartments |
| 200 | Mycelium / Mushroom / Fruiting | 56 | mycelium, mushroom, fruiting, nucleus |
| 201 | Onrunsnippet / Openidx / Closes | 56 | onrunsnippet, openidx, closes, brace |
| 204 | Sizegb / Sum / 1Gb | 56 | sizegb, sum, 1gb, childitem |
| 213 | Const / Textcontent / Div | 55 | const, textcontent, div, const await |
| 215 | Udp / 09 27 / 127 53 | 55 | udp, 09 27, 127 53, udp 2025 |
| 216 | Sum / Old Files / Recurse File | 55 | sum, old files, recurse file, dst |
| 221 | Writeline / Methodinvocationexception / Writeline Row | 54 | writeline, methodinvocationexception, writeline row, sw writeline |
| 237 | Seg / Replace Seg / Seg Regex | 51 | seg, replace seg, seg regex, regex replace |
| 268 | Infographic / Walking Gait / Arrows | 47 | infographic, walking gait, arrows, walking |

## Integration

Each macro-chip has a centroid embedding (384-dim) for semantic routing:
1. When a query arrives, embed it with all-MiniLM-L6-v2
2. Compute cosine similarity against each chip centroid
3. Activate chips above threshold (e.g., > 0.35)
4. Inject activated chip's context into the LLM prompt