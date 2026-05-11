import json, subprocess, os, sys

session = os.environ.get("BW_SESSION", "")
if not session:
    print("ERROR: BW_SESSION not set. Run: bwu")
    sys.exit(1)

def bw(args):
    result = subprocess.run(
        ["bw"] + args + ["--session", session],
        capture_output=True, text=True
    )
    return result

def bw_json(args):
    result = bw(args)
    if result.returncode != 0:
        print(f"ERROR: {result.stderr}")
        return None
    return json.loads(result.stdout)

# Step 1 — Create folders
FOLDERS = [
    "Infrastructure",
    "Audio Production",
    "Tom Cat Business",
    "Financial — Active",
    "Gaming",
    "Streaming",
    "Education",
    "Personal",
    "Crypto",
    "Archive — Bankruptcy Hold",
    "_Delete Me",
]

print("Creating folders...")
folder_map = {}

existing = bw_json(["list", "folders"])
for f in existing:
    folder_map[f["name"]] = f["id"]

for name in FOLDERS:
    if name in folder_map:
        print(f"  EXISTS: {name}")
        continue
    encoded = subprocess.run(
        ["bw", "encode"],
        input=json.dumps({"name": name}),
        capture_output=True, text=True
    ).stdout.strip()
    result = bw(["create", "folder", encoded])
    if result.returncode == 0:
        folder_id = json.loads(result.stdout)["id"]
        folder_map[name] = folder_id
        print(f"  CREATED: {name} ({folder_id})")
    else:
        print(f"  FAILED: {name} — {result.stderr}")

# Step 2 — Load all items
print("\nLoading vault items...")
items = bw_json(["list", "items"])
print(f"Total items: {len(items)}")

# Step 3 — Category rules
RULES = {
    "Infrastructure": [
        "github", "docker", "ui.com", "quickconnect", "tailscale",
        "synology", "unifi", "192.168", "192.158", "10.0.0",
        "100.79", "127.0.0", "localhost", "fe80", "linode",
        "vscyberhosting", "account.mapbox", "account.ui",
    ],
    "Audio Production": [
        "sweetwater", "reverb.com", "waves.com", "plugin-alliance",
        "uaudio", "antelope", "puremix", "adam-audio", "softube",
        "audionews", "acoustica", "vintageking", "stewmac",
        "tubesandmore", "lancasteraudio", "registration.namm",
        "geartrade", "jetcitycustom",
    ],
    "Tom Cat Business": [
        "freshbooks", "tomcatproductions", "waveapps",
    ],
    "Financial — Active": [
        "sofi", "paypal", "studentaid", "wellsfargo",
    ],
    "Archive — Bankruptcy Hold": [
        "creditkarma", "synchrony", "cfna", "chase", "klarna",
        "bankofamerica", "citi", "turbotax", "hrblock", "principal",
        "premera", "cigna", "caremark", "benefitsolver",
    ],
    "Gaming": [
        "steam", "epicgames", "battle.net", "riotgames", "nintendo",
        "ea.com", "warframe", "nexusmods", "pathofexile", "gearbox",
        "ubisoft", "roll20", "arena.net", "blizzard", "dauntless",
        "wizards", "square-enix", "kinguin", "skyrimnexus",
    ],
    "Streaming": [
        "netflix", "hulu", "spotify", "twitch", "sling", "plex",
        "pandora", "soundcloud", "roku", "curiositystream", "crunchyroll",
    ],
    "Education": [
        "vcccd.edu", "csun.edu", "edx", "khanacademy", "udemy",
        "coursera", "netacad", "teachable", "sololearn", "study.com",
        "pearsonvue", "umassglobal", "scratch.mit", "openccc",
    ],
    "Crypto": [
        "coinbase", "tradingview", "bittrex", "minergate", "pooledbits",
        "poloniex", "simplefx", "coinmine", "blocksfactory",
        "webxass", "dgb-groestl",
    ],
    "_Delete Me": [
        "funimation", "vrv.co", "gfycat", "dcuniverse", "dreamspark",
        "harmontown", "ticketfly", "getnugg", "weedmaps", "cougarlife",
        "sugardaddy", "mousemingle", "oursecret.com", "adultfriendfinder",
        "maiotaku", "aeriagames", "idp.amazon.work", "taleo.net",
        "icims.com", "myworkdayjobs", "peopleanswers", "jibeapply",
        "rayjobs", "elwoodstaffing", "manpower.com", "sterlingdirect",
        "bestbuy.dtdeals", "extrasforamazon", "doge.pool", "webxass",
        "amdrewards", "e-rewards", "walmartgift", "mytestcom",
        "textem.net", "dreamteam.gg", "tapplatform",
    ],
}

# Step 4 — Assign folders
print("\nAssigning folders...")
moved = 0
skipped = 0
already = 0

for item in items:
    name = item.get("name", "").lower()
    current_folder = item.get("folderId")
    target_folder = None

    for folder_name, keywords in RULES.items():
        if any(k in name for k in keywords):
            target_folder = folder_name
            break

    if target_folder is None:
        target_folder = "Personal"

    target_id = folder_map.get(target_folder)
    if not target_id:
        skipped += 1
        continue

    if current_folder == target_id:
        already += 1
        continue

    # Update item folder
    item["folderId"] = target_id
    encoded = subprocess.run(
        ["bw", "encode"],
        input=json.dumps(item),
        capture_output=True, text=True
    ).stdout.strip()

    result = bw(["edit", "item", item["id"], encoded])
    if result.returncode == 0:
        moved += 1
        print(f"  → {target_folder}: {item.get('name')}")
    else:
        print(f"  FAIL: {item.get('name')} — {result.stderr.strip()}")

# Step 5 — Sync
print(f"\nMoved: {moved} | Already correct: {already} | Skipped: {skipped}")
print("Syncing vault...")
bw(["sync"])
print("Done.")
