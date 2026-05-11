"""
FAITHH PULSE Observer — Connects ALIFE simulation to ChromaDB for semantic logging.

Every meaningful event in the simulation is logged with natural language descriptions
that FAITHH can search semantically, reason about, and use to model its own behavior.
"""

import os
import chromadb
from datetime import datetime
from typing import Dict, List, Optional, Any

# Genome slot to op name mappings (by category)
SENSE_OPS = {
    0x00: "SENSE_ENERGY", 0x01: "SENSE_THREAT", 0x02: "SENSE_LIGHT",
    0x03: "SENSE_NEIGHBOR", 0x04: "SENSE_DENSITY", 0x05: "SENSE_SELF",
    0x06: "SENSE_GRADIENT", 0x07: "SENSE_AGE",
}

PROCESS_OPS = {
    0x00: "PROC_THRESHOLD", 0x01: "PROC_COMPARE", 0x02: "PROC_MEMORY_CMP",
    0x03: "PROC_TREND", 0x04: "PROC_PREDICT", 0x05: "PROC_BEAT",
    0x06: "PROC_AVERAGE", 0x07: "PROC_INVERT",
}

MEMORY_OPS = {
    0x00: "MEM_NONE", 0x01: "MEM_LAST1", 0x02: "MEM_LAST4",
    0x03: "MEM_LAST8", 0x04: "MEM_BEST", 0x05: "MEM_WORST",
    0x06: "MEM_PATTERN", 0x07: "MEM_DUAL",
}

ACT_OPS = {
    0x00: "ACT_IDLE", 0x01: "ACT_MOVE", 0x02: "ACT_CONSUME",
    0x03: "ACT_SHIELD", 0x04: "ACT_REPRODUCE", 0x05: "ACT_SIGNAL",
    0x06: "ACT_TOXIN", 0x07: "ACT_FLEE",
}

REGULATE_OPS = {
    0x00: "REG_NONE", 0x01: "REG_CONSERVE", 0x02: "REG_BURST",
    0x03: "REG_CYCLE", 0x04: "REG_LEARN", 0x05: "REG_SUPPRESS",
    0x06: "REG_PRIORITIZE", 0x07: "REG_ADAPTIVE",
}


