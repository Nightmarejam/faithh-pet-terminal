# Chip Consolidation Report
**Generated:** 2026-05-17 08:15:58  
**Duration:** 5.3s  
**Input:** 660 micro-topics  
**Output:** 15 macro-chips  
**Assigned:** 540 micro-topics (32,526 docs)  
**Unassigned:** 120 micro-topics (6,191 docs)  

## Macro-Chips

| Rank | Chip | Docs | Micro-Topics | Top Keywords |
|------|------|------|-------------|-------------|
| 1 | **FAITHH Core System** | 8,537 | 139 | chip, faithh langflow, 2024, llc, chips |
| 2 | **Git & Version Control** | 4,181 | 96 | 7077, 7077 processed, processed, repack, submodule |
| 3 | **ChromaDB & RAG Indexing** | 3,309 | 56 | get_message_dict, messages_en, messages_en json, messages messages_en, json handling |
| 4 | **Infrastructure & Docker** | 3,128 | 34 | pihole, pi hole, pi, hole, volume1 |
| 5 | **LLM & AI Tools** | 2,350 | 47 | llama, llama cpp, ollama, groq, llama_model_loader |
| 6 | **Constella Framework** | 2,079 | 34 | astris, civic, merit, vault, governance |
| 7 | **PowerShell & Windows Scripts** | 1,760 | 21 | seg, 100644 backup_20250830_172701, create mode, backup_20250830_172701 gui, gui node_modules |
| 8 | **Hardware & System Config** | 1,197 | 14 | thunderbolt, dock, usb, voltage, mhz |
| 9 | **Health & Wellness** | 1,129 | 11 | blank lines, blanks, headings, expected actual, blank |
| 10 | **File Management & Backup** | 1,090 | 20 | limited liability, liability company, liability, company, amd64 |
| 11 | **Desktop App Development** | 1,025 | 20 | staticresource, grid, microsoft, border, stackpanel |
| 12 | **Audio & Music Business** | 880 | 10 | partnership, partner, schedule, income, tax |
| 13 | **Networking & Security** | 877 | 18 | current device, block supported, supported current, supported, device |
| 14 | **Gen8 Server & Homelab** | 814 | 17 | gen8, udm, enable, langflow services, langflow |
| 15 | **Philosophy & Universe** | 170 | 3 | universe, soup, moon, black, bureau |

## Unassigned Micro-Topics (Top 20)

| Topic ID | Name | Docs | Keywords |
|----------|------|------|----------|
| 2 | Land / 197 / Ors | 494 | land, 197, ors, 215 |
| 7 | Mastering / Xmax / Intercity | 300 | mastering, xmax, intercity, tegeler |
| 14 | Ai Toolkit / Jonathan Ai / Toolkit | 230 | ai toolkit, jonathan ai, toolkit, webui |
| 24 | Bankruptcy / Credit / Debt | 180 | bankruptcy, credit, debt, debts |
| 51 | Embcache / Leaf / Hits | 128 | embcache, leaf, hits, global ws |
| 56 | Founder / Marketing / Artist | 118 | founder, marketing, artist, strategy |
| 61 | Www Baidu / Baidu Com / 24 12 | 115 | www baidu, baidu com, 24 12, baidu |
| 73 | Rite / Rites / Shadow | 100 | rite, rites, shadow, spiritual |
| 74 | Txt Line / Webui Venv / Toolkit Text | 98 | txt line, webui venv, toolkit text, requirement satisfied |
| 77 | Documents Text / Webui Old / Old Venv | 95 | documents text, webui old, old venv, md users |
| 92 | Year / Farm / Oregon | 86 | year, farm, oregon, land |
| 96 | Sizegb / Sum / Childitem | 85 | sizegb, sum, childitem, 1gb |
| 100 | Plex / Media / 32400 | 82 | plex, media, 32400, torbox |
| 104 | Langflow Langflow / Langflow / Parents | 81 | langflow langflow, langflow, parents, true langflow |
| 105 | Vmpath / Relaycommand / Code Path | 81 | vmpath, relaycommand, code path, mwpath |
| 114 | Marriage / Legal / Household | 76 | marriage, legal, household, agreement |
| 118 | Onrunsnippet / Brace / Openidx | 75 | onrunsnippet, brace, openidx, depth |
| 123 | Row / Yield / Encoding Utf | 73 | row, yield, encoding utf, utf |
| 128 | Cid / Idtofile / Valid | 70 | cid, idtofile, valid, incode |
| 141 | Py3 Whl / Py3 / Whl | 66 | py3 whl, py3, whl, kb |

## Integration

Each macro-chip has a centroid embedding (384-dim) for semantic routing:
1. When a query arrives, embed it with all-MiniLM-L6-v2
2. Compute cosine similarity against each chip centroid
3. Activate chips above threshold (e.g., > 0.35)
4. Inject activated chip's context into the LLM prompt