import chromadb
from datetime import datetime

PURGE_SOURCES = [
    "claude/Continuing previous conversation",
    "claude/System check",
    "claude/Conversation history highlights",
]

FAILURE_REASONS = {
    "claude/Continuing previous conversation": "handoff_boilerplate",
    "claude/System check": "deflection_response",
    "claude/Conversation history highlights": "circular_meta_conversation",
}

def migrate_batch(kb, uncertainty, source, failure_reason, batch_size=100):
    offset = 0
    total_migrated = 0

    while True:
        r = kb.get(
            where={"source": {"$eq": source}},
            limit=batch_size,
            include=["documents", "metadatas", "embeddings"]
        )

        if not r["ids"]:
            break

        # Enrich metadata
        enriched_meta = []
        for m in r["metadatas"]:
            m["failure_reason"] = failure_reason
            m["migrated_at"] = datetime.utcnow().isoformat()
            m["migrated_from"] = "faithh_knowledge_base"
            enriched_meta.append(m)

        # Write to uncertainty surface
        uncertainty.add(
            ids=r["ids"],
            documents=r["documents"],
            metadatas=enriched_meta,
            embeddings=r["embeddings"]
        )

        # Delete from KB
        kb.delete(ids=r["ids"])

        total_migrated += len(r["ids"])
        print(f"  Migrated {total_migrated} chunks from {source}...")

        if len(r["ids"]) < batch_size:
            break

    return total_migrated

if __name__ == "__main__":
    c = chromadb.HttpClient(host="192.158.1.10", port=8000)
    kb = c.get_collection("faithh_knowledge_base")
    uncertainty = c.get_collection("faithh_uncertainty_surface")

    print(f"KB before: {kb.count()} chunks")
    print(f"Uncertainty surface before: {uncertainty.count()} chunks")
    print()

    total = 0
    for source in PURGE_SOURCES:
        reason = FAILURE_REASONS[source]
        print(f"Migrating: {source}")
        n = migrate_batch(kb, uncertainty, source, reason)
        print(f"  Done: {n} chunks\n")
        total += n

    print(f"KB after: {kb.count()} chunks")
    print(f"Uncertainty surface after: {uncertainty.count()} chunks")
    print(f"Total migrated: {total} chunks")
