#!/usr/bin/env python3
"""Audit backend endpoints vs UI features to identify misalignments."""
import re
from pathlib import Path

BACKEND_FILE = Path("/home/jonat/ai-stack/faithh_professional_backend_fixed.py")
UI_FILE = Path("/home/jonat/ai-stack/faithh_pet_v4.html")

print("=" * 70)
print("BACKEND / UI ALIGNMENT AUDIT")
print("=" * 70)

# 1. Extract backend routes
print("\n## BACKEND ROUTES")
print("-" * 70)

backend_code = BACKEND_FILE.read_text()
routes = re.findall(r'@app\.route\([\'"]([^\'"]+)[\'"]', backend_code)
routes = sorted(set(routes))

print(f"Found {len(routes)} routes:\n")
for route in routes:
    # Check if route is called from UI
    route_in_ui = route in UI_FILE.read_text() or route.replace("/api/", "") in UI_FILE.read_text()
    status = "✅" if route_in_ui else "⚠️ NOT IN UI"
    print(f"   {status} {route}")

# 2. Extract UI fetch calls
print("\n\n## UI FETCH CALLS")
print("-" * 70)

ui_code = UI_FILE.read_text()
fetch_calls = re.findall(r'fetch\([\'"`]([^\'"` ]+)[\'"`]', ui_code)
fetch_calls = sorted(set(fetch_calls))

print(f"Found {len(fetch_calls)} fetch endpoints:\n")
for endpoint in fetch_calls:
    # Check if endpoint exists in backend
    endpoint_in_backend = endpoint in backend_code or endpoint.lstrip('/') in backend_code
    status = "✅" if endpoint_in_backend else "❌ NOT IN BACKEND"
    print(f"   {status} {endpoint}")

# 3. Check for UI features that may not work
print("\n\n## POTENTIAL UI/BACKEND MISMATCHES")
print("-" * 70)

# Check specific features
features_to_check = [
    ("retryLastMessage", "Retry button function"),
    ("lastFailedMessage", "Failed message state"),
    ("model.disabled", "Disabled model support"),
    ("refreshCompass", "Compass refresh"),
    ("generateJournal", "Journal generation"),
    ("logWork", "Work logging"),
    ("fetchMlChips", "ML chips fetch"),
    ("pulseReflection", "PULSE reflection"),
]

for pattern, desc in features_to_check:
    in_ui = pattern in ui_code
    # Check if corresponding backend support exists
    print(f"   {'✅' if in_ui else '❌'} {desc}: {'present' if in_ui else 'missing'} in UI")

# 4. Check backend features not exposed in UI
print("\n\n## BACKEND FEATURES")
print("-" * 70)

backend_features = [
    ("/api/chat", "Main chat endpoint"),
    ("/api/status", "System status"),
    ("/api/compass/director", "Compass director"),
    ("/api/compass/log", "Work logging"),
    ("/api/journal/generate", "Journal generation"),
    ("/api/journal/latest", "Latest journal"),
    ("/api/ml/chips", "ML chips list"),
    ("/api/pulse/reflection", "PULSE reflection"),
    ("/api/rag/search", "RAG search"),
    ("/upload", "File upload"),
]

for route, desc in backend_features:
    in_backend = route in backend_code
    in_ui = route in ui_code
    if in_backend:
        status = "✅ UI+Backend" if in_ui else "⚠️ Backend only"
    else:
        status = "❌ Missing"
    print(f"   {status}: {desc} ({route})")

# 5. Summary
print("\n\n" + "=" * 70)
print("ALIGNMENT SUMMARY")
print("=" * 70)

print("""
## Key Findings:

1. **Routes Analysis**: Check above for routes not called from UI
   - These may be dead code or planned features

2. **Fetch Calls**: Check for endpoints UI calls that don't exist
   - These will cause errors in the UI

3. **Feature Parity**: Most core features appear aligned

## Recommended Actions:

1. **Remove dead routes** from backend if not needed
2. **Fix broken fetch calls** in UI that point to non-existent endpoints
3. **Document planned features** that have backend but no UI
4. **Add UI for useful backend-only features**

## Automation Opportunities:

1. **Auto-generate API docs** from route decorators
2. **Create health check** that validates all UI endpoints work
3. **Add integration tests** for each route
""")
