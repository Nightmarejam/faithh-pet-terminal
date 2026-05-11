# Building Pulse: An AI immune system for FAITHH

Your personal AI assistant needs what biological organisms evolved over millions of years: a sophisticated immune system that detects threats, heals damage, and maintains awareness of its own state. This research reveals that the tooling for building such a system has reached remarkable maturity in 2025—**most of what you need exists as open-source components ready for integration**, with the Model Context Protocol (MCP) emerging as the connective standard that ties everything together.

The architecture that emerges from this research is **defense-in-depth with layered autonomy**: prompt injection scanners at the perimeter, capability-based gatekeepers controlling access, self-healing infrastructure for resilience, and a shared state system that grounds any AI (local or cloud) in live system truth.

## The four pillars of an AI immune system

Pulse needs to function across four integrated layers, each addressing a distinct failure mode. **Prompt injection and adversarial attacks** represent external threats—malicious inputs designed to hijack your AI's behavior. **Infrastructure failures** represent internal breakdowns—crashed services, corrupted state, resource exhaustion. **Context drift and hallucination** represent epistemic failures—when AI loses touch with ground truth. **Excessive autonomy** represents control failures—when AI takes actions beyond its authority.

The tools for each layer have different maturity levels. Security tooling like **LLM Guard** and **NeMo Guardrails** is production-ready today. Self-healing patterns from Kubernetes have been adapted for smaller deployments through tools like **Monit** and **Docker Autoheal**. MCP standardization is accelerating rapidly with adoption by OpenAI, Google, and Anthropic. The remaining gap is integration—connecting these components into a coherent system.

## Practical tools for immediate deployment

### Prompt injection defense with LLM Guard

LLM Guard from ProtectAI represents the fastest path to basic security. Install with `pip install llm-guard` and you gain input scanners for prompt injection, PII detection, toxicity filtering, and secrets detection—all running locally without external API calls. The library adds approximately **0.9 seconds latency per scan** on consumer hardware, acceptable for most personal assistant use cases.

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

For deeper protection, **Vigil-LLM** adds canary tokens—invisible markers injected into prompts that trigger alerts if they appear in outputs, indicating the AI was tricked into revealing system instructions. This technique catches attacks that bypass classifier-based detection.

**NeMo Guardrails** provides the most comprehensive framework, using a domain-specific language called Colang to define conversation boundaries. It integrates directly with Ollama and enables dialog-level control: defining what topics are permitted, what responses are forbidden, and how to handle edge cases. The investment is higher (medium setup complexity) but the protection is significantly more sophisticated.

### Self-healing infrastructure through Docker Autoheal

The critical insight for homelab-scale self-healing: **Docker's restart policies don't restart unhealthy containers—they only restart on process exit**. A service that's alive but unresponsive stays stuck. The solution is the **willfarrell/autoheal** container:

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
    image: ollama/ollama:latest
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 3
    labels:
      - "autoheal=true"
```

Autoheal monitors container health status and restarts any container that fails its healthcheck—bridging Docker's missing capability. For services running outside Docker (native WSL2 processes), **Monit** provides equivalent functionality with HTTP/TCP health probes, CPU/memory monitoring, and automatic restart with configurable thresholds.

### MCP as the universal connector

The Model Context Protocol has become the **de facto standard for AI tool integration** since Anthropic's November 2024 release. OpenAI, Google DeepMind, Replit, and Sourcegraph have all adopted it. For FAITHH, MCP means you can expose system state, tools, and capabilities through a single protocol that any AI—local Ollama or cloud Claude—can consume identically.

The `mcphost` tool (Go-based, install via `go install github.com/mark3labs/mcphost@latest`) connects Ollama to MCP servers. Your Pulse system becomes an MCP server exposing:

- **State query tools**: Current system health, recent actions, active tasks
- **Memory search tools**: Semantic search over ChromaDB
- **Action logging tools**: Record what any AI does for audit

```json
{
  "mcpServers": {
    "pulse-state": {
      "command": "python",
      "args": ["-m", "uvicorn", "pulse_mcp:app", "--port", "8001"]
    },
    "filesystem": {
      "command": "npx", 
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/data"]
    }
  }
}
```

This architecture means when you switch from local Ollama to cloud Claude for complex tasks, both receive identical context through the same MCP interface. No custom integration per model.

## Ground truth architecture for multi-AI coordination

The core innovation Pulse needs is a **state briefing system** that any AI can consume to understand current reality. This prevents the hallucination and context drift that occurs when AI operates without grounding.

### State schema design

A versioned JSON schema captures everything an AI needs to know:

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
  ],
  "entity_registry": {
    "project-alpha": {"type": "project", "last_mentioned": "...", "status": "active"}
  }
}
```