class PulseWatcher:
    """Observes ALIFE simulation and logs events to ChromaDB for FAITHH semantic search."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize connection to ChromaDB.
        
        Args:
            config_path: Path to config file (uses env vars for ChromaDB connection)
        """
        self.connected = False
        self.collection = None
        self.event_counter = 0
        self.seen_genomes: set = set()  # Track unique genomes for novelty detection
        
        # ChromaDB connection from environment (same pattern as FAITHH backend)
        chroma_host = os.environ.get("CHROMA_HOST", "192.158.1.243")
        chroma_port = int(os.environ.get("CHROMA_PORT", 8000))
        collection_name = "alife_lineage"
        
        try:
            self.client = chromadb.HttpClient(host=chroma_host, port=chroma_port)
            
            # Get or create the alife_lineage collection
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"description": "ALIFE simulation lineage and event data"}
            )
            
            self.connected = True
            print(f"[PULSE] Connected to ChromaDB at {chroma_host}:{chroma_port}")
            print(f"[PULSE] Collection '{collection_name}': {self.collection.count()} documents")
        except Exception as e:
            self.connected = False
            print(f"[PULSE] ChromaDB connection failed (non-fatal): {e}")
    
    def _genome_to_hex(self, genome: bytes) -> str:
        """Convert genome bytes to readable hex string."""
        return " ".join(f"{b:02X}" for b in genome)
    
    def _genome_to_readable(self, genome: bytes) -> str:
        """Convert genome bytes to readable op names.
        
        Genome structure: [S0][S1][P0][P1][M0][A0][A1][R0]
        """
        if len(genome) != 8:
            return "INVALID_GENOME"
        
        parts = [
            SENSE_OPS.get(genome[0], f"SENSE_{genome[0]:02X}"),
            SENSE_OPS.get(genome[1], f"SENSE_{genome[1]:02X}"),
            PROCESS_OPS.get(genome[2], f"PROC_{genome[2]:02X}"),
            PROCESS_OPS.get(genome[3], f"PROC_{genome[3]:02X}"),
            MEMORY_OPS.get(genome[4], f"MEM_{genome[4]:02X}"),
            ACT_OPS.get(genome[5], f"ACT_{genome[5]:02X}"),
            ACT_OPS.get(genome[6], f"ACT_{genome[6]:02X}"),
            REGULATE_OPS.get(genome[7], f"REG_{genome[7]:02X}"),
        ]
        return " ".join(parts)
    
    def _characterize_agent(self, agent) -> str:
        """Generate plain English behavioral characterization of agent.
        
        Returns a complete sentence describing the agent's behavioral sophistication.
        """
        genome = agent.genome
        m0 = genome[4]  # Memory op
        p0, p1 = genome[2], genome[3]  # Process ops
        r0 = genome[7]  # Regulate op
        
        characterizations = []
        
        # Memory characterization
        if m0 == 0x00:  # MEM_NONE
            characterizations.append(
                "This agent is behaving reactively — it has no memory and cannot anticipate future states."
            )
        elif m0 in [0x01, 0x02, 0x03]:  # MEM_LAST1, MEM_LAST4, MEM_LAST8
            characterizations.append(
                "This agent has short-term memory and may be developing pattern recognition."
            )
        elif m0 == 0x06:  # MEM_PATTERN
            characterizations.append(
                "This agent stores threat encounter patterns — it has the prerequisites for anticipatory behavior."
            )
        elif m0 == 0x07:  # MEM_HYBRID
            if p0 == 0x04 or p1 == 0x04:  # PROC_PREDICT
                characterizations.append(
                    "This agent has both pattern memory and predictive processing — anticipatory behavior is possible in this lineage."
                )
            else:
                characterizations.append(
                    "This agent has hybrid memory but lacks predictive processing."
                )
        
        # Regulation characterization
        if r0 == 0x04:  # REG_LEARN
            characterizations.append(
                "This agent's regulation is adaptive — it develops metabolic efficiency for frequently used behaviors."
            )
        
        return " ".join(characterizations) if characterizations else "This agent has standard behavioral patterns."
    
    def _build_document(self, event_type: str, agent, world, tick: int, extra: Optional[Dict] = None) -> str:
        """Build natural language document string for ChromaDB.
        
        This is the critical field — FAITHH will search this semantically.
        """
        genome_readable = self._genome_to_readable(agent.genome)
        characterization = self._characterize_agent(agent)
        cell_energy = world.get_cell_energy(agent.x, agent.y) if hasattr(world, 'get_cell_energy') else 0
        
        if event_type == "reproduction":
            return (
                f"Agent {agent.id} at generation {agent.generation} reproduced at tick {tick}. "
                f"Its genome expresses {genome_readable.lower().replace('_', ' ')}. "
                f"Parent energy at moment of reproduction was {agent.energy}. "
                f"The world energy at its location was {cell_energy}. "
                f"{characterization}"
            )
        
        elif event_type == "death_starvation":
            lifetime = agent.age
            peak_energy = getattr(agent, 'peak_energy', agent.energy)
            return (
                f"Agent {agent.id} died at tick {tick} from starvation after {lifetime} ticks alive. "
                f"Its genome expressed {genome_readable.lower().replace('_', ' ')}. "
                f"{characterization} "
                f"Final energy was {agent.energy}. Peak energy during lifetime was {peak_energy}."
            )
        
        elif event_type == "death_predator":
            lifetime = agent.age
            energy_before = extra.get("energy_before", 0) if extra else 0
            return (
                f"Agent {agent.id} died at tick {tick} from predator contact at generation {agent.generation}. "
                f"It did not have ACT_SHIELD active. Energy at death: 0 (from {energy_before} before "
                f"predator contact — lethal damage). This lineage ends here. "
                f"Genome lacked shield protection: {genome_readable.lower().replace('_', ' ')}. "
                f"{characterization}"
            )
        
        elif event_type == "shield_activation":
            shield_activations = getattr(agent, 'shield_activations', 0)
            return (
                f"Agent {agent.id} activated its Shield trait at tick {tick} generation {agent.generation}. "
                f"Predator wave contact imminent — agent at column {agent.x}. "
                f"Shield cost: 1 energy/tick. Agent energy before shield: {agent.energy}. "
                f"This is shield activation #{shield_activations + 1} for this agent. "
                f"This agent is behaving reactively — shield fires on threat contact, not in anticipation of it. "
                f"Genome: {genome_readable.lower().replace('_', ' ')}."
            )
        
        elif event_type == "flag_novel_genome":
            reason = extra.get("reason", "unknown") if extra else "unknown"
            return (
                f"Novel genome variant detected at tick {tick}. "
                f"Agent {agent.id} at generation {agent.generation} carries a genome not seen in any ancestor: "
                f"{genome_readable.lower().replace('_', ' ')}. "
                f"{reason} "
                f"{characterization}"
            )
        
        elif event_type == "flag_intent":
            gap = extra.get("anticipation_gap", 0) if extra else 0
            return (
                f"Anticipation gap event at tick {tick}. "
                f"Agent {agent.id} showed anticipation gap of {gap}. "
                f"Its genome expresses {genome_readable.lower().replace('_', ' ')}. "
                f"{characterization}"
            )
        
        elif event_type == "thermal_death":
            lifetime = agent.age
            avg_light = extra.get("avg_light", 0) if extra else 0
            has_disruption = extra.get("has_disruption", False) if extra else False
            return (
                f"Agent {agent.id} at generation {agent.generation} died at tick {tick} from thermal drain. "
                f"Occupied cells averaging light level {avg_light:.0f} for {lifetime} ticks "
                f"{'with' if has_disruption else 'without'} Disruption trait protection. "
                f"Genome: {genome_readable.lower().replace('_', ' ')}. "
                f"This agent was pursuing Strategy {'C (Disruption)' if has_disruption else 'A or B'} but thermal "
                f"pressure exceeded its behavioral avoidance capacity. Lineage ends here."
            )
        
        elif event_type == "disruption_emergence":
            pct = extra.get("disruption_pct", 0) if extra else 0
            return (
                f"Disruption phenotype confirmed in agent {agent.id} at generation {agent.generation} "
                f"tick {tick}. Genome carries SENSE_LIGHT in S0/S1 and ACT_SHIELD in A0/A1 — "
                f"addressing both predator and thermal pressure simultaneously. "
                f"Current thermal drain reduction: 70%. Predator wave protection: full. "
                f"This is Strategy C — the dual-purpose Stripe analog. "
                f"Population Strategy C frequency at emergence: {pct:.1f}%."
            )
        
        elif event_type == "strategy_snapshot":
            pct_a = extra.get("pct_a", 0) if extra else 0
            pct_b = extra.get("pct_b", 0) if extra else 0
            pct_c = extra.get("pct_c", 0) if extra else 0
            pct_u = extra.get("pct_u", 0) if extra else 0
            total = extra.get("total", 0) if extra else 0
            avg_gen = extra.get("avg_gen", 0) if extra else 0
            dominant = extra.get("dominant", "balanced") if extra else "balanced"
            return (
                f"Strategy distribution at tick {tick} generation {avg_gen:.1f}: "
                f"Strategy A (Shield only): {pct_a:.1f}% — predator defense, thermal vulnerable. "
                f"Strategy B (Thermal avoidance): {pct_b:.1f}% — thermal adapted, predator vulnerable. "
                f"Strategy C (Disruption): {pct_c:.1f}% — dual-purpose protection. "
                f"Unspecialized: {pct_u:.1f}%. Total population: {total}. "
                f"Dominant pressure this interval: {dominant}."
            )
        
        elif event_type == "flag_intent":
            gap = extra.get("gap", 0) if extra else 0
            detection_tick = extra.get("detection_tick", tick) if extra else tick
            shield_tick = extra.get("shield_tick", tick) if extra else tick
            warning_ticks = extra.get("warning_ticks", 0) if extra else 0
            position_score = extra.get("position_score", 0) if extra else 0
            memory_op = extra.get("memory_op", "MEM_NONE") if extra else "MEM_NONE"
            return (
                f"INTENT EMERGENCE EVENT at tick {tick} generation {agent.generation}. "
                f"Agent {agent.id} activated Shield at tick {shield_tick} — "
                f"{abs(gap)} ticks BEFORE wave entered its detection range at tick {detection_tick}. "
                f"Position: column {agent.x} of 160. Positional warning available: {warning_ticks:.1f} ticks. "
                f"Position-adjusted gap score: {position_score:.3f}. "
                f"This agent modeled a future threat state rather than reacting to a detected one. "
                f"Genome: {genome_readable.lower().replace('_', ' ')}. Memory op: {memory_op}. "
                f"{characterization}"
            )
        
        elif event_type == "wave_detection":
            front_col = extra.get("front_col", 0) if extra else 0
            warning_ticks = extra.get("warning_ticks", 0) if extra else 0
            shield_status = extra.get("shield_status", "inactive") if extra else "inactive"
            gap = extra.get("gap", None) if extra else None
            gap_type = "anticipatory" if gap and gap < 0 else "reactive"
            return (
                f"Agent {agent.id} detected approaching wave at tick {tick}. "
                f"Wave front at column {front_col:.1f}, agent at column {agent.x}. "
                f"Positional warning available: {warning_ticks:.1f} ticks. "
                f"Shield status at detection: {shield_status}. "
                f"Gap at this moment: {gap} ticks ({gap_type})."
            )
        
        elif event_type == "memory_emergence":
            old_op = extra.get("old_op", "MEM_NONE") if extra else "MEM_NONE"
            new_op = extra.get("new_op", "unknown") if extra else "unknown"
            memory_count = extra.get("memory_count", 1) if extra else 1
            memory_pct = extra.get("memory_pct", 0) if extra else 0
            return (
                f"Memory capability emerged through mutation in agent {agent.id} "
                f"at generation {agent.generation} tick {tick}. Previous M0: {old_op}. "
                f"New M0: {new_op}. "
                f"This agent now has memory capability. "
                f"It is the {memory_count}th agent in this simulation to carry a memory op. "
                f"Population memory frequency: {memory_pct:.1f}%. "
                f"Whether this memory capability leads to anticipatory behavior depends on "
                f"whether {new_op} combined with process ops can produce predictive output "
                f"before wave detection. Watching this lineage."
            )
        
        elif event_type == "gap_snapshot":
            mean_gap = extra.get("mean_gap", 0) if extra else 0
            min_gap = extra.get("min_gap", 0) if extra else 0
            neg_count = extra.get("neg_count", 0) if extra else 0
            neg_pct = extra.get("neg_pct", 0) if extra else 0
            mem_count = extra.get("mem_count", 0) if extra else 0
            mem_pct = extra.get("mem_pct", 0) if extra else 0
            first_neg_tick = extra.get("first_neg_tick", None) if extra else None
            avg_gen = extra.get("avg_gen", 0) if extra else 0
            gap_type = "anticipatory" if mean_gap < 0 else "reactive"
            return (
                f"Anticipation gap population snapshot at tick {tick} generation {avg_gen:.1f}: "
                f"Mean gap: {mean_gap:.1f} ticks ({gap_type}). "
                f"Most anticipatory agent gap: {min_gap:.1f} ticks. "
                f"Negative gap agents: {neg_count} ({neg_pct:.1f}% of population). "
                f"Memory-carrying agents: {mem_count} ({mem_pct:.1f}% of population). "
                f"{'INTENT EMERGENCE CONFIRMED at tick ' + str(first_neg_tick) + '.' if first_neg_tick else 'No anticipatory behavior observed yet.'}"
            )
        
        elif event_type == "constitutive_shield":
            return (
                f"Constitutive defense detected in agent {agent.id} at tick {tick} "
                f"generation {agent.generation}. "
                f"This agent exhibits constitutive defense — Shield is maintained regardless "
                f"of threat level. This is energetically expensive but provides complete "
                f"protection. Strategy: constitutive (PROC_INVERT on SENSE_THREAT). "
                f"Genome: {genome_readable}. "
                f"{characterization}"
            )
        
        else:
            return (
                f"Event '{event_type}' for agent {agent.id} at tick {tick}. "
                f"Genome: {genome_readable}. Energy: {agent.energy}. "
                f"{characterization}"
            )
    
    def _build_metadata(self, event_type: str, agent, world, tick: int, 
                        flagged: bool = False, flag_reason: str = None,
                        extra: Optional[Dict] = None) -> Dict[str, Any]:
        """Build metadata dict for ChromaDB entry."""
        cell = world.grid[agent.y][agent.x] if hasattr(world, 'grid') else None
        
        metadata = {
            "agent_id": agent.id,
            "generation": agent.generation,
            "experiment": 0,  # Will be parameterized in later experiments
            "tick": tick,
            "genome_hex": self._genome_to_hex(agent.genome),
            "genome_readable": self._genome_to_readable(agent.genome),
            "env_energy": cell.energy if cell else 0,
            "env_threat": cell.threat if cell else 0,
            "env_light": cell.light if cell else 0,
            "agent_energy": agent.energy,
            "anticipation_gap": extra.get("anticipation_gap") if extra else None,
            "intent_score": extra.get("intent_score") if extra else None,
            "event_type": event_type,
            "parent_id": agent.parent_id,
            "flagged": flagged,
            "flag_reason": flag_reason,
            "lifetime_ticks": agent.age,
            "peak_energy": getattr(agent, 'peak_energy', agent.energy),
        }
        
        # ChromaDB doesn't accept None values in metadata - filter them out
        return {k: v for k, v in metadata.items() if v is not None}
    
    def log_event(self, event_type: str, agent, world, tick: int, extra: Optional[Dict] = None) -> None:
        """Log a simulation event to ChromaDB.
        
        Args:
            event_type: Type of event (reproduction, death_starvation, etc.)
            agent: The agent involved in the event
            world: The world state
            tick: Current simulation tick
            extra: Optional extra data for the event
        """
        if not self.connected or self.collection is None:
            return
        
        try:
            self.event_counter += 1
            doc_id = f"alife_{tick}_{event_type}_{agent.id}_{self.event_counter}"
            
            document = self._build_document(event_type, agent, world, tick, extra)
            metadata = self._build_metadata(event_type, agent, world, tick, extra=extra)
            
            self.collection.add(
                ids=[doc_id],
                documents=[document],
                metadatas=[metadata]
            )
            
            # Track genome for novelty detection
            genome_hex = self._genome_to_hex(agent.genome)
            if genome_hex not in self.seen_genomes:
                self.seen_genomes.add(genome_hex)
                # Check if this is a novel variant worth flagging
                if agent.generation > 0:  # Not initial population
                    self._check_novel_genome(agent, world, tick)
                    
        except Exception as e:
            print(f"[PULSE] Observer error (non-fatal): {e}")
    
    def _check_novel_genome(self, agent, world, tick: int) -> None:
        """Check if agent has a novel genome variant worth flagging."""
        genome = agent.genome
        
        # Check for first appearance of key ops
        novel_reasons = []
        
        # PROC_PREDICT (0x04) - prerequisite for anticipatory behavior
        if genome[2] == 0x04 or genome[3] == 0x04:
            novel_reasons.append("This is the first appearance of PROC_PREDICT in any lineage — the prerequisite for anticipatory behavior.")
        
        # MEM_PATTERN (0x06) or MEM_HYBRID (0x07) - memory sophistication
        if genome[4] in [0x06, 0x07]:
            novel_reasons.append("This lineage has developed sophisticated memory patterns.")
        
        # REG_LEARN (0x04) - adaptive regulation
        if genome[7] == 0x04:
            novel_reasons.append("This lineage has developed adaptive regulation.")
        
        if novel_reasons:
            self.flag_event(
                reason=" ".join(novel_reasons),
                agent=agent,
                world=world,
                tick=tick,
                extra={"reason": " ".join(novel_reasons)}
            )
    
    def flag_event(self, reason: str, agent, world, tick: int, extra: Optional[Dict] = None) -> None:
        """Flag an event for special attention.
        
        Args:
            reason: Why this event is being flagged
            agent: The agent involved
            world: The world state
            tick: Current simulation tick
            extra: Optional extra data
        """
        if not self.connected or self.collection is None:
            return
        
        try:
            self.event_counter += 1
            doc_id = f"alife_{tick}_flag_{agent.id}_{self.event_counter}"
            
            document = self._build_document("flag_novel_genome", agent, world, tick, extra)
            metadata = self._build_metadata(
                "flag_novel_genome", agent, world, tick,
                flagged=True, flag_reason=reason, extra=extra
            )
            
            self.collection.add(
                ids=[doc_id],
                documents=[document],
                metadatas=[metadata]
            )
            
        except Exception as e:
            print(f"[PULSE] Observer flag error (non-fatal): {e}")
    
    def snapshot_population(self, agents: Dict, world, tick: int) -> None:
        """Log a population snapshot every N ticks.
        
        Args:
            agents: Dict of all agents (from world.agents)
            world: The world state
            tick: Current simulation tick
        """
        if not self.connected or self.collection is None:
            return
        
        try:
            alive_agents = [a for a in agents.values() if a.alive]
            population = len(alive_agents)
            
            if population == 0:
                avg_energy = 0
            else:
                avg_energy = sum(a.energy for a in alive_agents) / population
            
            # Count unique genomes
            unique_genomes = len(set(self._genome_to_hex(a.genome) for a in alive_agents))
            
            self.event_counter += 1
            doc_id = f"alife_{tick}_snapshot_{self.event_counter}"
            
            document = (
                f"Population snapshot at tick {tick}: {population} agents alive, "
                f"average energy {avg_energy:.1f}. "
                f"Population has {unique_genomes} unique genome variants. "
                f"{'Population is stable near carrying capacity.' if 200 <= population <= 400 else ''} "
                f"{'Population is below carrying capacity.' if population < 200 else ''} "
                f"{'Population is above carrying capacity.' if population > 400 else ''}"
            )
            
            metadata = {
                "event_type": "population_snapshot",
                "tick": tick,
                "population": population,
                "avg_energy": round(avg_energy, 1),
                "unique_genomes": unique_genomes,
                "experiment": 0,
                "flagged": False,
            }
            
            self.collection.add(
                ids=[doc_id],
                documents=[document],
                metadatas=[metadata]
            )
            
        except Exception as e:
            print(f"[PULSE] Observer snapshot error (non-fatal): {e}")
    
    def log_trait_frequency(self, agents: list, world, tick: int, 
                            shield_freq: float, avg_generation: float) -> None:
        """Log Shield trait frequency snapshot for Experiment 1+.
        
        Args:
            agents: List of alive agents
            world: The world state
            tick: Current simulation tick
            shield_freq: Percentage of population with Shield trait
            avg_generation: Average generation of population
        """
        if not self.connected or self.collection is None:
            return
        
        try:
            population = len(agents)
            
            # Determine trend
            if shield_freq > 50:
                trend = "Selection pressure is working — shielded lineages surviving predator waves at higher rates."
            elif shield_freq > 20:
                trend = "Shield trait is spreading but has not yet reached majority."
            elif shield_freq > 5:
                trend = "Shield trait is present but rare — selection pressure may be insufficient."
            else:
                trend = "Shield trait is nearly absent — either no mutations or strong counter-selection."
            
            self.event_counter += 1
            doc_id = f"alife_{tick}_trait_freq_{self.event_counter}"
            
            document = (
                f"Shield trait frequency snapshot at tick {tick} generation {avg_generation:.1f}: "
                f"{shield_freq:.1f}% of population carries ACT_SHIELD in A0 or A1. "
                f"{trend}"
            )
            
            metadata = {
                "event_type": "trait_frequency_snapshot",
                "tick": tick,
                "population": population,
                "shield_frequency": round(shield_freq, 1),
                "avg_generation": round(avg_generation, 1),
                "experiment": 1,
                "flagged": False,
            }
            
            self.collection.add(
                ids=[doc_id],
                documents=[document],
                metadatas=[metadata]
            )
            
        except Exception as e:
            print(f"[PULSE] Observer trait frequency error (non-fatal): {e}")
    
    def log_strategy_snapshot(self, tick: int, pct_a: float, pct_b: float, pct_c: float,
                              total: int, world, avg_gen: float = 0.0) -> None:
        """Log strategy distribution snapshot for Experiment 2.
        
        Args:
            tick: Current simulation tick
            pct_a: Percentage with Strategy A (Shield only)
            pct_b: Percentage with Strategy B (Thermal avoidance)
            pct_c: Percentage with Strategy C (Disruption)
            total: Total population
            world: The world state
            avg_gen: Average generation of population
        """
        if not self.connected or self.collection is None:
            return
        
        try:
            pct_u = 100.0 - pct_a - pct_b - pct_c
            
            # Determine dominant pressure
            if pct_a > pct_b and pct_a > pct_c:
                dominant = "predator"
            elif pct_b > pct_a and pct_b > pct_c:
                dominant = "thermal"
            elif pct_c > pct_a and pct_c > pct_b:
                dominant = "balanced (dual-purpose winning)"
            else:
                dominant = "balanced"
            
            self.event_counter += 1
            doc_id = f"alife_{tick}_strategy_{self.event_counter}"
            
            extra = {
                "pct_a": pct_a,
                "pct_b": pct_b,
                "pct_c": pct_c,
                "pct_u": pct_u,
                "total": total,
                "avg_gen": avg_gen,
                "dominant": dominant
            }
            
            # Create a minimal agent-like object for _build_document
            class SnapshotAgent:
                def __init__(self):
                    self.id = "population"
                    self.generation = avg_gen
                    self.genome = bytes([0, 0, 0, 0, 0, 0, 0, 0])
                    self.energy = 0
                    self.age = 0
                    self.x = 0
                    self.y = 0
            
            document = self._build_document("strategy_snapshot", SnapshotAgent(), world, tick, extra)
            
            metadata = {
                "event_type": "strategy_snapshot",
                "tick": tick,
                "population": total,
                "pct_strategy_a": round(pct_a, 1),
                "pct_strategy_b": round(pct_b, 1),
                "pct_strategy_c": round(pct_c, 1),
                "avg_generation": round(avg_gen, 1),
                "experiment": 2,
                "flagged": False,
            }
            
            self.collection.add(
                ids=[doc_id],
                documents=[document],
                metadatas=[metadata]
            )
            
        except Exception as e:
            print(f"[PULSE] Observer strategy snapshot error (non-fatal): {e}")
    
    def log_gap_snapshot(self, agents: dict, world, tick: int, 
                         first_negative_gap: tuple = None) -> None:
        """Log anticipation gap population snapshot for Experiment 3.
        
        Args:
            agents: Dict of agent_id -> Agent
            world: The world state
            tick: Current simulation tick
            first_negative_gap: (tick, agent_id, gap) tuple if observed
        """
        if not self.connected or self.collection is None:
            return
        
        try:
            alive_agents = [a for a in agents.values() if a.alive]
            total = len(alive_agents)
            
            if total == 0:
                return
            
            # Calculate gap statistics
            all_gaps = []
            for agent in alive_agents:
                if agent.anticipation_gaps:
                    all_gaps.extend(agent.anticipation_gaps)
            
            mean_gap = sum(all_gaps) / len(all_gaps) if all_gaps else 0
            min_gap = min(all_gaps) if all_gaps else 0
            neg_count = sum(1 for g in all_gaps if g < 0)
            neg_pct = (neg_count / len(all_gaps) * 100) if all_gaps else 0
            
            # Count memory-carrying agents (M0 slot != 0)
            mem_count = sum(1 for a in alive_agents if a.genome[4] != 0)
            mem_pct = (mem_count / total * 100) if total > 0 else 0
            
            avg_gen = sum(a.generation for a in alive_agents) / total
            
            self.event_counter += 1
            doc_id = f"alife_{tick}_gap_snapshot_{self.event_counter}"
            
            extra = {
                "mean_gap": mean_gap,
                "min_gap": min_gap,
                "neg_count": neg_count,
                "neg_pct": neg_pct,
                "mem_count": mem_count,
                "mem_pct": mem_pct,
                "first_neg_tick": first_negative_gap[0] if first_negative_gap else None,
                "avg_gen": avg_gen
            }
            
            # Create a minimal agent-like object for _build_document
            class SnapshotAgent:
                def __init__(self):
                    self.id = "population"
                    self.generation = avg_gen
                    self.genome = bytes([0, 0, 0, 0, 0, 0, 0, 0])
                    self.energy = 0
                    self.age = 0
                    self.x = 0
                    self.y = 0
            
            document = self._build_document("gap_snapshot", SnapshotAgent(), world, tick, extra)
            
            metadata = {
                "event_type": "gap_snapshot",
                "tick": tick,
                "population": total,
                "mean_gap": round(mean_gap, 1),
                "min_gap": round(min_gap, 1),
                "negative_gap_count": neg_count,
                "negative_gap_pct": round(neg_pct, 1),
                "memory_count": mem_count,
                "memory_pct": round(mem_pct, 1),
                "avg_generation": round(avg_gen, 1),
                "experiment": 3,
                "flagged": first_negative_gap is not None,
            }
            
            self.collection.add(
                ids=[doc_id],
                documents=[document],
                metadatas=[metadata]
            )
            
        except Exception as e:
            print(f"[PULSE] Observer gap snapshot error (non-fatal): {e}")
    
    def flag_intent(self, agent, world, tick: int, gap: float, 
                    wave_speed: float = 0.8) -> None:
        """Log the critical INTENT EMERGENCE event — first negative gap.
        
        This is the most important event in the entire project.
        """
        if not self.connected or self.collection is None:
            return
        
        try:
            from config import SENSE_THREAT_RANGE
            
            # Calculate position warning
            position_warning = (agent.x - SENSE_THREAT_RANGE) / wave_speed
            position_warning = max(1, position_warning)
            position_score = gap / position_warning
            
            # Get memory op name
            MEM_OPS = ["MEM_NONE", "MEM_LAST1", "MEM_LAST4", "MEM_AVG", 
                       "MEM_DELTA", "MEM_PEAK", "MEM_TREND", "MEM_PATTERN"]
            memory_op = MEM_OPS[agent.genome[4]] if agent.genome[4] < len(MEM_OPS) else "UNKNOWN"
            
            self.event_counter += 1
            doc_id = f"alife_{tick}_intent_{self.event_counter}"
            
            extra = {
                "gap": gap,
                "detection_tick": agent.wave_detection_tick,
                "shield_tick": agent.last_shield_activation,
                "warning_ticks": position_warning,
                "position_score": position_score,
                "memory_op": memory_op
            }
            
            document = self._build_document("flag_intent", agent, world, tick, extra)
            
            metadata = {
                "event_type": "flag_intent",
                "tick": tick,
                "agent_id": agent.id,
                "generation": agent.generation,
                "gap": round(gap, 1),
                "position_adjusted_gap": round(position_score, 3),
                "memory_op": memory_op,
                "genome_hex": self._genome_to_hex(agent.genome),
                "experiment": 3,
                "flagged": True,
                "flag_reason": "INTENT_EMERGENCE"
            }
            
            self.collection.add(
                ids=[doc_id],
                documents=[document],
                metadatas=[metadata]
            )
            
            print(f"[PULSE] *** INTENT EMERGENCE LOGGED: agent {agent.id} gap={gap} ***")
            
        except Exception as e:
            print(f"[PULSE] Observer flag_intent error (non-fatal): {e}")
    
    def log_zone_entry(self, agent, old_zone: str, new_zone: str, tick: int, 
                       intent_score: float = 0.0) -> None:
        """Log when agent crosses zone boundary (Exp 4+).
        
        Args:
            agent: The agent crossing zones
            old_zone: Previous zone ('left', 'center', 'right')
            new_zone: New zone
            tick: Current simulation tick
            intent_score: Agent's current intent score (neg gap ratio)
        """
        if not self.connected or self.collection is None:
            return
        
        try:
            self.event_counter += 1
            doc_id = f"alife_{tick}_zone_entry_{agent.id}_{self.event_counter}"
            
            document = (
                f"Agent {agent.id} crossed zone boundary at tick {tick} generation {agent.generation}. "
                f"Moved from {old_zone} zone to {new_zone} zone. "
                f"Intent score at crossing: {intent_score:.3f}. "
                f"Genome: {self._genome_to_readable(agent.genome)}. "
                f"{'Entering interference zone — dual-source prediction required.' if new_zone == 'center' else ''}"
                f"{'Leaving interference zone — single-source prediction sufficient.' if old_zone == 'center' else ''}"
            )
            
            metadata = {
                "event_type": "zone_entry",
                "tick": tick,
                "agent_id": agent.id,
                "generation": agent.generation,
                "old_zone": old_zone,
                "new_zone": new_zone,
                "intent_score": round(intent_score, 3),
                "genome_hex": self._genome_to_hex(agent.genome),
                "experiment": 4,
                "flagged": False,
            }
            
            self.collection.add(
                ids=[doc_id],
                documents=[document],
                metadatas=[metadata]
            )
            
        except Exception as e:
            print(f"[PULSE] Observer zone_entry error (non-fatal): {e}")
    
    def log_beat_activation(self, agent, tick: int, wave1_interval: float, 
                            wave2_interval: float) -> None:
        """Log when agent shields at beat interval (Exp 4+).
        
        Args:
            agent: The agent with beat activation
            tick: Current simulation tick
            wave1_interval: Calculated interval for Wave 1
            wave2_interval: Calculated interval for Wave 2
        """
        if not self.connected or self.collection is None:
            return
        
        try:
            self.event_counter += 1
            doc_id = f"alife_{tick}_beat_activation_{agent.id}_{self.event_counter}"
            
            document = (
                f"Beat frequency activation detected in agent {agent.id} at tick {tick} "
                f"generation {agent.generation}. "
                f"Agent is tracking dual wave sources: Wave 1 interval ~{wave1_interval:.0f} ticks, "
                f"Wave 2 interval ~{wave2_interval:.0f} ticks. "
                f"This agent has developed phase coherence for the interference zone. "
                f"Genome: {self._genome_to_readable(agent.genome)}."
            )
            
            metadata = {
                "event_type": "beat_activation",
                "tick": tick,
                "agent_id": agent.id,
                "generation": agent.generation,
                "wave1_interval": round(wave1_interval, 1),
                "wave2_interval": round(wave2_interval, 1),
                "genome_hex": self._genome_to_hex(agent.genome),
                "experiment": 4,
                "flagged": True,
                "flag_reason": "BEAT_COHERENCE"
            }
            
            self.collection.add(
                ids=[doc_id],
                documents=[document],
                metadatas=[metadata]
            )
            
        except Exception as e:
            print(f"[PULSE] Observer beat_activation error (non-fatal): {e}")
    
    def log_spatial_snapshot(self, zone_data: dict, tick: int) -> None:
        """Log population distribution across zones (Exp 4+).
        
        Args:
            zone_data: Dict with zone -> {population, beat_genome_pct, neg_gaps}
            tick: Current simulation tick
        """
        if not self.connected or self.collection is None:
            return
        
        try:
            self.event_counter += 1
            doc_id = f"alife_{tick}_spatial_snapshot_{self.event_counter}"
            
            left = zone_data.get('left', {})
            center = zone_data.get('center', {})
            right = zone_data.get('right', {})
            
            total_pop = left.get('population', 0) + center.get('population', 0) + right.get('population', 0)
            
            document = (
                f"Spatial distribution snapshot at tick {tick}. "
                f"Left zone (Wave 1 only): {left.get('population', 0)} agents, "
                f"{left.get('beat_genome_pct', 0):.1f}% beat genome, {left.get('neg_gaps', 0)} neg gaps. "
                f"Center zone (interference): {center.get('population', 0)} agents, "
                f"{center.get('beat_genome_pct', 0):.1f}% beat genome, {center.get('neg_gaps', 0)} neg gaps. "
                f"Right zone (Wave 2 only): {right.get('population', 0)} agents, "
                f"{right.get('beat_genome_pct', 0):.1f}% beat genome, {right.get('neg_gaps', 0)} neg gaps. "
                f"Total population: {total_pop}."
            )
            
            # Determine if stratification is occurring
            center_beat_pct = center.get('beat_genome_pct', 0)
            outer_beat_pct = (left.get('beat_genome_pct', 0) + right.get('beat_genome_pct', 0)) / 2
            stratification = center_beat_pct > outer_beat_pct * 1.5
            
            metadata = {
                "event_type": "spatial_snapshot",
                "tick": tick,
                "left_population": left.get('population', 0),
                "center_population": center.get('population', 0),
                "right_population": right.get('population', 0),
                "left_beat_pct": round(left.get('beat_genome_pct', 0), 1),
                "center_beat_pct": round(center.get('beat_genome_pct', 0), 1),
                "right_beat_pct": round(right.get('beat_genome_pct', 0), 1),
                "stratification_detected": stratification,
                "experiment": 4,
                "flagged": stratification,
                "flag_reason": "SPATIAL_STRATIFICATION" if stratification else None
            }
            
            # Filter None values
            metadata = {k: v for k, v in metadata.items() if v is not None}
            
            self.collection.add(
                ids=[doc_id],
                documents=[document],
                metadatas=[metadata]
            )
            
        except Exception as e:
            print(f"[PULSE] Observer spatial_snapshot error (non-fatal): {e}")
    
    def close(self) -> None:
        """Close the observer connection."""
        if self.connected:
            print(f"[PULSE] Observer closing. Logged {self.event_counter} events.")
        self.connected = False
        self.collection = None
