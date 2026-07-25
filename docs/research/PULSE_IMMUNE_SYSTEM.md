# Building Pulse: An AI Immune System for FAITHH

> Research Document - 2026-01-18
> Source: Claude Deep Research

Your personal AI assistant needs what biological organisms evolved over millions of years: a sophisticated immune system that detects threats, heals damage, and maintains awareness of its own state. This research reveals that the tooling for building such a system has reached remarkable maturity in 2025—**most of what you need exists as open-source components ready for integration**, with the Model Context Protocol (MCP) emerging as the connective standard that ties everything together.

The architecture that emerges from this research is **defense-in-depth with layered autonomy**: prompt injection scanners at the perimeter, capability-based gatekeepers controlling access, self-healing infrastructure for resilience, and a shared state system that grounds any AI (local or cloud) in live system truth.

---

## The Four Pillars of an AI Immune System

Pulse needs to function across four integrated layers, each addressing a distinct failure mode:

| Pillar | Failure Mode | Solution |
|--------|--------------|----------|
| **Prompt Injection Defense** | External attacks hijacking AI behavior | Input/output scanning, canary tokens |
| **Infrastructure Failures** | Crashed services, corrupted state | Self-healing, health checks, auto-restart |
| **Context Drift & Hallucination** | AI loses touch with ground truth | State briefings, live system grounding |
| **Excessive Autonomy** | AI takes actions beyond authority | Capability permissions, gatekeeper pattern |

---

## Practical Tools for Immediate Deployment

### 1. Prompt Injection Defense with LLM Guard

**LLM Guard** from ProtectAI represents the fastest path to basic security. Install with `pip install llm-guard` and you gain input scanners for prompt injection, PII detection, toxicity filtering, and secrets detection—all running locally without external API calls.

```python
from llm_guard.input_scanners import PromptInjection, Secrets
from llm_guard.output_scanners import Sensitive

input_scanners = [PromptInjection(threshold=0.5), Secrets()]
output_scanners = [Sensitive()]

# Wrap every Ollama call
sanitized_input, is_valid, risk_score = scan_prompt(input_scanners, user_input)
if not is_valid:
    log_security_event(user_input, risk_score)
    return "Request blocked by security policy"
```

**Vigil-LLM** adds canary tokens—invisible markers injected into prompts that trigger alerts if they appear in outputs.

**NeMo Guardrails** provides the most comprehensive framework, using Colang DSL to define conversation boundaries.

### 2. Self-Healing Infrastructure with Docker Autoheal

The critical insight: **Docker's restart policies don't restart unhealthy containers—they only restart on process exit**. A service that's alive but unresponsive stays stuck.

Solution: **willfarrell/autoheal** container:

```yaml
services:
  autoheal:
    image: willfarrell/autoheal:latest
    restart: always
    environment:
      - AUTOHEAL_CONTAINER_LABEL=all
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock

  ollama:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 3
    labels:
      - "autoheal=true"
```

For non-Docker services, **Monit** provides equivalent functionality.

### 3. MCP as the Universal Connector

The **Model Context Protocol** has become the de facto standard for AI tool integration since Anthropic's November 2024 release. OpenAI, Google DeepMind, Replit, and Sourcegraph have all adopted it.

For FAITHH, MCP means exposing system state, tools, and capabilities through a single protocol that any AI—local Ollama or cloud Claude—can consume identically.

---

## Ground Truth Architecture for Multi-AI Coordination

### State Schema Design

```json
{
  "metadata": {
    "version": "1.0",
    "timestamp": "2025-01-18T10:30:00Z",
    "ttl_seconds": 300
  },
  "system_health": {
    "overall_status": "healthy",
    "services": [
      {"name": "ollama", "status": "running", "latency_ms": 45},
      {"name": "chromadb", "status": "running", "collections": 12}
    ]
  },
  "recent_actions": [
    {"agent": "ollama", "action": "file_read", "timestamp": "...", "status": "success"}
  ],
  "active_tasks": [
    {"id": "task-001", "description": "...", "priority": "high", "progress": 60}
  ]
}
```

### Briefing Generator

Transform state into markdown any AI can parse:

```markdown
# FAITHH System Briefing
Generated: 2025-01-18T10:30:00Z

## Current Status
- Overall Health: **healthy**
- Active Services: Ollama (45ms), ChromaDB (12 collections)

## Recent Activity (Last Hour)
| Time | Agent | Action | Result |
|------|-------|--------|--------|
| 10:28 | ollama | file_read | success |
```

