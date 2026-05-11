import json, subprocess, os, sys

session = os.environ.get("BW_SESSION", "")
if not session:
    print("ERROR: BW_SESSION not set. Run: export BW_SESSION=$(bw unlock --raw)")
    sys.exit(1)

# Confirmed dead — safe to delete without review
DEAD_KEYWORDS = [
    # Dead crypto
    "bittrex", "minergate", "pooledbits", "webxass", "coinmine",
    "blocksfactory", "simplefx", "poloniex", "dgb-groestl", "doge.pool",
    # Dead services  
    "funimation", "vrv.co", "gfycat", "dcuniverse", "dreamspark",
    "harmontown", "ticketfly", "getnugg", "weedmaps", "cougarlife",
    "sugardaddy", "mousemingle", "oursecret.com", "adultfriendfinder",
    "maiotaku", "aeriagames",
    # Dead job hunting
    "taleo.net", "icims.com", "myworkdayjobs", "peopleanswers",
    "jibeapply", "rayjobs.com", "elwoodstaffing", "manpower.com",
    "sterlingdirect", "governmentjobs.com",
    # Dead Amazon work portals
    "idp.amazon.work",
    # Old school
    "vcccd.edu", "csun.edu",
]

result = subprocess.run(
    ["bw", "list", "items", "--session", session],
    capture_output=True, text=True
)
items = json.loads(result.stdout)

to_delete = []
for item in items:
    name = item.get("name", "").lower()
    if any(k in name for k in DEAD_KEYWORDS):
        to_delete.append((item["id"], item.get("name", "?")))

print(f"Items to delete: {len(to_delete)}")
print()
for id_, name in sorted(to_delete, key=lambda x: x[1]):
    print(f"  {name}")

if "--dry-run" not in sys.argv:
    confirm = input(f"\nDelete {len(to_delete)} items? (yes/no): ")
    if confirm.lower() == "yes":
        for id_, name in to_delete:
            result = subprocess.run(
                ["bw", "delete", "item", id_, "--session", session],
                capture_output=True, text=True
            )
            status = "OK" if result.returncode == 0 else f"FAIL: {result.stderr.strip()}"
            print(f"  [{status}] {name}")
        
        # Sync after deletes
        subprocess.run(["bw", "sync", "--session", session])
        print("\nDone. Vault synced.")
    else:
        print("Cancelled.")
else:
    print("\n(dry run — no changes made)")
