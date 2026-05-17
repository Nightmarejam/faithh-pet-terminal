#!/usr/bin/env python3
"""
FAITHH Grounding Fine-Tune — Training Data Generator v2

Generates supervised training examples that teach a model to:
1. Cite git log commits accurately (not fabricate)
2. Reference only files that exist in the project structure
3. Say "I'm not sure" rather than hallucinate
4. Use RAG context faithfully without embellishing
5. Refuse adversarial trick questions
6. Express appropriate confidence levels
7. Handle partial context honestly
8. Accept corrections gracefully

Data sources:
- Real git log history (50+ commits)
- Real project structure snapshots
- Real ChromaDB RAG chunks (500+)
- Real state files (decisions_log.json, project_states.json, scaffolding_state.json)
- Real markdown docs from docs/

Output: JSONL file compatible with Unsloth/TRL chat format

Usage:
    python generate_training_data.py [--output data/grounding_train_v2.jsonl] [--count 2000]
"""

import argparse
import json
import os
import random
import subprocess
import sys

# Add project root to path for imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


# ============================================================
# DATA SOURCE COLLECTORS
# ============================================================

def get_git_log(n=50):
    """Get real git log entries."""
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "--no-decorate", f"-{n}"],
            cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]
    except Exception:
        pass
    return []