---

## Security Architecture: Capability-Based Permissions

### The Gatekeeper Pattern

Every AI action passes through a central gatekeeper that checks permissions before execution:

```yaml
capabilities:
  read_files:
    level: read
    allowed_paths: ["/home/user/documents/**"]
    denied_patterns: ["*.key", "*.pem", "*.env"]
    requires_approval: false
    
  write_files:
    level: write
    allowed_paths: ["/home/user/workspace/**"]
    requires_approval: true
    
  execute_code:
    level: dangerous
    sandbox_required: true
    timeout_seconds: 30
    requires_approval: true
```

### Action Classification for Scaled Human Oversight

- **Green-light actions**: Read-only, no side effects → Execute automatically
- **Yellow-light actions**: Reversible modifications → Execute with async notification
- **Red-light actions**: Financial, permanent, security-sensitive → Explicit approval required

---

## Long-term Architectural Patterns

### The Artificial Immune System Paradigm

Academic research on Artificial Immune Systems (AIS) provides the conceptual framework:

- **Negative Selection Algorithm**: Establish "self" (normal patterns), flag deviations as "non-self"
- **Danger Theory**: Focus on stress signals—high latency, error rates, unusual actions

### Constitutional AI for Self-Governance

Anthropic's Constitutional AI offers a model for AI systems that can evaluate their own behavior against explicit principles:

```
FAITHH Constitution:
1. Always verify actions against current system state before execution
2. Never modify files outside designated workspace without explicit approval
3. Refuse requests that could expose secrets or credentials
4. When uncertain, ask for clarification rather than guessing
5. Log all actions for audit trail
```

### Responsible Scaling for Growing Capabilities

As FAITHH gains more capabilities, security should scale proportionally:

- **Level 1**: Basic assistant → Standard safeguards
- **Level 2**: Tool-using agent → Enhanced logging, approval workflows
- **Level 3**: Autonomous operations → Comprehensive audit, strict boundaries
- **Level 4**: Multi-agent coordination → Formal verification, cryptographic signing

---

## Implementation Roadmap

### Week 1-2: Security Foundation
- Deploy Docker stack with autoheal
- Install LLM Guard, wrap all Ollama calls
- Implement structured JSON-L logging
- Add canary tokens, rate limiting
- Test with NVIDIA Garak vulnerability scanner

### Week 3-4: Pulse State System
- Design state schema
- Build ChromaDB integration for semantic memory
- Create briefing generator
- Implement MCP server exposing state
- Build context injection pipeline

### Month 2: Gatekeeper and Permissions
- Implement capability-based permission system
- Define initial capability YAML
- Build gatekeeper service
- Add action classification (green/yellow/red)
- Deploy Loki + Grafana for audit logging

### Month 3+: Self-Healing and Optimization
- Deploy NeMo Guardrails for dialog-level control
- Implement circuit breaker patterns
- Add anomaly detection for behavioral drift
- Build self-diagnostic dashboards

---

## Tool Summary

| Category | Tool | Purpose | Time |
|----------|------|---------|------|
| Input/Output Security | **LLM Guard** | Prompt injection, PII, secrets | 1-2 days |
| Dialog Control | **NeMo Guardrails** | Topic boundaries, jailbreaks | 3-5 days |
| Container Healing | **Docker Autoheal** | Restart unhealthy containers | 1 hour |
| Process Monitoring | **Monit** | Health checks, auto-restart | 1 day |
| AI Interoperability | **MCP + mcphost** | Universal tool/state protocol | 2-3 days |
| Vector Memory | **ChromaDB** | Semantic search, context | Already deployed |
| Secrets Management | **HashiCorp Vault** | API key storage, injection | 2-3 days |
| Audit Logging | **Loki + Grafana** | Centralized logs, dashboards | 1-2 days |
| Vulnerability Testing | **Garak** | Red-team your defenses | Ongoing |
| DNS Filtering | **Pi-hole** | Block malicious domains | Already deployed |

---

## Key Architectural Principles

1. **Defense in depth**: No single layer catches everything
2. **Layered autonomy**: Green/yellow/red action classification
3. **Grounded in truth**: Every AI interaction receives current system state
4. **Observable by design**: Log everything in structured format
5. **Proportional protection**: Security scales with capabilities

---

*The foundation for FAITHH's immune system is achievable in 2-4 weeks of focused implementation.*
