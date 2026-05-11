import json, sys, subprocess, os

session = os.environ.get("BW_SESSION", "")
result = subprocess.run(
    ["bw", "list", "items", "--session", session],
    capture_output=True, text=True
)
items = json.loads(result.stdout)

categories = {
    "INFRASTRUCTURE": ["github", "docker", "ui.com", "quickconnect", "tailscale",
                       "grafana", "synology", "unifi", "192.168", "192.158", "10.0.0",
                       "100.79", "127.0.0", "localhost", "fe80", "linode", "vscyber"],
    "AUDIO_PRODUCTION": ["sweetwater", "reverb.com", "waves", "plugin-alliance", "uaudio",
                         "antelope", "puremix", "adam-audio", "softube", "audionews",
                         "acoustica", "vintageking", "stewmac", "tubesandmore", "lancaster"],
    "CRYPTO_DEAD": ["bittrex", "minergate", "pooledbits", "webxass", "coinmine",
                    "blocksfactory", "simplefx", "poloniex", "dgb", "doge.pool"],
    "CRYPTO_ACTIVE": ["coinbase", "tradingview"],
    "DEAD_SERVICES": ["funimation", "vrv.co", "gfycat", "dcuniverse", "dreamspark",
                      "harmontown", "ticketfly", "getnugg", "weedmaps", "cougarlife",
                      "sugardaddy", "mousemingle", "oursecret", "adultfriendfinder",
                      "maiotaku", "aeriagames"],
    "JOB_HUNTING": ["taleo.net", "icims.com", "myworkdayjobs", "peopleanswers",
                    "jibeapply", "rayjobs", "elwoodstaffing", "manpower", "workday",
                    "governmentjobs", "indeed", "sterling"],
    "GAMING": ["steam", "epicgames", "battle.net", "riotgames", "nintendo", "ea.com",
               "warframe", "nexusmods", "pathofexile", "gearbox", "ubisoft", "roll20",
               "arena.net", "blizzard", "dauntless", "wizards"],
    "FINANCIAL": ["paypal", "chase", "wellsfargo", "coinbase", "creditkarma", "sofi",
                  "synchrony", "cfna", "klarna", "bankofamerica", "principal",
                  "studentaid", "turbotax", "hrblock"],
    "STREAMING": ["netflix", "hulu", "spotify", "twitch", "sling", "plex", "pandora",
                  "crunchyroll", "curiosity", "soundcloud", "roku"],
    "TOMCAT_BUSINESS": ["freshbooks", "reverb.com", "tomcatproductions", "geartrade",
                        "lancasteraudio", "registration.namm"],
}

assigned = {}
unassigned = []

for item in items:
    name = item.get("name", "").lower()
    found = False
    for cat, keywords in categories.items():
        if any(k in name for k in keywords):
            assigned.setdefault(cat, []).append(item.get("name"))
            found = True
            break
    if not found:
        unassigned.append(item.get("name"))

print(f"TOTAL: {len(items)} items\n")
for cat, names in sorted(assigned.items()):
    print(f"\n=== {cat} ({len(names)}) ===")
    for n in sorted(names):
        print(f"  {n}")

print(f"\n=== UNCATEGORIZED ({len(unassigned)}) ===")
for n in sorted(unassigned):
    print(f"  {n}")
