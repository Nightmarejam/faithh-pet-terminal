# WINDSURF CONTINUATION — NAS + FAITHH Hats
# March 14, 2026
# Pick up from where the NAS reorganization session left off

## WHAT WAS COMPLETED (do not redo)
- legal_tax_db downloaded to /mnt/x/AI/legal_tax_db/ (30 files, 4,512 chunks indexed)
- #recycle emptied (23GB freed)
- qdrant_backup deleted
- staging/venv-archives deleted
- Old NAS scripts deleted
- New folder structure created: projects/ knowledge/ infrastructure/ assets/
- Oregon Annual Report status confirmed: ACTIVE, renewal DUE MARCH 19

## IMMEDIATE — Oregon Annual Report (do this first, 2 minutes)
The annual report needs to be FILED (not just checked).
Fee: $100 at https://sos.oregon.gov/business/pages/renew.aspx
Jonathan must file this manually (requires login + payment).
ACTION: Create a reminder file so he sees it immediately:
  Write to: /mnt/x/TomCatSound_LLC/01_Annual_Filings/URGENT_FILE_BY_MARCH_19.txt
  Content: "URGENT: File 2026 Oregon Annual Report by March 19, 2026. Fee: $100. URL: https://sos.oregon.gov/business/pages/renew.aspx Registry: 2242571-96"

## TASK A — Fix p535 PDF (quick fix)
p535_business_expenses.pdf failed extraction ("No /Root object" — corrupted download).
Re-download and re-index:
  url = "https://www.irs.gov/pub/irs-pdf/p535.pdf"
  save to /mnt/x/AI/legal_tax_db/federal_irs/p535_business_expenses.pdf (overwrite)
  extract with pdfplumber and index ~200 chunks into faithh_knowledge_base
  category: "irs_pub", hat: "tax_personal,tax_partnership"

## TASK B — Create FAITHH Hat Files
Location: ~/ai-stack/faithh/hats/ (create dir if missing)

Create these 6 files (keep them concise — 10-15 lines each):

hat_tax_personal.md:
  Purpose: Personal income tax questions (Form 1040, Schedule E K-1 income, Oregon OR-40)
  ChromaDB filter: category IN (irs_pub, oregon_tax)
  Example queries: "how do I report partnership loss on my 1040", "what is Schedule E",
    "Oregon personal income tax rate", "self-employment tax calculation"
  Instruction: Always cite specific publication number and section.

hat_tax_partnership.md:
  Purpose: Partnership tax questions (Form 1065, K-1, Pub 541, OR-65, penalty abatement)
  ChromaDB filter: category IN (irs_pub, oregon_tax)
  Example queries: "how to file Form 1065 late", "what is Rev Proc 84-35",
    "Section 179 depreciation election", "multi-state partnership K-1"
  Instruction: Always cite IRS pub or ORS section. Note Tom Cat Sound LLC context.

hat_music_copyright.md:
  Purpose: Music law for Floating Garden Soundworks label (copyright, licensing, ownership)
  ChromaDB filter: category IN (music_law, federal_law)
  Example queries: "who owns a master recording", "mechanical license for covers",
    "sound recording vs musical composition copyright", "artist agreement basics"

hat_business_law.md:
  Purpose: Oregon LLC law, operating agreements, member rights, contracts
  ChromaDB filter: category IN (oregon_tax, federal_law)
  Example queries: "Oregon LLC member withdrawal", "ORS 63 operating agreement requirements",
    "member dissociation process", "single member vs multi-member LLC"

hat_zoning.md:
  Purpose: Albany OR and Linn County zoning for home studio / commercial use
  ChromaDB filter: category = albany_zoning
  Example queries: "can I run a recording studio from home in Albany OR",
    "home occupation permit requirements", "commercial use in residential zone"
  Note: Albany zoning not yet indexed — respond with general Oregon guidance until available.

hat_land_use.md:
  Purpose: Oregon statewide land use planning, rural property, permaculture projects
  ChromaDB filter: category = land_use
  Example queries: "farm zone restrictions Oregon", "rural residential land use",
    "ORS 215 exceptions for small farms", "statewide planning goal 3"

## TASK C — Learning Portal Reorganization
The learning_portal folder has 177GB of books/courses from 2020.
Location: /mnt/x/learning_portal/Learning Portal/

Step 1: Get full folder list (do NOT move files yet):
  find '/mnt/x/learning_portal/Learning Portal' -maxdepth 1 -type d
  Save output to /mnt/x/knowledge/LEARNING_PORTAL_INVENTORY.txt

Step 2: Categorize into the new knowledge/ subfolders:
  programming/     → Java, Python, PHP, C++, Linux, networking, security books
  business/        → life skills, rules for writers, memory books
  knowledge/       → Japanese language pack, French collection, math books
  (keep cosplay, fitness as-is in a misc/ subfolder for now)

Step 3: Move (do NOT copy — NAS space matters):
  Move each folder from learning_portal/ to appropriate knowledge/ subfolder
  Use mv not cp

Step 4: After moving, check if learning_portal is empty → delete it

Step 5: Save reorganization map to:
  /mnt/x/knowledge/REORGANIZATION_LOG.md
  (what moved where, date, counts)

## TASK D — Archives Review (DO NOT DELETE — just report)
/mnt/x/archives/ is 108GB. Before touching it:
  Get top-level folder list and sizes
  Save to /mnt/x/ARCHIVES_INVENTORY.txt
  Flag anything that looks like a duplicate of backups/
  DO NOT delete anything — report findings only

## TASK E — Update SYSTEMS_MAP.md
After completing above tasks, update ~/ai-stack/SYSTEMS_MAP.md:
  - NAS section: note new X: folder structure, legal_tax_db location
  - FAITHH section: note 46,882 chunks, hat files created
  - Add note: learning_portal reorganized into knowledge/

## SUCCESS CRITERIA
- [ ] URGENT_FILE_BY_MARCH_19.txt created in TomCatSound_LLC/01_Annual_Filings/
- [ ] p535 re-downloaded and indexed
- [ ] 6 hat files created in ~/ai-stack/faithh/hats/
- [ ] Learning portal inventory saved
- [ ] Learning portal reorganized into knowledge/ subfolders
- [ ] Archives inventory saved (no deletions)
- [ ] SYSTEMS_MAP.md updated

## NOTES
- X: drive mounted at /mnt/x/ with full read/write from WSL
- Z: drive at /mnt/z/ is READ ONLY — do not attempt writes there
- Gen8 ChromaDB at 192.158.1.243:8000 — collection: faithh_knowledge_base
- DO NOT load SentenceTransformer in WSL (crashes WSL — see decisions_log.json infra_002)
- For large file operations on NAS, expect slow speeds (~50-100MB/s over SMB)
