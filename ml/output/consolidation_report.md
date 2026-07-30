# Chip Consolidation Report
**Generated:** 2026-07-30 20:15:25  
**Duration:** 16.1s  
**Input:** 971 micro-topics  
**Output:** 18 macro-chips  
**Assigned:** 604 micro-topics (31,979 docs)  
**Unassigned:** 367 micro-topics (16,639 docs)  

## Macro-Chips

| Rank | Chip | Docs | Micro-Topics | Top Keywords |
|------|------|------|-------------|-------------|
| 1 | **FAITHH Core System** | 6,332 | 104 | chip, faithh langflow, chips, div, faithh inference |
| 2 | **Git & Version Control** | 5,249 | 103 | index, democracy index, democracy, expression index, freedom expression |
| 3 | **File Management & Backup** | 5,241 | 139 | democracy index, democracy, participatory democracy, electoral democracy, egalitarian democracy |
| 4 | **LLM & AI Tools** | 2,046 | 31 | false, maxtokens, gpt codex, gpt, isinternal |
| 5 | **Infrastructure & Docker** | 1,920 | 27 | pihole, volume1 docker, volume1, docker pihole, td |
| 6 | **Constella Framework** | 1,864 | 32 | astris, line length, sweden, eden, civic |
| 7 | **Desktop App Development** | 1,614 | 30 | faithh desktop, faithh src, faithh faithh, hdx, border |
| 8 | **PowerShell & Windows Scripts** | 1,292 | 17 | mexico year, country mexico, 7077, 7077 processed, employment |
| 9 | **Hardware & System Config** | 1,266 | 15 | inf, usb, thunderbolt, dock, driver |
| 10 | **ChromaDB & RAG Indexing** | 1,088 | 25 | chatgpt, conversations, jsonl, schema, google cloud |
| 11 | **Gen8 Server & Homelab** | 869 | 18 | ssh, docs security, gen8, langflow services, langflow |
| 12 | **Networking & Security** | 858 | 18 | vailability, portugal, emissions, year vailability, vailability country |
| 13 | **Inference & Model Serving** | 490 | 13 | vllm, faithh_force_local, wsl_migration, ops vllm, cc_proxy |
| 14 | **Health & Wellness** | 468 | 9 | headings, blanks, blank lines, expected actual, blank |
| 15 | **Philosophy & Universe** | 427 | 4 | nan, ok ok, ok, earth, sun |
| 16 | **Architecture & Documentation** | 426 | 8 | parity, phase flip, label, power bi, coherence |
| 17 | **Audio & Music Business** | 278 | 5 | fgsjson, jonat floating_gardens_soundworks, floating_gardens_soundworks, operational_pillars, phase_1_financials |
| 18 | **Retrieval & Embeddings** | 251 | 6 | mali, add member, country guatemala, guatemala year, guatemala |

## Unassigned Micro-Topics (Top 20)

| Topic ID | Name | Docs | Keywords |
|----------|------|------|----------|
| 9 | Voicemeeter / Obs / Audio | 214 | voicemeeter, obs, audio, elgato |
| 22 | Ai Toolkit / Jonathan Ai / Toolkit | 157 | ai toolkit, jonathan ai, toolkit, jonathan |
| 28 | Sensorbridge / Sensorbridge Sensorbridge / Wmi | 140 | sensorbridge, sensorbridge sensorbridge, wmi, ps sensorbridge |
| 31 | Time Series / Series / Cross Section | 132 | time series, series, cross section, qog |
| 33 | Esd / Pad / Thermal | 131 | esd, pad, thermal, pcb |
| 39 | False / Display Name / Advanced True | 128 | false, display_name, advanced true, tool_mode |
| 42 | Childitem / Pictures / Moved Pictures | 124 | childitem, pictures, moved pictures, screenshots screenshot |
| 54 | Council / Security Council / Shall | 108 | council, security council, shall, article |
| 60 | Idtofile / Cid / Incode | 103 | idtofile, cid, incode, clean clean |
| 61 | Bacteria / Bya / Ocean | 103 | bacteria, bya, ocean, oxygen |
| 66 | States America / United States / Country United | 100 | states america, united states, country united, america |
| 67 | Qemu / Pve Qemu / Pve | 99 | qemu, pve qemu, pve, hw |
| 74 | Pages / Brother / Scanner | 95 | pages, brother, scanner, scan |
| 76 | United Kingdom / Kingdom / Country United | 93 | united kingdom, kingdom, country united, united |
| 78 | 753 Country / Index 753 / 753 | 92 | 753 country, index 753, 753, index |
| 80 | Mastering / Eq / Diy | 92 | mastering, eq, diy, sontec |
| 81 | Philippines / Index / Democracy Index | 92 | philippines, index, democracy index, democracy |
| 83 | 901 Free / Index 901 / 901 | 91 | 901 free, index 901, 901, 099 political |
| 86 | South Africa / Africa / Country South | 90 | south africa, africa, country south, south |
| 90 | 576 Free / Index 576 / 591 Political | 88 | 576 free, index 576, 591 political, 576 |

## Integration

Each macro-chip has a centroid embedding (768-dim) for semantic routing:
1. When a query arrives, embed it with all-MiniLM-L6-v2
2. Compute cosine similarity against each chip centroid
3. Activate chips above threshold (e.g., > 0.35)
4. Inject activated chip's context into the LLM prompt