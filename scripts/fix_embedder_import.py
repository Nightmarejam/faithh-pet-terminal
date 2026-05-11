#!/usr/bin/env python3
"""Fix the SentenceTransformer import to be fully lazy and prevent CUDA crashes."""

BACKEND_FILE = "/home/jonat/ai-stack/faithh_professional_backend_fixed.py"

with open(BACKEND_FILE, "r") as f:
    content = f.read()

# Remove the top-level import
old_import_section = """# Load embedding model lazily for manual query embedding
from sentence_transformers import SentenceTransformer
query_embedder = None
_embedder_init_attempted = False
_embedder_load_error = None"""

new_import_section = """# Load embedding model lazily for manual query embedding
# NOTE: SentenceTransformer import moved inside get_query_embedder() to prevent
# CUDA initialization at module load time (causes WSL crashes on sm_61 GPUs)
query_embedder = None
_embedder_init_attempted = False
_embedder_load_error = None
_SentenceTransformer = None  # Lazy import holder"""

if old_import_section in content:
    content = content.replace(old_import_section, new_import_section)
    print("✅ Removed top-level SentenceTransformer import")
else:
    print("⚠️ Top-level import section not found (may already be fixed)")

# Update the get_query_embedder function to do lazy import
old_function = """def get_query_embedder():
    \"\"\"Lazy-load embedder; avoid blocking startup when offline.\"\"\"
    global query_embedder, _embedder_init_attempted, _embedder_load_error
    if query_embedder is not None or _embedder_init_attempted:
        return query_embedder

    _embedder_init_attempted = True
    try:
        kwargs = {"device": "cpu"}  # force CPU for embedder to avoid CUDA kernel image issues
        if EMBEDDER_LOCAL_ONLY and not EMBEDDER_ALLOW_DOWNLOAD:
            kwargs["local_files_only"] = True
        query_embedder = SentenceTransformer(EMBEDDING_MODEL_ID, **kwargs)
        print("✅ Query embedder loaded (all-MiniLM-L6-v2, 384-dim)")
    except TypeError as e:
        _embedder_load_error = e
        if EMBEDDER_ALLOW_DOWNLOAD:
            try:
                query_embedder = SentenceTransformer(EMBEDDING_MODEL_ID)
                print("✅ Query embedder loaded (all-MiniLM-L6-v2, 384-dim)")
            except Exception as inner:
                _embedder_load_error = inner
                query_embedder = None
                print(f"⚠️ Query embedder not loaded: {inner}")
        else:
            query_embedder = None
            print(f"⚠️ Query embedder not loaded: {e}")
    except Exception as e:
        _embedder_load_error = e
        query_embedder = None
        print(f"⚠️ Query embedder not loaded: {e}")

    return query_embedder"""

new_function = """def get_query_embedder():
    \"\"\"Lazy-load embedder; avoid blocking startup when offline.
    
    IMPORTANT: SentenceTransformer is imported here (not at module level) to prevent
    CUDA initialization at startup, which crashes WSL on sm_61 GPUs (GTX 1080 Ti).
    \"\"\"
    global query_embedder, _embedder_init_attempted, _embedder_load_error, _SentenceTransformer
    if query_embedder is not None or _embedder_init_attempted:
        return query_embedder

    _embedder_init_attempted = True
    
    # Lazy import to avoid CUDA init at module load
    if _SentenceTransformer is None:
        try:
            # Force CPU before importing to prevent CUDA probe
            import os
            os.environ["CUDA_VISIBLE_DEVICES"] = ""
            from sentence_transformers import SentenceTransformer as ST
            _SentenceTransformer = ST
            print("✅ SentenceTransformer imported (CPU-only mode)")
        except Exception as e:
            _embedder_load_error = e
            print(f"⚠️ SentenceTransformer import failed: {e}")
            return None
    
    try:
        kwargs = {"device": "cpu"}  # force CPU for embedder to avoid CUDA kernel image issues
        if EMBEDDER_LOCAL_ONLY and not EMBEDDER_ALLOW_DOWNLOAD:
            kwargs["local_files_only"] = True
        query_embedder = _SentenceTransformer(EMBEDDING_MODEL_ID, **kwargs)
        print("✅ Query embedder loaded (all-MiniLM-L6-v2, 384-dim)")
    except TypeError as e:
        _embedder_load_error = e
        if EMBEDDER_ALLOW_DOWNLOAD:
            try:
                query_embedder = _SentenceTransformer(EMBEDDING_MODEL_ID)
                print("✅ Query embedder loaded (all-MiniLM-L6-v2, 384-dim)")
            except Exception as inner:
                _embedder_load_error = inner
                query_embedder = None
                print(f"⚠️ Query embedder not loaded: {inner}")
        else:
            query_embedder = None
            print(f"⚠️ Query embedder not loaded: {e}")
    except Exception as e:
        _embedder_load_error = e
        query_embedder = None
        print(f"⚠️ Query embedder not loaded: {e}")

    return query_embedder"""

if old_function in content:
    content = content.replace(old_function, new_function)
    print("✅ Updated get_query_embedder() with lazy import")
else:
    print("⚠️ get_query_embedder function not found (may already be fixed)")

with open(BACKEND_FILE, "w") as f:
    f.write(content)

print("\n✅ Backend patched to prevent CUDA crashes")
print("   - SentenceTransformer import is now fully lazy")
print("   - CUDA_VISIBLE_DEVICES set to empty before import")
print("\nRestart backend with: ./restart_backend.sh")
