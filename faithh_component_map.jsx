import { useState } from "react";

const COMPONENTS = {
  inputs: [
    { id: "claude_json", label: "Claude Exports", sub: "3× conversations.json", size: "144MB", format: "JSON", color: "#e8a87c" },
    { id: "chatgpt_json", label: "ChatGPT Exports", sub: "4× conversations*.json", size: "182MB", format: "JSON", color: "#e8a87c" },
    { id: "grok_dir", label: "Grok Exports", sub: "extracted/ directory", size: "19MB", format: "Mixed", color: "#e8a87c" },
    { id: "windsurf_md", label: "Windsurf Exports", sub: "5 .md files", size: "804KB", format: "Markdown", color: "#e8a87c" },
    { id: "cursor_md", label: "Cursor Exports", sub: "3 .md files", size: "696KB", format: "Markdown", color: "#e8a87c" },
  ],
  parsers: [
    { id: "parse_claude", label: "parse_claude_conversations()", sub: "+ parse_claude_projects()", mem: "~50MB", returns: "list[NormalizedConversation]", color: "#7eb8d4" },
    { id: "parse_chatgpt", label: "parse_chatgpt_conversations()", sub: "deduplicates by conv_id", mem: "~120MB", returns: "list[NormalizedConversation]", color: "#7eb8d4" },
    { id: "parse_grok", label: "parse_grok_conversations()", sub: "walks extracted/ dir", mem: "~30MB", returns: "list[NormalizedConversation]", color: "#7eb8d4" },
    { id: "parse_md", label: "collect_markdown_dir()", sub: "windsurf + cursor", mem: "~5MB", returns: "list[NormalizedConversation]", color: "#7eb8d4" },
  ],
  orchestration: [
    { id: "iter_conv", label: "iter_conversations()", sub: "generator — yields one conv at a time\ngc.collect() between providers", mem: "O(1) accumulation", color: "#9b8ec4", impedance: "✓ Fixed Apr 2026" },
    { id: "iter_chunks", label: "iter_chunks()", sub: "yields one chunk at a time\nattaches metadata per chunk", mem: "O(1) accumulation", color: "#9b8ec4", impedance: "✓ Fixed Apr 2026" },
    { id: "chunk_conv", label: "chunk_conversation()", sub: "chunk_size=1200, overlap=150\nfilters <50 char messages", mem: "O(conv size)", color: "#9b8ec4" },
  ],
  embed: [
    { id: "ef", label: "SentenceTransformerEmbeddingFunction", sub: "model: all-MiniLM-L6-v2\ndevice: cpu (recommended)\n384-dim vectors", mem: "~761MB init", color: "#7ec4a0", impedance: "⚠ CUDA init = +45GB RES (avoid)" },
  ],
  transport: [
    { id: "chroma_client", label: "chromadb.HttpClient", sub: "host: 192.158.1.243:8000\nLAN path (not Tailscale)\nbatch_size=25", mem: "~50MB", color: "#d4a07e", impedance: "⚠ batch_size vs throughput tradeoff" },
    { id: "flush_batch", label: "flush_batch()", sub: "upserts ids + documents + metadatas\nclears batch after each flush", mem: "O(batch_size)", color: "#d4a07e" },
  ],
  storage: [
    { id: "chroma_db", label: "ChromaDB (Gen8)", sub: "faithh_knowledge_base\n~25K docs target\n192.158.1.243:8000", mem: "On Gen8 (separate host)", color: "#c47e7e" },
    { id: "other_cols", label: "Other Collections", sub: "governance_corpus: 18,768\nalife_lineage: 339,900\nfaithh_session_metrics: 7", mem: "Do NOT delete", color: "#c47e7e" },
  ],
};