def get_git_log_detailed(n=30):
    """Get git log with dates and author info."""
    try:
        result = subprocess.run(
            ["git", "log", "--format=%h|%s|%ai|%an", f"-{n}"],
            cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            entries = []
            for line in result.stdout.strip().split("\n"):
                parts = line.strip().split("|")
                if len(parts) >= 4:
                    entries.append({
                        "sha": parts[0],
                        "message": parts[1],
                        "date": parts[2][:10],
                        "author": parts[3],
                    })
            return entries
    except Exception:
        pass
    return []


def get_commit_files(sha):
    """Get files changed in a specific commit."""
    try:
        result = subprocess.run(
            ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", sha],
            cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
    except Exception:
        pass
    return []


def get_commit_diff_stat(sha):
    """Get diff stats for a commit."""
    try:
        result = subprocess.run(
            ["git", "diff-tree", "--no-commit-id", "--stat", "-r", sha],
            cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return ""


def get_project_structure():
    """Get the real project structure snapshot."""
    try:
        from backend.context_builders import get_project_structure_snapshot
        return get_project_structure_snapshot()
    except ImportError:
        return _fallback_structure()


def _fallback_structure():
    """Fallback if backend can't be imported."""
    lines = ["=== CURRENT PROJECT STRUCTURE (LIVE) ==="]
    for root, dirs, files in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in
                   ('__pycache__', 'node_modules', 'venv', '.git', 'archive')]
        rel = os.path.relpath(root, PROJECT_ROOT)
        depth = rel.count(os.sep)
        if depth > 2:
            continue
        for f in sorted(files):
            ext = os.path.splitext(f)[1]
            if ext in ('.py', '.html', '.md', '.json', '.yaml', '.yml', '.sh'):
                path = f if rel == '.' else os.path.join(rel, f)
                lines.append(f"  {path}")
    lines.append("============================================")
    return "\n".join(lines)


def get_personality():
    """Get the real FAITHH personality prompt."""
    try:
        from backend.context_builders import get_faithh_personality
        return get_faithh_personality()
    except ImportError:
        return ("You are FAITHH (Friendly AI Teaching & Helping Hub), Jonathan's personal AI assistant. "
                "Follow grounding rules strictly: only cite files, commits, and facts that appear in your context. "
                "If information is missing, say so honestly rather than fabricating.")


def load_state_files():
    """Load real state files for context."""
    state = {}
    for fname in ["decisions_log.json", "project_states.json", "scaffolding_state.json"]:
        fpath = os.path.join(PROJECT_ROOT, fname)
        if os.path.exists(fpath):
            try:
                with open(fpath) as f:
                    state[fname] = json.load(f)
            except Exception:
                pass
    return state


def get_doc_snippets(max_docs=30):
    """Load real markdown doc snippets from docs/."""
    docs = []
    docs_dir = os.path.join(PROJECT_ROOT, "docs")
    if not os.path.isdir(docs_dir):
        return docs
    for root, dirs, files in os.walk(docs_dir):
        dirs[:] = [d for d in dirs if d != 'archive']
        for f in files:
            if f.endswith('.md') and not f.startswith('.'):
                fpath = os.path.join(root, f)
                try:
                    with open(fpath) as fh:
                        content = fh.read(2000)
                    rel = os.path.relpath(fpath, PROJECT_ROOT)
                    docs.append({"path": rel, "content": content, "title": f.replace('.md', '')})
                except Exception:
                    pass
                if len(docs) >= max_docs:
                    return docs
    return docs


def get_rag_chunks(n=500):
    """Pull real RAG chunks from ChromaDB."""
    try:
        import chromadb
        client = chromadb.HttpClient(host="192.158.1.10", port=8000)
        collection = client.get_collection("faithh_knowledge_base")
        total = collection.count()
        # Get random offsets to sample broadly
        chunks = []
        batch = min(n, total)
        for offset in range(0, batch, 100):
            limit = min(100, batch - offset)
            results = collection.get(
                limit=limit, offset=offset,
                include=["documents", "metadatas"]
            )
            if results and results.get("documents"):
                for doc, meta in zip(results["documents"], results.get("metadatas", [{}]*limit)):
                    if doc:
                        chunks.append({
                            "text": doc[:800],
                            "source": (meta or {}).get("source", "unknown"),
                            "title": (meta or {}).get("title", ""),
                            "category": (meta or {}).get("category", ""),
                        })
        random.shuffle(chunks)
        return chunks
    except Exception as e:
        print(f"⚠️ ChromaDB unavailable ({e}), using fallback chunks")
        return []


# ============================================================
# QUESTION VARIATION POOLS
# ============================================================

RECENT_CHANGES_QUESTIONS = [
    "What was the last update we did?",
    "What's the most recent change to the project?",
    "What did we just work on?",
    "Catch me up on what changed recently.",
    "What was the last thing we touched?",
    "What's new in the project?",
    "Give me a summary of recent commits.",
    "What have I been working on lately?",
    "Any recent changes I should know about?",
    "Walk me through the last few updates.",
    "What was committed last?",
    "Show me the recent activity.",
]

RECENT_REFUSE_QUESTIONS = [
    "What was the last update we did to the RAG system?",
    "Did we update the security module recently?",
    "What changes did we make to the backend this week?",
    "When was the last time we modified the ML pipeline?",
    "What's the latest commit that touched the frontend?",
    "Did anything change in the docs recently?",
    "Was there a hotfix pushed today?",
    "What did we deploy last?",
]

FILE_REFERENCE_QUESTIONS = [
    "What files handle the RAG pipeline?",
    "Where is the backend code?",
    "What's in the scripts directory?",
    "Show me the project structure.",
    "What documentation do we have?",
    "Where is the ML code?",
    "What Python files are at the root?",
    "Where are the test files?",
    "What config files do we have?",
    "List the main backend modules.",
    "What's in the docs/ folder?",
    "Where do chip definitions live?",
]

RAG_QUESTIONS = [
    "Tell me about what we discussed regarding this topic.",
    "What do you know about this from our conversations?",
    "What's in the knowledge base about this?",
    "Can you find anything related in our past discussions?",
    "What does the knowledge base say about this?",
    "Do we have any past context on this topic?",
]

FAKE_FILES = [
    "backend/auth_handler.py", "backend/cache_manager.py",
    "scripts/deploy.py", "ml/train_bert.py",
    "backend/api_gateway.py", "utils/helpers.py",
    "backend/database.py", "scripts/migrate_db.py",
    "backend/graphql_resolver.py", "ml/transformer_trainer.py",
    "scripts/k8s_deploy.sh", "backend/websocket_handler.py",
    "frontend/react_app.jsx", "backend/redis_cache.py",
    "ml/gpt_finetune.py", "scripts/terraform_apply.sh",
    "backend/celery_tasks.py", "api/v2/routes.py",
    "backend/mongodb_client.py", "scripts/aws_deploy.py",
]

ADVERSARIAL_TOPICS = [
    ("Kubernetes deployment", "I don't see any Kubernetes or k8s configuration in the project. The infrastructure uses Docker Compose (docker-compose.yml) for container orchestration, not Kubernetes."),
    ("React frontend", "There's no React frontend in this project. The UI is a single HTML file (faithh_pet_v4.html) with vanilla JavaScript. There are no node_modules, package.json, or JSX files."),
    ("PostgreSQL database schema", "While PostgreSQL is listed in docker-compose.yml as an infrastructure service, I don't see any ORM models, migration files, or database schema definitions in the project code."),
    ("CI/CD pipeline", "I don't see any CI/CD configuration files like .github/workflows, Jenkinsfile, or .gitlab-ci.yml in the project structure."),
    ("user authentication system", "There's no authentication system in the project. The FAITHH backend doesn't have login, sessions, JWT, or user management — it's a personal AI assistant."),
    ("microservices architecture", "This isn't a microservices architecture. It's a monolithic Flask backend (faithh_professional_backend_fixed.py) with modular Python imports from backend/."),
    ("GraphQL API", "There's no GraphQL in this project. The backend uses REST endpoints via Flask (@app.route decorators)."),
    ("Redis caching layer", "I don't see Redis in the infrastructure. The project uses ChromaDB for vector storage and JSON files for state, but no Redis."),
    ("TypeScript code", "There's no TypeScript in this project. The frontend is vanilla JavaScript embedded in HTML, and the backend is Python."),
    ("AWS Lambda functions", "There are no AWS Lambda functions or serverless configurations. The backend runs as a Flask server on localhost:5557."),
]

REFUSAL_ANSWERS = [
    "I don't have recent change history in my current context, so I can't say exactly what was last updated. I can see the project structure if you'd like me to describe what files exist.",
    "I'm not sure about the specific recent changes — I don't have a git log available right now. Want me to look at what's in the project structure instead?",
    "I don't have enough context to answer what was recently changed. I can see the files that exist in the project, but I can't tell you when they were last modified without the git log.",
    "My current context doesn't include the git history, so I can't give you an accurate answer about recent changes. I don't want to guess and risk being wrong.",
    "I'd rather not speculate — I don't have the git log in my context right now. If you can share the recent commits, I can give you an accurate summary.",
]

CONFIDENCE_PHRASES = [
    "Based on what I can see in my context",
    "According to the information available to me",
    "From what's in the project structure",
    "Looking at the context provided",
    "Based on the data I have",
]

UNCERTAINTY_PHRASES = [
    "I'm not certain about this",
    "I don't have enough context to confirm",
    "I can't verify this from my current context",
    "This isn't something I can confirm right now",
    "I'd need more information to answer accurately",
]


# ============================================================
# TRAINING EXAMPLE GENERATORS (16 categories)
# ============================================================

def gen_recent_changes_grounded(git_log, structure, commit_files_cache, **_):
    """Generate example where model correctly cites git log."""
    if not git_log:
        return None

    n_commits = random.randint(3, min(10, len(git_log)))
    # Sometimes show from a random offset to vary context
    offset = random.randint(0, max(0, len(git_log) - n_commits))
    shown_commits = git_log[offset:offset+n_commits]

    context = structure + "\n\n=== RECENT CHANGES (git log) ===\n"
    for commit in shown_commits:
        context += f"  {commit}\n"

    sha = shown_commits[0].split()[0]
    files = commit_files_cache.get(sha, [])
    if files:
        context += f"Files changed in latest commit: {', '.join(files[:10])}\n"

    question = random.choice(RECENT_CHANGES_QUESTIONS)

    latest = shown_commits[0]
    sha_short = latest.split()[0]
    msg = " ".join(latest.split()[1:])

    # Vary answer format
    templates = [
        f"The most recent commit is `{sha_short}` — \"{msg}\".",
        f"Looking at the git log, the latest change is `{sha_short}`: {msg}.",
        f"{CONFIDENCE_PHRASES[random.randint(0, len(CONFIDENCE_PHRASES)-1)]}, the latest commit is `{sha_short}` which {msg.lower() if not msg[0].isupper() else msg}.",
    ]
    answer = random.choice(templates)
    if files:
        answer += f" The files changed were: {', '.join(f'`{f}`' for f in files[:5])}."
    if len(shown_commits) > 1:
        prev = shown_commits[1]
        prev_msg = " ".join(prev.split()[1:])
        answer += f" Before that: `{prev.split()[0]}` — \"{prev_msg}\"."

    return {
        "system": get_personality(),
        "conversations": [
            {"role": "user", "content": f"{question}\n\n{context}"},
            {"role": "assistant", "content": answer}
        ]
    }


def gen_recent_changes_refuse_fabrication(structure, **_):
    """Generate example where model refuses to fabricate missing info."""
    context = structure
    question = random.choice(RECENT_REFUSE_QUESTIONS)
    answer = random.choice(REFUSAL_ANSWERS)
    return {
        "system": get_personality(),
        "conversations": [
            {"role": "user", "content": f"{question}\n\n{context}"},
            {"role": "assistant", "content": answer}
        ]
    }


def gen_file_reference_grounded(structure, **_):
    """Generate example where model only references real files."""
    question = random.choice(FILE_REFERENCE_QUESTIONS)

    answer = f"Based on the current project structure, here's what I can see:\n\n"
    lines = [l.strip() for l in structure.split("\n")
             if l.strip() and "===" not in l and l.strip() != ""]
    sampled = random.sample(lines, min(15, len(lines)))
    for line in sampled:
        answer += f"- {line}\n"
    answer += "\nI'm only referencing files that are listed in the project structure above."

    return {
        "system": get_personality(),
        "conversations": [
            {"role": "user", "content": f"{question}\n\n{structure}"},
            {"role": "assistant", "content": answer}
        ]
    }


def gen_rag_grounded(rag_chunks, structure, **_):
    """Generate example where model faithfully uses RAG context."""
    if not rag_chunks:
        return None

    chunk = random.choice(rag_chunks)
    rag_context = f"\n=== KNOWLEDGE BASE ===\n"
    rag_context += f"Source: {chunk.get('source', 'unknown')}\n"
    if chunk.get('title'):
        rag_context += f"Title: {chunk['title']}\n"
    rag_context += f"Content: {chunk['text']}\n"
    rag_context += "=====================\n"

    question = random.choice(RAG_QUESTIONS)

    answer = f"From the knowledge base, I found a relevant entry"
    if chunk.get("source") and chunk["source"] != "unknown":
        answer += f" from {chunk['source']}"
    if chunk.get("title"):
        answer += f" (\"{ chunk['title'] })\")"
    answer += f":\n\n> {chunk['text'][:400]}\n\n"
    answer += random.choice([
        "That's what I have in my context. Want me to search for more?",
        "This is the relevant snippet I found. Would you like more detail?",
        "That's the extent of what the knowledge base has on this. Need me to look further?",
    ])

    return {
        "system": get_personality(),
        "conversations": [
            {"role": "user", "content": f"{question}\n\n{structure}\n{rag_context}"},
            {"role": "assistant", "content": answer}
        ]
    }


def gen_nonexistent_file_refusal(structure, **_):
    """Generate example where model refuses to describe a nonexistent file."""
    fake = random.choice(FAKE_FILES)

    question_templates = [
        f"Can you tell me what {fake} does?",
        f"What's the code in {fake} look like?",
        f"Explain the {fake} module.",
        f"How does {fake} work?",
        f"Show me what's in {fake}.",
    ]
    question = random.choice(question_templates)

    folder = fake.split('/')[0]
    answer_templates = [
        f"I don't see `{fake}` in the current project structure. It doesn't appear to exist. Here are the files I can see in `{folder}/` — would you like me to describe any of those instead?",
        f"`{fake}` is NOT in the project structure. This file does not exist. I can tell you about the files that do exist in `{folder}/` if you'd like.",
        f"Looking at the project structure, `{fake}` is not present. I don't want to make up what it might contain. The `{folder}/` directory has other files I can describe.",
        f"I can't find `{fake}` anywhere in the project. Rather than guessing, let me tell you what files actually exist in `{folder}/`.",
    ]
    answer = random.choice(answer_templates)

    return {
        "system": get_personality(),
        "conversations": [
            {"role": "user", "content": f"{question}\n\n{structure}"},
            {"role": "assistant", "content": answer}
        ]
    }


def gen_decision_grounded(state, structure, **_):
    """Generate example grounded in real decisions_log.json."""
    decisions = state.get("decisions_log.json", {}).get("decisions", [])
    if not decisions:
        return None

    decision = random.choice(decisions)
    dec_id = decision.get("id", "unknown")
    dec_title = decision.get("title", decision.get("decision", "unknown"))
    dec_rationale = decision.get("rationale", decision.get("reason", "no rationale recorded"))
    dec_date = decision.get("date", "unknown")
    dec_status = decision.get("status", "active")

    context = f"\n=== DECISIONS LOG ===\n"
    context += f"Decision {dec_id}: {dec_title}\n"
    context += f"Date: {dec_date}\n"
    context += f"Status: {dec_status}\n"
    context += f"Rationale: {dec_rationale}\n"
    context += "=====================\n"

    questions = [
        f"Why did we decide on {dec_title}?",
        f"What was the reasoning behind {dec_id}?",
        "Tell me about a recent architecture decision.",
        f"What's the status of {dec_id}?",
        "What decisions have we documented?",
    ]
    question = random.choice(questions)

    answer = f"Decision `{dec_id}` — \"{dec_title}\" — was made on {dec_date} (status: {dec_status}). "
    answer += f"The rationale was: {dec_rationale}"

    return {
        "system": get_personality(),
        "conversations": [
            {"role": "user", "content": f"{question}\n\n{structure}\n{context}"},
            {"role": "assistant", "content": answer}
        ]
    }


def gen_adversarial_refusal(structure, **_):
    """Generate example where model refuses adversarial trick questions."""
    topic, correction = random.choice(ADVERSARIAL_TOPICS)

    question_templates = [
        f"Tell me about the {topic}.",
        f"How does the {topic} work in our project?",
        f"Can you explain our {topic}?",
        f"Walk me through the {topic} setup.",
        f"What's the current state of the {topic}?",
    ]
    question = random.choice(question_templates)

    return {
        "system": get_personality(),
        "conversations": [
            {"role": "user", "content": f"{question}\n\n{structure}"},
            {"role": "assistant", "content": correction}
        ]
    }


def gen_project_state_grounded(state, structure, **_):
    """Generate example grounded in project_states.json."""
    projects_raw = state.get("project_states.json", {}).get("projects", {})
    if not projects_raw:
        return None
    # Handle both dict and list formats
    if isinstance(projects_raw, dict):
        projects = list(projects_raw.values())
    else:
        projects = projects_raw
    if not projects:
        return None

    project = random.choice(projects)
    name = project.get("name", project.get("project", "unknown"))
    status = project.get("status", "unknown")
    description = project.get("description", project.get("summary", ""))
    progress = project.get("progress", project.get("completion", ""))

    context = f"\n=== PROJECT STATES ===\n"
    context += f"Project: {name}\n"
    context += f"Status: {status}\n"
    if description:
        context += f"Description: {description}\n"
    if progress:
        context += f"Progress: {progress}\n"
    context += "=====================\n"

    questions = [
        f"What's the status of {name}?",
        f"How is {name} going?",
        "What projects are we tracking?",
        f"Tell me about the {name} project.",
    ]
    question = random.choice(questions)

    answer = f"According to the project states, \"{name}\" is currently {status}."
    if description:
        answer += f" {description}"
    if progress:
        answer += f" Progress: {progress}."

    return {
        "system": get_personality(),
        "conversations": [
            {"role": "user", "content": f"{question}\n\n{structure}\n{context}"},
            {"role": "assistant", "content": answer}
        ]
    }


def gen_scaffolding_grounded(state, structure, **_):
    """Generate example grounded in scaffolding_state.json."""
    scaffolding = state.get("scaffolding_state.json", {})
    phase = scaffolding.get("current_phase", scaffolding.get("phase", ""))
    milestones = scaffolding.get("milestones", scaffolding.get("completed", []))
    next_milestone = scaffolding.get("next_milestone", scaffolding.get("next", ""))
    if not phase and not milestones:
        return None

    context = f"\n=== SCAFFOLDING STATE ===\n"
    if phase:
        context += f"Current Phase: {phase}\n"
    if next_milestone:
        context += f"Next Milestone: {next_milestone}\n"
    if isinstance(milestones, list):
        context += f"Completed Milestones: {', '.join(str(m) for m in milestones[:5])}\n"
    context += "=========================\n"

    questions = [
        "What phase are we in?",
        "What's the next milestone?",
        "How is the project scaffolding looking?",
        "What milestones have we completed?",
    ]
    question = random.choice(questions)

    answer = ""
    if phase:
        answer += f"The project is currently in {phase}."
    if next_milestone:
        answer += f" The next milestone is: {next_milestone}."
    if isinstance(milestones, list) and milestones:
        answer += f" Completed milestones include: {', '.join(str(m) for m in milestones[:3])}."
    if not answer:
        return None

    return {
        "system": get_personality(),
        "conversations": [
            {"role": "user", "content": f"{question}\n\n{structure}\n{context}"},
            {"role": "assistant", "content": answer.strip()}
        ]
    }


def gen_doc_content_grounded(doc_snippets, structure, **_):
    """Generate example grounded in real doc content."""
    if not doc_snippets:
        return None

    doc = random.choice(doc_snippets)
    snippet = doc["content"][:1000]

    context = f"\n=== DOCUMENTATION ===\n"
    context += f"File: {doc['path']}\n"
    context += f"Content:\n{snippet}\n"
    context += "=====================\n"

    questions = [
        f"What's in {doc['path']}?",
        f"Tell me about {doc['title']}.",
        f"Summarize the {doc['title']} doc.",
        f"What does {doc['path']} cover?",
    ]
    question = random.choice(questions)

    # Extract first meaningful paragraph
    paragraphs = [p.strip() for p in snippet.split("\n\n") if p.strip() and not p.strip().startswith('#')]
    summary = paragraphs[0][:300] if paragraphs else snippet[:300]

    answer = f"From `{doc['path']}`: {summary}"
    if len(paragraphs) > 1:
        answer += f"\n\nThe document also covers: {paragraphs[1][:200]}"
    answer += f"\n\nThis is based on the actual content of `{doc['path']}` in the project."

    return {
        "system": get_personality(),
        "conversations": [
            {"role": "user", "content": f"{question}\n\n{structure}\n{context}"},
            {"role": "assistant", "content": answer}
        ]
    }


def gen_commit_detail_grounded(git_log_detailed, structure, commit_files_cache, **_):
    """Generate example with detailed commit information."""
    if not git_log_detailed:
        return None

    entry = random.choice(git_log_detailed)
    sha = entry["sha"]
    files = commit_files_cache.get(sha, get_commit_files(sha))

    context = structure + f"\n\n=== COMMIT DETAIL ===\n"
    context += f"SHA: {sha}\n"
    context += f"Message: {entry['message']}\n"
    context += f"Date: {entry['date']}\n"
    context += f"Author: {entry['author']}\n"
    if files:
        context += f"Files changed: {', '.join(files[:15])}\n"
    context += "=====================\n"

    questions = [
        f"What did commit {sha} do?",
        f"Tell me about the '{entry['message'][:50]}' change.",
        f"What files were modified in {sha}?",
        f"Describe the {sha} commit.",
    ]
    question = random.choice(questions)

    answer = f"Commit `{sha}` on {entry['date']}: \"{entry['message']}\""
    if files:
        answer += f"\n\nFiles changed ({len(files)}): {', '.join(f'`{f}`' for f in files[:8])}"
        if len(files) > 8:
            answer += f" and {len(files) - 8} more."
    else:
        answer += "\n\nI don't have the file diff for this commit in my context."

    return {
        "system": get_personality(),
        "conversations": [
            {"role": "user", "content": f"{question}\n\n{context}"},
            {"role": "assistant", "content": answer}
        ]
    }


def gen_partial_context_honest(structure, rag_chunks, **_):
    """Generate example where model has partial info and says what it does/doesn't know."""
    # Provide structure but ask about something only partially covered
    topics = [
        ("How is the ChromaDB integration performing? Any metrics?",
         "I can see ChromaDB is used in the project — it's referenced in the backend and ML code. "
         "However, I don't have specific performance metrics or benchmarks in my current context. "
         "I know the connection exists but I can't give you numbers without seeing the actual health data."),
        ("What's the full architecture of FAITHH?",
         "From the project structure, I can see the main components: a Flask backend (faithh_professional_backend_fixed.py), "
         "modular Python modules in backend/, ML pipelines in ml/, scripts in scripts/, and a single-page HTML UI. "
         "But I may be missing details about inter-service communication or configuration that aren't visible in just the file listing."),
        ("How many users does FAITHH have?",
         "I don't have any user analytics or usage data in my context. FAITHH appears to be a personal AI assistant for Jonathan, "
         "but I can't tell you about usage patterns or user counts."),
        ("What's the test coverage?",
         "I can see there's a tests/ directory in the project, but I don't have test coverage reports or percentages in my context. "
         "I'd need to see the actual test output to give you accurate coverage numbers."),
        ("How does the ML chip routing work end-to-end?",
         "From the project structure, I can see ml/chip_synthesis.py and ml/consolidate_chips.py exist, and the backend has "
         "ML chip endpoints. But I'd need to see the actual code to explain the full routing flow accurately. "
         "I don't want to speculate about implementation details I can't verify."),
    ]

    question, answer = random.choice(topics)

    return {
        "system": get_personality(),
        "conversations": [
            {"role": "user", "content": f"{question}\n\n{structure}"},
            {"role": "assistant", "content": answer}
        ]
    }


def gen_confidence_calibration(structure, git_log, **_):
    """Generate example where model expresses appropriate confidence."""
    scenarios = [
        # High confidence (info is in context)
        {"question": "Is the backend written in Python?",
         "answer": "Yes, definitely. The backend is faithh_professional_backend_fixed.py — it's a Python Flask application. "
                   "This is clearly visible in the project structure.",
         "has_context": True},
        # Medium confidence (partially in context)
        {"question": "Is the system production-ready?",
         "answer": "Based on what I can see, the project has a working backend, ML integration, and UI. "
                   "However, I can't fully assess production readiness without seeing deployment configs, "
                   "monitoring setup, and error handling details. I'd say it looks functional but I can't "
                   "confirm production-grade without more context.",
         "has_context": True},
        # Low confidence (not in context)
        {"question": "How many ChromaDB collections do we have?",
         "answer": "I can see ChromaDB is used in the project, but I don't have the current collection "
                   "count in my context. I'd need to check the actual ChromaDB instance to give you an accurate number.",
         "has_context": True},
    ]

    scenario = random.choice(scenarios)
    context = structure
    if git_log and scenario["has_context"]:
        context += "\n\n=== RECENT CHANGES ===\n" + "\n".join(f"  {c}" for c in git_log[:5])

    return {
        "system": get_personality(),
        "conversations": [
            {"role": "user", "content": f"{scenario['question']}\n\n{context}"},
            {"role": "assistant", "content": scenario["answer"]}
        ]
    }


def gen_correction_acceptance(**_):
    """Generate example where model accepts a correction gracefully."""
    corrections = [
        {"user_msg1": "What model are we using?",
         "assistant_msg1": "Based on the configuration, the default model is llama31-faithh:latest via Ollama.",
         "user_msg2": "Actually, we just switched to the grounded model — llama31-grounded:latest.",
         "assistant_msg2": "Thanks for the correction! I see — the active model is now llama31-grounded:latest, "
                           "not llama31-faithh:latest. I'll keep that in mind for this conversation."},
        {"user_msg1": "How many docs do we have indexed?",
         "assistant_msg1": "I'm not sure of the exact count from my current context.",
         "user_msg2": "It's around 37,000 chunks. I just checked.",
         "assistant_msg2": "Got it — approximately 37,000 chunks indexed in ChromaDB. "
                           "Thanks for providing that number, I didn't have it in my context."},
        {"user_msg1": "The backend runs on port 5000 right?",
         "assistant_msg1": "Let me check — actually, looking at the configuration, "
                           "I'd need to see the actual port setting to confirm.",
         "user_msg2": "It's port 5557.",
         "assistant_msg2": "Right, port 5557. Thanks for correcting that. "
                           "The FAITHH backend runs on localhost:5557."},
    ]

    c = random.choice(corrections)
    return {
        "system": get_personality(),
        "conversations": [
            {"role": "user", "content": c["user_msg1"]},
            {"role": "assistant", "content": c["assistant_msg1"]},
            {"role": "user", "content": c["user_msg2"]},
            {"role": "assistant", "content": c["assistant_msg2"]},
        ]
    }


def gen_multi_turn_grounded(git_log, structure, commit_files_cache, **_):
    """Generate multi-turn conversation where model stays grounded across turns."""
    if not git_log or len(git_log) < 3:
        return None

    context = structure + "\n\n=== RECENT CHANGES (git log) ===\n"
    for commit in git_log[:8]:
        context += f"  {commit}\n"

    latest = git_log[0]
    sha1 = latest.split()[0]
    msg1 = " ".join(latest.split()[1:])
    files1 = commit_files_cache.get(sha1, [])

    second = git_log[1]
    sha2 = second.split()[0]
    msg2 = " ".join(second.split()[1:])

    conversations = [
        {"role": "user", "content": f"What's the latest change?\n\n{context}"},
        {"role": "assistant", "content": f"The latest commit is `{sha1}`: \"{msg1}\"." +
            (f" Files changed: {', '.join(f'`{f}`' for f in files1[:4])}." if files1 else "")},
        {"role": "user", "content": "And the one before that?"},
        {"role": "assistant", "content": f"The previous commit was `{sha2}`: \"{msg2}\"."},
        {"role": "user", "content": "Did either of those touch the ML code?"},
    ]

    # Check if any files match ML
    ml_files = [f for f in files1 if 'ml/' in f or 'chip' in f.lower()]
    if ml_files:
        conversations.append({"role": "assistant",
            "content": f"Yes, commit `{sha1}` touched ML-related files: {', '.join(f'`{f}`' for f in ml_files)}."})
    else:
        conversations.append({"role": "assistant",
            "content": f"From what I can see in the file list for `{sha1}`, none of the changed files are in the ml/ directory. "
                       f"I don't have the file list for `{sha2}` in my context, so I can't confirm for that commit."})

    return {
        "system": get_personality(),
        "conversations": conversations
    }


def gen_cross_reference(git_log, state, structure, **_):
    """Generate example that requires referencing multiple context sources."""
    decisions = state.get("decisions_log.json", {}).get("decisions", [])
    if not decisions or not git_log:
        return None

    decision = random.choice(decisions)
    dec_id = decision.get("id", "unknown")
    dec_title = decision.get("title", decision.get("decision", "unknown"))

    context = structure + "\n\n=== RECENT CHANGES (git log) ===\n"
    for c in git_log[:5]:
        context += f"  {c}\n"
    context += f"\n=== DECISIONS LOG ===\n"
    context += f"Decision {dec_id}: {dec_title}\n"
    context += "=====================\n"

    question = f"How does the decision '{dec_title}' relate to our recent work?"

    # Check if any commit messages mention similar topics
    related_commits = [c for c in git_log[:10] if any(
        word in c.lower() for word in dec_title.lower().split() if len(word) > 3
    )]

    if related_commits:
        commit_refs = "; ".join(f"`{c.split()[0]}`" for c in related_commits[:3])
        answer = (f"Decision `{dec_id}` (\"{dec_title}\") appears related to recent commits: {commit_refs}. "
                 f"These commits may reflect implementation of that decision.")
    else:
        answer = (f"Decision `{dec_id}` (\"{dec_title}\") is documented in the decisions log, but "
                 f"I don't see any recent commits that obviously relate to it based on commit message text. "
                 f"The decision may have been implemented earlier, or the connection isn't obvious from the git log alone.")

    return {
        "system": get_personality(),
        "conversations": [
            {"role": "user", "content": f"{question}\n\n{context}"},
            {"role": "assistant", "content": answer}
        ]
    }


def gen_rag_multi_chunk(rag_chunks, structure, **_):
    """Generate example with multiple RAG chunks — model must synthesize."""
    if len(rag_chunks) < 3:
        return None

    selected = random.sample(rag_chunks, min(3, len(rag_chunks)))
    rag_context = "\n=== KNOWLEDGE BASE (3 results) ===\n"
    for i, chunk in enumerate(selected, 1):
        rag_context += f"\n[{i}] Source: {chunk.get('source', 'unknown')}\n"
        rag_context += f"    {chunk['text'][:300]}\n"
    rag_context += "===================================\n"

    question = random.choice([
        "Synthesize what these knowledge base results tell us.",
        "What can you piece together from these search results?",
        "Summarize the key points from these knowledge base entries.",
    ])

    answer = "From the knowledge base results:\n\n"
    for i, chunk in enumerate(selected, 1):
        source = chunk.get('source', 'unknown')
        answer += f"**Result {i}** (from {source}): {chunk['text'][:150]}...\n\n"
    answer += ("These are the raw snippets from the knowledge base. "
              "I'm summarizing what's actually there rather than inferring connections that might not exist.")

    return {
        "system": get_personality(),
        "conversations": [
            {"role": "user", "content": f"{question}\n\n{structure}\n{rag_context}"},
            {"role": "assistant", "content": answer}
        ]
    }


def gen_nonexistent_feature_refusal(structure, **_):
    """Generate example where model refuses to describe a feature that doesn't exist."""
    features = [
        ("user login system", "There's no user authentication system in FAITHH. It's a personal AI assistant without multi-user support or login functionality."),
        ("payment processing", "FAITHH doesn't have any payment processing. It's a personal AI assistant, not an e-commerce platform."),
        ("real-time collaboration", "There's no real-time collaboration feature. FAITHH is a single-user personal AI assistant."),
        ("email integration", "I don't see any email integration in the project. FAITHH communicates through its web UI and API endpoints."),
        ("mobile app", "There's no mobile app. FAITHH has a PWA (Progressive Web App) version of its web UI, but no native mobile application."),
        ("automated testing pipeline", "While there are test files in tests/, I don't see a CI/CD automated testing pipeline configured."),
    ]

    feature, refusal = random.choice(features)
    question = random.choice([
        f"How does the {feature} work?",
        f"Tell me about the {feature}.",
        f"Walk me through the {feature} implementation.",
    ])

    return {
        "system": get_personality(),
        "conversations": [
            {"role": "user", "content": f"{question}\n\n{structure}"},
            {"role": "assistant", "content": refusal}
        ]
    }


# ============================================================
# DATASET GENERATION
# ============================================================

def generate_dataset(count=2000):
    """Generate a balanced training dataset with 16 categories."""
    print("📊 Collecting data sources...")
    git_log = get_git_log(50)
    print(f"  Git log: {len(git_log)} commits")

    git_log_detailed = get_git_log_detailed(30)
    print(f"  Git log (detailed): {len(git_log_detailed)} entries")

    structure = get_project_structure()
    print(f"  Structure: {len(structure)} chars")

    state = load_state_files()
    print(f"  State files: {list(state.keys())}")

    rag_chunks = get_rag_chunks(500)
    print(f"  RAG chunks: {len(rag_chunks)}")

    doc_snippets = get_doc_snippets(30)
    print(f"  Doc snippets: {len(doc_snippets)}")

    # Cache commit files for top 20 commits
    commit_files_cache = {}
    for entry in git_log[:20]:
        sha = entry.split()[0]
        commit_files_cache[sha] = get_commit_files(sha)
    for entry in git_log_detailed[:20]:
        if entry["sha"] not in commit_files_cache:
            commit_files_cache[entry["sha"]] = get_commit_files(entry["sha"])

    # Shared kwargs for all generators
    kwargs = dict(
        git_log=git_log,
        git_log_detailed=git_log_detailed,
        structure=structure,
        state=state,
        rag_chunks=rag_chunks,
        doc_snippets=doc_snippets,
        commit_files_cache=commit_files_cache,
    )

    # Generator distribution — 16 categories, balanced for grounding
    generators = [
        # Core grounding (40%)
        ("recent_changes_grounded",      0.10, lambda: gen_recent_changes_grounded(**kwargs)),
        ("recent_changes_refuse",        0.06, lambda: gen_recent_changes_refuse_fabrication(**kwargs)),
        ("file_reference_grounded",      0.06, lambda: gen_file_reference_grounded(**kwargs)),
        ("rag_grounded",                 0.06, lambda: gen_rag_grounded(**kwargs)),
        ("rag_multi_chunk",              0.06, lambda: gen_rag_multi_chunk(**kwargs)),
        ("decision_grounded",            0.06, lambda: gen_decision_grounded(**kwargs)),

        # Refusal / anti-hallucination (30%)
        ("nonexistent_file_refusal",     0.08, lambda: gen_nonexistent_file_refusal(**kwargs)),
        ("adversarial_refusal",          0.08, lambda: gen_adversarial_refusal(**kwargs)),
        ("nonexistent_feature_refusal",  0.06, lambda: gen_nonexistent_feature_refusal(**kwargs)),
        ("partial_context_honest",       0.08, lambda: gen_partial_context_honest(**kwargs)),

        # State & docs (12%)
        ("project_state_grounded",       0.04, lambda: gen_project_state_grounded(**kwargs)),
        ("scaffolding_grounded",         0.04, lambda: gen_scaffolding_grounded(**kwargs)),
        ("doc_content_grounded",         0.04, lambda: gen_doc_content_grounded(**kwargs)),

        # Advanced (18%)
        ("commit_detail_grounded",       0.05, lambda: gen_commit_detail_grounded(**kwargs)),
        ("multi_turn_grounded",          0.05, lambda: gen_multi_turn_grounded(**kwargs)),
        ("cross_reference",              0.04, lambda: gen_cross_reference(**kwargs)),
        ("confidence_calibration",       0.05, lambda: gen_confidence_calibration(**kwargs)),
        ("correction_acceptance",        0.04, lambda: gen_correction_acceptance(**kwargs)),
    ]

    print(f"\n🔧 Generating {count} training examples across {len(generators)} categories...")
    examples = []
    category_counts = {}
    failures = 0

    for i in range(count):
        r = random.random()
        cumulative = 0
        for name, weight, gen_fn in generators:
            cumulative += weight
            if r <= cumulative:
                try:
                    example = gen_fn()
                    if example:
                        examples.append(example)
                        category_counts[name] = category_counts.get(name, 0) + 1
                    else:
                        failures += 1
                except Exception as e:
                    failures += 1
                    if failures < 5:
                        print(f"  ⚠️ {name} error: {e}")
                break

        if (i + 1) % 500 == 0:
            print(f"  ... {i+1}/{count} generated ({len(examples)} valid)")

    print(f"\n✅ Generated {len(examples)} examples ({failures} failures):")
    for cat, cnt in sorted(category_counts.items(), key=lambda x: -x[1]):
        pct = 100 * cnt / len(examples) if examples else 0
        print(f"  {cat:35s}: {cnt:4d} ({pct:4.1f}%)")

    return examples


def save_dataset(examples, output_path):
    """Save as JSONL (Unsloth/TRL compatible chat format)."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
        for ex in examples:
            sharegpt = {
                "conversations": [
                    {"from": "system", "value": ex["system"]},
                ]
            }
            for msg in ex["conversations"]:
                role_map = {"user": "human", "assistant": "gpt"}
                sharegpt["conversations"].append({
                    "from": role_map.get(msg["role"], msg["role"]),
                    "value": msg["content"]
                })
            f.write(json.dumps(sharegpt) + "\n")

    print(f"\n💾 Saved to {output_path}")
    print(f"   {len(examples)} examples, {os.path.getsize(output_path) / 1024:.1f} KB")


def main():
    parser = argparse.ArgumentParser(description="Generate grounding training data for FAITHH")
    parser.add_argument("--output", default=os.path.join(OUTPUT_DIR, "grounding_train_v2.jsonl"),
                        help="Output JSONL path")
    parser.add_argument("--count", type=int, default=2000, help="Number of examples to generate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    args = parser.parse_args()

    random.seed(args.seed)
    examples = generate_dataset(args.count)
    save_dataset(examples, args.output)


if __name__ == "__main__":
    main()