The briefing generator transforms this into markdown that any AI can parse:

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

## Active Tasks
- [HIGH] task-001: Research prompt injection (60% complete)
```

### Context injection patterns

Inject this briefing into every AI interaction using structured delimiters:

```python
def inject_context(user_query: str) -> str:
    briefing = pulse.get_current_briefing()
    return f"""<system_state>
{briefing}
</system_state>

<user_query>
{user_query}
</user_query>

Respond based on the system state provided. If information is unavailable, say so explicitly."""
```

Research shows **less context is often better**—optimal to provide minimal necessary grounding rather than overwhelming the context window. Implement tiered memory: current conversation in-context, recent sessions in ChromaDB for retrieval, historical archives compressed and stored on NAS.

## Security architecture with capability-based permissions

### The gatekeeper pattern

Every AI action passes through a central gatekeeper that checks permissions before execution. Define capabilities in YAML:

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

The gatekeeper checks every tool call against this policy:

```python
class Gatekeeper:
    def check_permission(self, action: str, resource: str) -> bool:
        capability = self.capabilities.get(action)
        if not capability:
            return False
        if capability.requires_approval:
            return self.request_human_approval(action, resource)
        return self.evaluate_policy(capability, resource)
```

### Action classification for scaled human oversight

Not every action needs human approval—that would make the system unusable. Classify actions into three tiers:

- **Green-light actions**: Read-only, no side effects → Execute automatically
- **Yellow-light actions**: Reversible modifications → Execute with async notification, revocable
- **Red-light actions**: Financial, permanent, or security-sensitive → Explicit approval required

This pattern from AWS Security lets AI operate autonomously on routine tasks while maintaining human control over consequential decisions. Track approval patterns over time—actions with consistent approval can graduate to lower tiers.

### Secrets management without exposure

AI should never see raw API keys. The **proxy injection pattern** keeps secrets server-side:

```python
class SecretInjectingProxy:
    async def proxy_request(self, request, secret_path: str):
        # Get secret from Vault—AI never sees this
        secret = await self.vault.read(secret_path)
        request.headers["Authorization"] = f"Bearer {secret['api_key']}"
        return await self.forward(request)