const IMPEDANCE_BLOCKS = [
  {
    id: "ib1",
    title: "IB-1: CUDA Device Init",
    severity: "high",
    location: "Embed Layer",
    symptom: "45GB RES even for tiny model",
    cause: "PyTorch CUDA runtime maps GPU memory into process address space on init, even if GPU is never used for inference",
    fix: "Always use --embed-device cpu for all-MiniLM-L6-v2. Model is 90MB — CPU inference is fast enough.",
    status: "mitigated",
  },
  {
    id: "ib2",
    title: "IB-2: Corpus Accumulation",
    severity: "high",
    location: "Orchestration Layer",
    symptom: "47GB VIRT, OOM on 16GB WSL",
    cause: "Original gather_conversations() + all_chunks list loaded entire corpus before first upsert",
    fix: "Replaced with iter_conversations() + iter_chunks() streaming generators. gc.collect() between providers.",
    status: "fixed",
  },
  {
    id: "ib3",
    title: "IB-3: WSL Memory Cap",
    severity: "high",
    location: "Infrastructure",
    symptom: "OOM at 8GB even with 64GB physical RAM",
    cause: "No .wslconfig — WSL2 defaulted to 50% of physical RAM (8GB)",
    fix: "Created .wslconfig: memory=48GB, swap=16GB, processors=12",
    status: "fixed",
  },
  {
    id: "ib4",
    title: "IB-4: IDE Memory Competition",
    severity: "medium",
    location: "Infrastructure",
    symptom: "Indexer OOMs even with streaming fix",
    cause: "Cursor language server consumes 20-28GB RES on ai-stack workspace, runs inside WSL",
    fix: "Operational rule: close Cursor/Windsurf before indexing. IDE and indexer cannot coexist on 48GB.",
    status: "operational",
  },
  {
    id: "ib5",
    title: "IB-5: Tailscale vs LAN",
    severity: "low",
    location: "Transport Layer",
    symptom: "Unnecessary VPN overhead for local ChromaDB",
    cause: ".env hardcoded Tailscale IP (100.79.85.32) instead of LAN IP",
    fix: "Updated .env to 192.158.1.243. Added gen8 to /etc/hosts.",
    status: "fixed",
  },
  {
    id: "ib6",
    title: "IB-6: Collection EF Conflict",
    severity: "medium",
    location: "Storage Layer",
    symptom: "ValueError on get_collection() after recreation",
    cause: "Collection created with 'default' EF, script passed 'sentence_transformer' EF",
    fix: "Changed to get_or_create_collection() with metadata={dimension:768}",
    status: "fixed",
  },
  {
    id: "ib7",
    title: "IB-7: Residual 46GB RES",
    severity: "medium",
    location: "Unknown — under investigation",
    symptom: "RES climbs to ~46GB during indexing run and plateaus",
    cause: "Not CUDA init (867MB). Not Python heap (247MB tracemalloc). Not source file size (total <500MB). Likely PyTorch internal allocator pool or ChromaDB client response buffering.",
    fix: "Open — block-by-block profiling needed. System completes without OOM on 48GB config.",
    status: "open",
  },
];

const severityColor = { high: "#c47e7e", medium: "#d4a07e", low: "#7eb8d4" };
const statusColor = { fixed: "#7ec4a0", mitigated: "#9b8ec4", operational: "#7eb8d4", open: "#c47e7e" };
const statusLabel = { fixed: "FIXED", mitigated: "MITIGATED", operational: "OPERATIONAL", open: "OPEN" };

