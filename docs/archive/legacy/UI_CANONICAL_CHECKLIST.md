# UI Canonical Smoke Checklist

- Load `http://localhost:5557/` and confirm the UI renders without blank sections.
- Open devtools console and confirm no blocking JS errors on first load.
- Verify `/api/status` populates status indicators (and that values update after refresh).
- Switch to the COMPASS tab and confirm `/api/compass` populates the dashboard without errors.
- Send a short chat and confirm `/api/chat` response renders correctly.
- Send a longer chat and confirm streaming/latency handling does not freeze the UI.
- Toggle RAG and confirm the request payload includes `use_rag` changes.
- Confirm RAG indicators (if shown) update when `ragEnabled` is toggled.
- Verify Pulse chips load from `/api/pulse/chips` and render without layout breakage.
- Trigger a backend error (stop server) and confirm the UI shows a clear error state.
- Re-enable backend and confirm recovery without a full page reload.
- Hit `/health` in a separate tab and confirm it returns `200` with expected payload.
- If the UI exposes upload controls, upload a small `.txt` and verify `/api/upload` succeeds.
- Confirm any image assets load from `/images/` without 404s.
- Confirm favicon loads from `/favicon.ico`.
- Check on mobile width that main chat input remains usable and status panel does not overlap.
