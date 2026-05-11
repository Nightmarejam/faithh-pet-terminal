"""
FAITHH Professional Backend
Port: 5557
LLM: Groq (primary), vLLM @ 192.158.1.100:8000 (fallback)
Vector DB: ChromaDB @ 192.158.1.10:8000
Embeddings: BGE (sentence-transformers) — never use query_texts= directly
Collection: faithh_knowledge_base
"""

import os
import logging
import time
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer
from groq import Groq
import requests

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("faithh")

# ── Config ────────────────────────────────────────────────────────────────────
load_dotenv(os.path.expanduser("~/ai-stack/.env"))

BACKEND_PORT     = int(os.getenv("BACKEND_PORT", 5557))
CHROMA_HOST      = os.getenv("CHROMA_HOST", "192.158.1.10")
CHROMA_PORT      = int(os.getenv("CHROMA_PORT", 8000))
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "faithh_knowledge_base")
GROQ_API_KEY     = os.getenv("GROQ_API_KEY", "")
GROQ_TIMEOUT_S   = int(os.getenv("GROQ_TIMEOUT_S", 120))
VLLM_URL         = "http://192.158.1.100:8000/v1/chat/completions"
VLLM_MODEL       = "default"          # adjust to whatever model vLLM is serving
GROQ_MODEL       = "llama-3.3-70b-versatile"  # fast, large context; swap as needed
N_RESULTS        = 5                  # ChromaDB top-k

# ── Embeddings (BGE) ──────────────────────────────────────────────────────────
log.info("Loading BGE embedding model…")
embedder = SentenceTransformer("BAAI/bge-base-en-v1.5")
log.info("BGE model ready.")

# ── ChromaDB ──────────────────────────────────────────────────────────────────
log.info("Connecting to ChromaDB @ %s:%s", CHROMA_HOST, CHROMA_PORT)
chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
collection = chroma_client.get_collection(CHROMA_COLLECTION)
log.info("ChromaDB connected — collection '%s'", CHROMA_COLLECTION)

# ── Groq client ───────────────────────────────────────────────────────────────
groq_client = Groq(api_key=GROQ_API_KEY, timeout=GROQ_TIMEOUT_S)

# ── Flask app ─────────────────────────────────────────────────────────────────
app = Flask(__name__)


# ── Helpers ───────────────────────────────────────────────────────────────────

def embed(text: str) -> list[float]:
    """Embed a single string with BGE. Prepend retrieval prefix as recommended."""
    return embedder.encode(f"Represent this sentence for searching relevant passages: {text}").tolist()


def retrieve_context(query: str) -> str:
    """Query ChromaDB and return concatenated context snippets."""
    try:
        query_embedding = embed(query)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=N_RESULTS,
            include=["documents"],
        )
        docs = results.get("documents", [[]])[0]
        if not docs:
            return ""
        return "\n\n---\n\n".join(docs)
    except Exception as exc:
        log.warning("ChromaDB retrieval failed: %s", exc)
        return ""


def call_groq(system: str, user: str) -> str:
    """Send a chat completion to Groq. Raises on failure."""
    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
    )
    return response.choices[0].message.content


def call_vllm(system: str, user: str) -> str:
    """Fallback: send a chat completion to local vLLM."""
    payload = {
        "model": VLLM_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
    }
    resp = requests.post(VLLM_URL, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def build_prompt(context: str, message: str) -> tuple[str, str]:
    """Return (system_prompt, user_message)."""
    system = (
        "You are FAITHH — a knowledgeable, thoughtful assistant. "
        "Use the retrieved context below to ground your answer. "
        "If the context is not relevant, say so and answer from general knowledge.\n\n"
        f"=== Retrieved Context ===\n{context}\n========================="
        if context
        else
        "You are FAITHH — a knowledgeable, thoughtful assistant. "
        "No relevant context was retrieved; answer from general knowledge."
    )
    return system, message


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "faithh-backend", "port": BACKEND_PORT}), 200


@app.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({"error": "message field is required and must not be empty"}), 400

    t0 = time.monotonic()

    # 1. Retrieve context
    context = retrieve_context(message)
    log.info("Retrieved context (%d chars) for: %s…", len(context), message[:60])

    # 2. Build prompts
    system_prompt, user_message = build_prompt(context, message)

    # 3. Try Groq → fallback to vLLM
    source = "groq"
    try:
        reply = call_groq(system_prompt, user_message)
        log.info("Groq replied in %.2fs", time.monotonic() - t0)
    except Exception as groq_err:
        log.warning("Groq failed (%s) — trying vLLM fallback", groq_err)
        source = "vllm"
        try:
            reply = call_vllm(system_prompt, user_message)
            log.info("vLLM replied in %.2fs", time.monotonic() - t0)
        except Exception as vllm_err:
            log.error("Both LLMs failed. Groq: %s | vLLM: %s", groq_err, vllm_err)
            return jsonify({"error": "Both Groq and vLLM are unavailable", "detail": str(vllm_err)}), 503

    elapsed = round(time.monotonic() - t0, 3)
    return jsonify({
        "response": reply,
        "source": source,
        "context_chars": len(context),
        "elapsed_s": elapsed,
    }), 200


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    log.info("Starting FAITHH backend on port %s", BACKEND_PORT)
    app.run(host="0.0.0.0", port=BACKEND_PORT, debug=False)