export default function FAITHHMap() {
  const [selected, setSelected] = useState(null);
  const [activeTab, setActiveTab] = useState("map");

  const selectedIB = IMPEDANCE_BLOCKS.find(b => b.id === selected);

  return (
    <div style={{
      background: "#0d1117",
      minHeight: "100vh",
      fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
      color: "#c9d1d9",
      padding: "24px",
    }}>
      {/* Header */}
      <div style={{ marginBottom: 24, borderBottom: "1px solid #21262d", paddingBottom: 16 }}>
        <div style={{ display: "flex", alignItems: "baseline", gap: 16 }}>
          <h1 style={{ margin: 0, fontSize: 22, color: "#e6edf3", letterSpacing: "-0.5px" }}>
            FAITHH
          </h1>
          <span style={{ fontSize: 13, color: "#8b949e" }}>Indexer Component Map — Apr 2026</span>
        </div>
        <div style={{ display: "flex", gap: 8, marginTop: 14 }}>
          {["map", "impedance"].map(tab => (
            <button key={tab} onClick={() => setActiveTab(tab)} style={{
              background: activeTab === tab ? "#21262d" : "transparent",
              border: `1px solid ${activeTab === tab ? "#30363d" : "transparent"}`,
              color: activeTab === tab ? "#e6edf3" : "#8b949e",
              padding: "5px 14px",
              borderRadius: 6,
              cursor: "pointer",
              fontSize: 12,
              letterSpacing: "0.5px",
              textTransform: "uppercase",
            }}>
              {tab === "map" ? "Signal Chain" : `Impedance Blocks (${IMPEDANCE_BLOCKS.length})`}
            </button>
          ))}
        </div>
      </div>

      {activeTab === "map" && (
        <div>
          {[
            { key: "inputs", label: "INPUT LAYER", desc: "Export files on disk — source of truth" },
            { key: "parsers", label: "PARSE LAYER", desc: "Provider-specific parsers → NormalizedConversation" },
            { key: "orchestration", label: "ORCHESTRATION LAYER", desc: "Generators — streaming pipeline" },
            { key: "embed", label: "EMBED LAYER", desc: "Client-side vector generation" },
            { key: "transport", label: "TRANSPORT LAYER", desc: "HTTP batching to Gen8" },
            { key: "storage", label: "STORAGE LAYER", desc: "ChromaDB collections on Gen8" },
          ].map(({ key, label, desc }) => (
            <div key={key} style={{ marginBottom: 20 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
                <span style={{ fontSize: 10, letterSpacing: "1.5px", color: "#8b949e" }}>{label}</span>
                <div style={{ flex: 1, height: 1, background: "#21262d" }} />
                <span style={{ fontSize: 11, color: "#484f58" }}>{desc}</span>
              </div>
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                {COMPONENTS[key].map(c => (
                  <div key={c.id} style={{
                    background: "#161b22",
                    border: `1px solid ${c.impedance ? "#30363d" : "#21262d"}`,
                    borderLeft: `3px solid ${c.color}`,
                    borderRadius: 6,
                    padding: "10px 14px",
                    minWidth: 200,
                    flex: "1 1 200px",
                    maxWidth: 280,
                  }}>
                    <div style={{ fontSize: 12, color: "#e6edf3", fontWeight: 600, marginBottom: 4 }}>{c.label}</div>
                    <div style={{ fontSize: 11, color: "#8b949e", whiteSpace: "pre-line", marginBottom: 6 }}>{c.sub}</div>
                    {c.size && <div style={{ fontSize: 10, color: "#484f58" }}>disk: {c.size} · {c.format}</div>}
                    {c.mem && <div style={{ fontSize: 10, color: "#484f58" }}>mem: {c.mem}</div>}
                    {c.returns && <div style={{ fontSize: 10, color: "#484f58" }}>→ {c.returns}</div>}
                    {c.impedance && (
                      <div style={{
                        marginTop: 6,
                        fontSize: 10,
                        color: c.impedance.startsWith("✓") ? "#7ec4a0" : "#d4a07e",
                        borderTop: "1px solid #21262d",
                        paddingTop: 4,
                      }}>{c.impedance}</div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}

          {/* Flow arrows summary */}
          <div style={{
            marginTop: 16,
            background: "#161b22",
            border: "1px solid #21262d",
            borderRadius: 8,
            padding: 16,
            fontSize: 11,
            color: "#8b949e",
            lineHeight: "1.8",
          }}>
            <div style={{ color: "#e6edf3", marginBottom: 8, fontSize: 12 }}>Signal Flow</div>
            <code style={{ color: "#7eb8d4" }}>Export files</code>
            <span style={{ color: "#484f58" }}> → </span>
            <code style={{ color: "#7eb8d4" }}>parse_*() per provider</code>
            <span style={{ color: "#484f58" }}> → </span>
            <code style={{ color: "#9b8ec4" }}>iter_conversations() generator</code>
            <span style={{ color: "#484f58" }}> → </span>
            <code style={{ color: "#9b8ec4" }}>iter_chunks() generator</code>
            <span style={{ color: "#484f58" }}> → </span>
            <code style={{ color: "#7ec4a0" }}>SentenceTransformer (CPU)</code>
            <span style={{ color: "#484f58" }}> → </span>
            <code style={{ color: "#d4a07e" }}>flush_batch() × N</code>
            <span style={{ color: "#484f58" }}> → </span>
            <code style={{ color: "#c47e7e" }}>ChromaDB LAN 192.158.1.243:8000</code>
          </div>
        </div>
      )}

      {activeTab === "impedance" && (
        <div style={{ display: "flex", gap: 16 }}>
          {/* List */}
          <div style={{ width: 280, flexShrink: 0 }}>
            {IMPEDANCE_BLOCKS.map(ib => (
              <div key={ib.id} onClick={() => setSelected(selected === ib.id ? null : ib.id)}
                style={{
                  background: selected === ib.id ? "#161b22" : "transparent",
                  border: `1px solid ${selected === ib.id ? "#30363d" : "#21262d"}`,
                  borderLeft: `3px solid ${severityColor[ib.severity]}`,
                  borderRadius: 6,
                  padding: "10px 12px",
                  marginBottom: 8,
                  cursor: "pointer",
                  transition: "all 0.15s",
                }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontSize: 12, color: "#e6edf3", fontWeight: 600 }}>{ib.title}</span>
                  <span style={{
                    fontSize: 9,
                    letterSpacing: "0.8px",
                    padding: "2px 6px",
                    borderRadius: 4,
                    background: statusColor[ib.status] + "22",
                    color: statusColor[ib.status],
                  }}>{statusLabel[ib.status]}</span>
                </div>
                <div style={{ fontSize: 10, color: "#8b949e", marginTop: 4 }}>{ib.location}</div>
              </div>
            ))}
          </div>

          {/* Detail */}
          <div style={{ flex: 1 }}>
            {selectedIB ? (
              <div style={{
                background: "#161b22",
                border: "1px solid #30363d",
                borderLeft: `3px solid ${severityColor[selectedIB.severity]}`,
                borderRadius: 8,
                padding: 20,
              }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
                  <div>
                    <div style={{ fontSize: 16, color: "#e6edf3", fontWeight: 700 }}>{selectedIB.title}</div>
                    <div style={{ fontSize: 11, color: "#8b949e", marginTop: 4 }}>{selectedIB.location}</div>
                  </div>
                  <span style={{
                    fontSize: 10,
                    letterSpacing: "0.8px",
                    padding: "4px 10px",
                    borderRadius: 4,
                    background: statusColor[selectedIB.status] + "22",
                    color: statusColor[selectedIB.status],
                    border: `1px solid ${statusColor[selectedIB.status]}44`,
                  }}>{statusLabel[selectedIB.status]}</span>
                </div>

                {[
                  { label: "SYMPTOM", value: selectedIB.symptom, color: "#d4a07e" },
                  { label: "ROOT CAUSE", value: selectedIB.cause, color: "#c47e7e" },
                  { label: "FIX / MITIGATION", value: selectedIB.fix, color: "#7ec4a0" },
                ].map(({ label, value, color }) => (
                  <div key={label} style={{ marginBottom: 14 }}>
                    <div style={{ fontSize: 9, letterSpacing: "1.5px", color: "#484f58", marginBottom: 4 }}>{label}</div>
                    <div style={{
                      fontSize: 12,
                      color: "#c9d1d9",
                      background: "#0d1117",
                      border: `1px solid ${color}33`,
                      borderLeft: `2px solid ${color}`,
                      borderRadius: 4,
                      padding: "8px 12px",
                      lineHeight: "1.6",
                    }}>{value}</div>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                height: 200,
                color: "#484f58",
                fontSize: 12,
                border: "1px dashed #21262d",
                borderRadius: 8,
              }}>
                Select an impedance block to inspect
              </div>
            )}

            {/* Legend */}
            <div style={{ display: "flex", gap: 16, marginTop: 16 }}>
              {Object.entries(severityColor).map(([s, c]) => (
                <div key={s} style={{ display: "flex", alignItems: "center", gap: 6 }}>
                  <div style={{ width: 10, height: 10, borderRadius: 2, background: c }} />
                  <span style={{ fontSize: 10, color: "#8b949e", textTransform: "uppercase", letterSpacing: "0.5px" }}>{s}</span>
                </div>
              ))}
              <div style={{ flex: 1 }} />
              {Object.entries(statusColor).map(([s, c]) => (
                <div key={s} style={{ display: "flex", alignItems: "center", gap: 6 }}>
                  <div style={{ width: 8, height: 8, borderRadius: "50%", background: c }} />
                  <span style={{ fontSize: 10, color: "#8b949e" }}>{statusLabel[s]}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