```

For homelab scale, HashiCorp Vault runs in development mode in Docker. For even simpler setups, **SOPS** with age encryption provides file-level secret management that integrates with git.

## Long-term architectural patterns

### The artificial immune system paradigm

Academic research on Artificial Immune Systems (AIS) provides the conceptual framework for Pulse. The **Negative Selection Algorithm** establishes "self" (normal operation patterns) and flags anything that deviates as potential "non-self" (anomaly). The **Danger Theory** approach focuses on stress signals—high latency, elevated error rates, unusual action sequences—rather than trying to enumerate all possible threats.

For practical implementation, this means:

1. **Establish baselines** for normal operation (response times, error rates, capability usage patterns)
2. **Monitor for deviations** using statistical process control
3. **Adaptive learning** refines detection based on confirmed issues versus false positives

Gartner's Digital Immune System framework operationalizes this: observability provides visibility, chaos engineering discovers vulnerabilities proactively, auto-remediation handles routine failures, and SRE practices govern reliability targets.

### Constitutional AI for self-governance

Anthropic's Constitutional AI offers a model for AI systems that can **evaluate their own behavior against explicit principles**. Rather than relying solely on external monitoring, the AI internalizes a "constitution" of permitted and forbidden behaviors.

For FAITHH, this could manifest as:

```
FAITHH Constitution:
1. Always verify actions against current system state before execution
2. Never modify files outside designated workspace without explicit approval
3. Refuse requests that could expose secrets or credentials
4. When uncertain, ask for clarification rather than guessing
5. Log all actions for audit trail
```

The AI references these principles when evaluating its own outputs, providing an inner layer of defense that complements external guardrails.

### Responsible scaling for growing capabilities

As FAITHH gains more capabilities, security should scale proportionally. The pattern from Anthropic's Responsible Scaling Policy:

- **Level 1**: Basic assistant (current) → Standard safeguards
- **Level 2**: Tool-using agent → Enhanced logging, approval workflows  
- **Level 3**: Autonomous operations → Comprehensive audit, strict capability boundaries
- **Level 4**: Multi-agent coordination → Formal verification, cryptographic action signing

Define **tripwires**—capability thresholds that trigger security upgrades. If FAITHH starts handling financial transactions, that triggers red-light classification for all financial tools. If it gains code execution, that triggers sandboxing requirements.

## Implementation roadmap

### Week 1-2: Security foundation

**Day 1-2**: Deploy Docker Compose stack with Ollama, ChromaDB, and autoheal. Add health checks to all containers.

**Day 3-4**: Install LLM Guard and wrap all Ollama calls with input/output scanning. Configure prompt injection detection at threshold 0.5 (tune based on false positive rate).

**Day 5-7**: Implement basic structured logging in JSON-L format. Capture timestamp, action type, result, and session ID for every AI interaction.

**Week 2**: Add canary tokens using Vigil's approach. Implement rate limiting. Test your defenses using NVIDIA's Garak vulnerability scanner.

### Week 3-4: Pulse state system

**Day 8-10**: Design state schema. Build ChromaDB integration for semantic memory. Create the briefing generator that produces markdown summaries.

**Day 11-12**: Implement MCP server exposing state query and memory search tools. Test with mcphost connecting Ollama to your state server.

**Day 13-14**: Build context injection pipeline that adds current briefing to every AI prompt. Validate that AI responses reference actual system state.

### Month 2: Gatekeeper and permissions

**Week 5-6**: Implement capability-based permission system. Define initial capability YAML. Build the gatekeeper service that checks permissions before tool execution.

**Week 7-8**: Add action classification (green/yellow/red). Implement approval workflow for red-light actions. Deploy Loki + Grafana for centralized audit logging.

### Month 3+: Self-healing and optimization

Deploy NeMo Guardrails for dialog-level control. Implement circuit breaker patterns for external service dependencies. Add anomaly detection for behavioral drift. Build self-diagnostic dashboards showing system health, action success rates, and approval patterns over time.

## The key architectural principles

**Defense in depth**: No single layer catches everything. Combine input scanning, dialog guardrails, capability permissions, output filtering, and audit logging. Each layer catches what others miss.

**Layered autonomy**: Green-light actions execute freely, yellow-light actions are logged for review, red-light actions require approval. This lets AI be useful while maintaining meaningful human control.

**Grounded in truth**: Every AI interaction receives current system state. This prevents hallucination about what's running, what's healthy, and what actions are available.

**Observable by design**: Log everything. You can't fix what you can't see. Structured JSON logging with correlation IDs lets you trace any problem to its source.

**Proportional protection**: As capabilities grow, security scales. Start simple, add complexity as needed. The roadmap builds foundation first, sophistication later.

The ecosystem has matured remarkably. **LLM Guard, MCP, Docker Autoheal, and ChromaDB** provide the core building blocks. What remains is integration—connecting these components into the coherent immune system that Pulse represents. The patterns exist; the implementation is engineering.

---

## Tool summary for FAITHH/Pulse

| Category | Recommended Tool | Purpose | Implementation Time |
|----------|-----------------|---------|---------------------|
| Input/Output Security | **LLM Guard** | Prompt injection, PII, secrets detection | 1-2 days |
| Dialog Control | **NeMo Guardrails** | Topic boundaries, jailbreak prevention | 3-5 days |
| Container Self-Healing | **Docker Autoheal** | Restart unhealthy containers | 1 hour |
| Process Monitoring | **Monit** | Health checks, automatic restart | 1 day |
| AI Interoperability | **MCP + mcphost** | Universal tool/state protocol | 2-3 days |
| Vector Memory | **ChromaDB** | Semantic search, context retrieval | Already deployed |
| Secrets Management | **HashiCorp Vault** | API key storage, injection | 2-3 days |
| Audit Logging | **Loki + Grafana** | Centralized logs, dashboards | 1-2 days |
| Vulnerability Testing | **Garak** | Red-team your defenses | Ongoing |
| DNS Filtering | **Pi-hole** | Block malicious domains for AI browsing | 1-2 hours |

The foundation for FAITHH's immune system is achievable in 2-4 weeks of focused implementation. The long-term sophistication—self-healing ML, Constitutional AI principles, formal capability verification—builds on that foundation over the following months.