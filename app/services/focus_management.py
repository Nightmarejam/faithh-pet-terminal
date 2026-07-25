"""
Focus Management System
Phase 7: Personal Productivity and Concept Drift Prevention
Natural idea capture, evaluation, and strategic alignment
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import uuid
import logging
from .constella_constitution import constella_constitution, ComplianceLevel

class ConceptState(Enum):
    """States in concept lifecycle"""
    CAPTURED = "captured"
    EVALUATING = "evaluating"
    PRIORITIZED = "prioritized"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class ConceptPriority(Enum):
    """Priority levels for concepts"""
    IMMEDIATE = "immediate"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    DEFERRED = "deferred"

class FocusHealth(Enum):
    """Focus health levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class Concept:
    """Idea or concept in the focus management system"""
    id: str
    title: str
    description: str
    raw_idea: str
    capture_context: Dict[str, Any]
    capture_timestamp: datetime
    state: ConceptState = ConceptState.CAPTURED
    priority: ConceptPriority = ConceptPriority.MEDIUM
    tags: List[str] = field(default_factory=list)
    domain: str = "general"
    parent_concept_id: Optional[str] = None
    child_concept_ids: List[str] = field(default_factory=list)
    
    # Evaluation results
    evaluation_score: float = 0.0
    strategic_alignment: float = 0.0
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    completion_probability: float = 0.0
    impact_potential: float = 0.0
    constitutional_feasibility: ComplianceLevel = ComplianceLevel.UNKNOWN
    
    # Progress tracking
    progress_percentage: float = 0.0
    last_activity: datetime = field(default_factory=datetime.now)
    estimated_completion: Optional[datetime] = None
    actual_completion: Optional[datetime] = None

@dataclass
class ConceptEvaluation:
    """Evaluation results for a concept"""
    concept_id: str
    evaluation_timestamp: datetime
    constitutional_compliance: ComplianceLevel
    strategic_value: float
    resource_requirements: Dict[str, Any]
    completion_probability: float
    impact_potential: float
    synergy_with_active: float
    urgency: float
    learning_value: float
    overall_score: float
    recommendation: str
    confidence: float
    reasoning: str

@dataclass
class FocusAlert:
    """Alert for focus management"""
    id: str
    alert_type: str
    severity: str
    message: str
    concept_ids: List[str]
    timestamp: datetime
    recommendations: List[str]
    acknowledged: bool = False

class FocusManager:
    """Manages concepts and prevents focus drift"""
    
    def __init__(self, focus_file: str = None):
        self.project_root = Path("/home/jonat/ai-stack")
        self.focus_file = focus_file or self.project_root / "data" / "focus_management.json"
        self.focus_file.parent.mkdir(exist_ok=True)
        
        # Concept storage
        self.concepts = {}
        self.concept_states = {state: [] for state in ConceptState}
        self.focus_alerts = []
        
        # Evaluation criteria weights
        self.evaluation_weights = {
            "constitutional_compliance": 0.2,
            "strategic_value": 0.2,
            "resource_requirements": 0.15,
            "completion_probability": 0.15,
            "impact_potential": 0.15,
            "synergy_with_active": 0.1,
            "urgency": 0.05
        }
        
        # Focus drift detection
        self.drift_threshold = 0.7
        self.focus_history = []
        self.max_history_size = 100
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Load existing data
        self.load_focus_data()
    
    def load_focus_data(self):
        """Load existing focus management data"""
        try:
            if self.focus_file.exists():
                with open(self.focus_file, 'r') as f:
                    data = json.load(f)
                
                # Load concepts
                for concept_data in data.get("concepts", []):
                    concept = Concept(
                        id=concept_data["id"],
                        title=concept_data["title"],
                        description=concept_data["description"],
                        raw_idea=concept_data["raw_idea"],
                        capture_context=concept_data["capture_context"],
                        capture_timestamp=datetime.fromisoformat(concept_data["capture_timestamp"]),
                        state=ConceptState(concept_data["state"]),
                        priority=ConceptPriority(concept_data["priority"]),
                        tags=concept_data.get("tags", []),
                        domain=concept_data.get("domain", "general"),
                        parent_concept_id=concept_data.get("parent_concept_id"),
                        child_concept_ids=concept_data.get("child_concept_ids", []),
                        evaluation_score=concept_data.get("evaluation_score", 0.0),
                        strategic_alignment=concept_data.get("strategic_alignment", 0.0),
                        resource_requirements=concept_data.get("resource_requirements", {}),
                        completion_probability=concept_data.get("completion_probability", 0.0),
                        impact_potential=concept_data.get("impact_potential", 0.0),
                        constitutional_feasibility=ComplianceLevel(concept_data.get("constitutional_feasibility", "unknown")),
                        progress_percentage=concept_data.get("progress_percentage", 0.0),
                        last_activity=datetime.fromisoformat(concept_data["last_activity"]),
                        estimated_completion=datetime.fromisoformat(concept_data["estimated_completion"]) if concept_data.get("estimated_completion") else None,
                        actual_completion=datetime.fromisoformat(concept_data["actual_completion"]) if concept_data.get("actual_completion") else None
                    )
                    
                    self.concepts[concept.id] = concept
                    self.concept_states[concept.state].append(concept.id)
                
                # Load alerts
                for alert_data in data.get("focus_alerts", []):
                    alert = FocusAlert(
                        id=alert_data["id"],
                        alert_type=alert_data["alert_type"],
                        severity=alert_data["severity"],
                        message=alert_data["message"],
                        concept_ids=alert_data["concept_ids"],
                        timestamp=datetime.fromisoformat(alert_data["timestamp"]),
                        recommendations=alert_data["recommendations"],
                        acknowledged=alert_data.get("acknowledged", False)
                    )
                    self.focus_alerts.append(alert)
                
                # Load focus history
                for history_item in data.get("focus_history", []):
                    self.focus_history.append({
                        "timestamp": datetime.fromisoformat(history_item["timestamp"]),
                        "active_concepts": history_item["active_concepts"],
                        "focus_health": history_item["focus_health"],
                        "drift_indicators": history_item["drift_indicators"]
                    })
                
                self.logger.info(f"Loaded {len(self.concepts)} concepts and {len(self.focus_alerts)} alerts")
            
        except Exception as e:
            self.logger.error(f"Error loading focus data: {e}")
    
    def save_focus_data(self):
        """Save focus management data"""
        try:
            data = {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "concepts": [],
                "focus_alerts": [],
                "focus_history": self.focus_history[-self.max_history_size:],
                "evaluation_weights": self.evaluation_weights
            }
            
            # Save concepts
            for concept in self.concepts.values():
                concept_data = {
                    "id": concept.id,
                    "title": concept.title,
                    "description": concept.description,
                    "raw_idea": concept.raw_idea,
                    "capture_context": concept.capture_context,
                    "capture_timestamp": concept.capture_timestamp.isoformat(),
                    "state": concept.state.value,
                    "priority": concept.priority.value,
                    "tags": concept.tags,
                    "domain": concept.domain,
                    "parent_concept_id": concept.parent_concept_id,
                    "child_concept_ids": concept.child_concept_ids,
                    "evaluation_score": concept.evaluation_score,
                    "strategic_alignment": concept.strategic_alignment,
                    "resource_requirements": concept.resource_requirements,
                    "completion_probability": concept.completion_probability,
                    "impact_potential": concept.impact_potential,
                    "constitutional_feasibility": concept.constitutional_feasibility.value,
                    "progress_percentage": concept.progress_percentage,
                    "last_activity": concept.last_activity.isoformat(),
                    "estimated_completion": concept.estimated_completion.isoformat() if concept.estimated_completion else None,
                    "actual_completion": concept.actual_completion.isoformat() if concept.actual_completion else None
                }
                data["concepts"].append(concept_data)
            
            # Save alerts
            for alert in self.focus_alerts:
                alert_data = {
                    "id": alert.id,
                    "alert_type": alert.alert_type,
                    "severity": alert.severity,
                    "message": alert.message,
                    "concept_ids": alert.concept_ids,
                    "timestamp": alert.timestamp.isoformat(),
                    "recommendations": alert.recommendations,
                    "acknowledged": alert.acknowledged
                }
                data["focus_alerts"].append(alert_data)
            
            with open(self.focus_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.logger.info(f"Saved focus data to {self.focus_file}")
            
        except Exception as e:
            self.logger.error(f"Error saving focus data: {e}")
    
    def capture_concept(self, raw_idea: str, context: Dict[str, Any] = None) -> Concept:
        """Capture a new concept from raw idea"""
        try:
            concept_id = f"concept_{int(time.time() * 1000)}"
            
            # Parse raw idea into structured concept
            title = self.extract_title(raw_idea)
            description = self.extract_description(raw_idea)
            domain = self.detect_domain(raw_idea, context)
            tags = self.extract_tags(raw_idea)
            
            concept = Concept(
                id=concept_id,
                title=title,
                description=description,
                raw_idea=raw_idea,
                capture_context=context or {},
                capture_timestamp=datetime.now(),
                domain=domain,
                tags=tags
            )
            
            # Store concept
            self.concepts[concept_id] = concept
            self.concept_states[ConceptState.CAPTURED].append(concept_id)
            
            # Queue for evaluation
            self.queue_for_evaluation(concept_id)
            
            # Save data
            self.save_focus_data()
            
            self.logger.info(f"Captured concept: {concept.title}")
            
            return concept
            
        except Exception as e:
            self.logger.error(f"Error capturing concept: {e}")
            raise
    
    def extract_title(self, raw_idea: str) -> str:
        """Extract title from raw idea"""
        # Simple extraction - take first sentence or first 50 chars
        sentences = raw_idea.split('.')
        if len(sentences) > 1:
            title = sentences[0].strip()
        else:
            title = raw_idea[:50].strip()
        
        return title if title else "Untitled Concept"
    
    def extract_description(self, raw_idea: str) -> str:
        """Extract description from raw idea"""
        # Use the full raw idea as description for now
        return raw_idea.strip()
    
    def detect_domain(self, raw_idea: str, context: Dict[str, Any]) -> str:
        """Detect domain of concept"""
        idea_lower = raw_idea.lower()
        
        domain_keywords = {
            "genomic_research": ["genomic", "dna", "gene", "biology", "research", "experiment"],
            "civic_engagement": ["civic", "community", "democracy", "government", "engagement"],
            "personal_assistance": ["personal", "assistant", "help", "support", "productivity"],
            "creative_arts": ["art", "creative", "design", "music", "writing"],
            "technical": ["code", "programming", "technical", "system", "architecture"]
        }
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in idea_lower for keyword in keywords):
                return domain
        
        # Check context
        if context and "domain" in context:
            return context["domain"]
        
        return "general"
    
    def extract_tags(self, raw_idea: str) -> List[str]:
        """Extract tags from raw idea"""
        # Simple tag extraction based on keywords
        idea_lower = raw_idea.lower()
        tags = []
        
        tag_keywords = {
            "urgent": ["urgent", "asap", "immediately", "critical"],
            "research": ["research", "study", "investigate", "analyze"],
            "development": ["develop", "build", "create", "implement"],
            "improvement": ["improve", "enhance", "optimize", "refine"],
            "collaboration": ["collaborate", "partner", "team", "together"]
        }
        
        for tag, keywords in tag_keywords.items():
            if any(keyword in idea_lower for keyword in keywords):
                tags.append(tag)
        
        return tags
    
    def queue_for_evaluation(self, concept_id: str):
        """Queue concept for evaluation"""
        # Move to evaluating state
        concept = self.concepts[concept_id]
        self.concept_states[ConceptState.CAPTURED].remove(concept_id)
        self.concept_states[ConceptState.EVALUATING].append(concept_id)
        concept.state = ConceptState.EVALUATING
        
        # Perform evaluation
        evaluation = self.evaluate_concept(concept_id)
        
        # Update concept with evaluation results
        concept.evaluation_score = evaluation.overall_score
        concept.strategic_alignment = evaluation.strategic_value
        concept.resource_requirements = evaluation.resource_requirements
        concept.completion_probability = evaluation.completion_probability
        concept.impact_potential = evaluation.impact_potential
        concept.constitutional_feasibility = evaluation.constitutional_compliance
        
        # Set priority based on evaluation
        concept.priority = self.determine_priority(evaluation)
        
        # Move to prioritized state
        self.concept_states[ConceptState.EVALUATING].remove(concept_id)
        self.concept_states[ConceptState.PRIORITIZED].append(concept_id)
        concept.state = ConceptState.PRIORITIZED
        
        self.logger.info(f"Evaluated concept: {concept.title} - Score: {evaluation.overall_score:.2f}")
    
    def evaluate_concept(self, concept_id: str) -> ConceptEvaluation:
        """Evaluate a concept against multiple criteria"""
        concept = self.concepts[concept_id]
        
        # Constitutional compliance check
        constitutional_compliance = self.check_constitutional_compliance(concept)
        
        # Strategic value assessment
        strategic_value = self.assess_strategic_value(concept)
        
        # Resource requirements assessment
        resource_requirements = self.assess_resource_requirements(concept)
        
        # Completion probability estimation
        completion_probability = self.estimate_completion_probability(concept)
        
        # Impact potential assessment
        impact_potential = self.assess_impact_potential(concept)
        
        # Synergy with active work
        synergy_with_active = self.assess_synergy_with_active(concept)
        
        # Urgency assessment
        urgency = self.assess_urgency(concept)
        
        # Learning value assessment
        learning_value = self.assess_learning_value(concept)
        
        # Calculate compliance score from compliance level
        compliance_score = 0.0
        if constitutional_compliance == ComplianceLevel.FULL:
            compliance_score = 1.0
        elif constitutional_compliance == ComplianceLevel.PARTIAL:
            compliance_score = 0.6
        elif constitutional_compliance == ComplianceLevel.VIOLATION:
            compliance_score = 0.0
        else:  # UNKNOWN
            compliance_score = 0.5
        
        # Calculate overall score
        overall_score = (
            compliance_score * self.evaluation_weights["constitutional_compliance"] +
            strategic_value * self.evaluation_weights["strategic_value"] +
            (1.0 - resource_requirements["complexity"]) * self.evaluation_weights["resource_requirements"] +
            completion_probability * self.evaluation_weights["completion_probability"] +
            impact_potential * self.evaluation_weights["impact_potential"] +
            synergy_with_active * self.evaluation_weights["synergy_with_active"] +
            urgency * self.evaluation_weights["urgency"]
        )
        
        # Generate recommendation
        recommendation = self.generate_recommendation(overall_score, constitutional_compliance, strategic_value)
        
        # Calculate confidence
        confidence = self.calculate_confidence(constitutional_compliance, strategic_value, resource_requirements)
        
        # Generate reasoning
        reasoning = self.generate_evaluation_reasoning(constitutional_compliance, strategic_value, resource_requirements, overall_score)
        
        return ConceptEvaluation(
            concept_id=concept_id,
            evaluation_timestamp=datetime.now(),
            constitutional_compliance=constitutional_compliance,
            strategic_value=strategic_value,
            resource_requirements=resource_requirements,
            completion_probability=completion_probability,
            impact_potential=impact_potential,
            synergy_with_active=synergy_with_active,
            urgency=urgency,
            learning_value=learning_value,
            overall_score=overall_score,
            recommendation=recommendation,
            confidence=confidence,
            reasoning=reasoning
        )
    
    def check_constitutional_compliance(self, concept: Concept) -> ComplianceLevel:
        """Check constitutional compliance of concept"""
        try:
            # Create action representation for constitutional evaluation
            action = {
                "id": concept.id,
                "description": concept.description,
                "context": concept.capture_context
            }
            
            # Evaluate against constitution
            compliance_report = constella_constitution.evaluate_compliance(action, concept.domain)
            
            return compliance_report.compliance_level
            
        except Exception as e:
            self.logger.error(f"Error checking constitutional compliance: {e}")
            return ComplianceLevel.UNKNOWN
    
    def assess_strategic_value(self, concept: Concept) -> float:
        """Assess strategic value of concept"""
        # Simple assessment based on domain and tags
        domain_values = {
            "genomic_research": 0.9,
            "civic_engagement": 0.8,
            "personal_assistance": 0.7,
            "creative_arts": 0.6,
            "technical": 0.7,
            "general": 0.5
        }
        
        base_value = domain_values.get(concept.domain, 0.5)
        
        # Adjust based on tags
        tag_adjustments = {
            "urgent": 0.1,
            "research": 0.1,
            "development": 0.1,
            "improvement": 0.05,
            "collaboration": 0.05
        }
        
        for tag in concept.tags:
            if tag in tag_adjustments:
                base_value += tag_adjustments[tag]
        
        return min(base_value, 1.0)
    
    def assess_resource_requirements(self, concept: Concept) -> Dict[str, Any]:
        """Assess resource requirements for concept"""
        # Simple assessment based on description length and complexity
        description_length = len(concept.description)
        
        complexity = min(description_length / 1000, 1.0)
        
        estimated_hours = max(1, description_length / 100)
        
        return {
            "complexity": complexity,
            "estimated_hours": estimated_hours,
            "skills_needed": self.detect_required_skills(concept),
            "tools_needed": self.detect_required_tools(concept)
        }
    
    def detect_required_skills(self, concept: Concept) -> List[str]:
        """Detect skills needed for concept"""
        description_lower = concept.description.lower()
        skills = []
        
        skill_keywords = {
            "programming": ["code", "program", "develop", "software"],
            "research": ["research", "study", "investigate", "analyze"],
            "design": ["design", "ui", "ux", "interface"],
            "writing": ["write", "document", "content", "text"],
            "data_analysis": ["data", "analysis", "statistics", "metrics"]
        }
        
        for skill, keywords in skill_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                skills.append(skill)
        
        return skills
    
    def detect_required_tools(self, concept: Concept) -> List[str]:
        """Detect tools needed for concept"""
        description_lower = concept.description.lower()
        tools = []
        
        tool_keywords = {
            "python": ["python", "code", "script"],
            "database": ["database", "data", "storage"],
            "web": ["web", "website", "browser"],
            "api": ["api", "interface", "integration"],
            "ml": ["machine learning", "ai", "model", "training"]
        }
        
        for tool, keywords in tool_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                tools.append(tool)
        
        return tools
    
    def estimate_completion_probability(self, concept: Concept) -> float:
        """Estimate probability of completing concept"""
        # Base probability on resource requirements and complexity
        resource_requirements = self.assess_resource_requirements(concept)
        complexity = resource_requirements["complexity"]
        
        # Higher complexity = lower probability
        base_probability = 1.0 - (complexity * 0.5)
        
        # Adjust based on domain familiarity
        domain_familiarity = {
            "genomic_research": 0.8,
            "civic_engagement": 0.7,
            "personal_assistance": 0.9,
            "technical": 0.9,
            "creative_arts": 0.6,
            "general": 0.7
        }
        
        familiarity = domain_familiarity.get(concept.domain, 0.7)
        
        return min(base_probability * familiarity, 1.0)
    
    def assess_impact_potential(self, concept: Concept) -> float:
        """Assess potential impact of concept"""
        # Higher strategic value and lower complexity = higher impact
        strategic_value = self.assess_strategic_value(concept)
        resource_requirements = self.assess_resource_requirements(concept)
        complexity = resource_requirements["complexity"]
        
        # Impact = strategic value * (1 - complexity/2)
        impact = strategic_value * (1.0 - complexity * 0.5)
        
        return min(impact, 1.0)
    
    def assess_synergy_with_active(self, concept: Concept) -> float:
        """Assess synergy with currently active concepts"""
        active_concepts = self.concept_states[ConceptState.ACTIVE]
        
        if not active_concepts:
            return 0.5  # Neutral if no active concepts
        
        synergy_score = 0.0
        synergy_count = 0
        
        for active_concept_id in active_concepts:
            active_concept = self.concepts[active_concept_id]
            
            # Check domain similarity
            if concept.domain == active_concept.domain:
                synergy_score += 0.3
                synergy_count += 1
            
            # Check tag overlap
            common_tags = set(concept.tags) & set(active_concept.tags)
            if common_tags:
                synergy_score += len(common_tags) * 0.1
                synergy_count += 1
            
            # Check skill overlap
            concept_skills = set(self.detect_required_skills(concept))
            active_skills = set(self.detect_required_skills(active_concept))
            common_skills = concept_skills & active_skills
            if common_skills:
                synergy_score += len(common_skills) * 0.1
                synergy_count += 1
        
        if synergy_count > 0:
            return min(synergy_score / synergy_count, 1.0)
        
        return 0.0
    
    def assess_urgency(self, concept: Concept) -> float:
        """Assess urgency of concept"""
        urgency = 0.0
        
        # Check for urgency tags
        if "urgent" in concept.tags:
            urgency += 0.5
        
        # Check for time-sensitive keywords
        description_lower = concept.description.lower()
        urgency_keywords = ["deadline", "asap", "immediately", "urgent", "time-sensitive"]
        for keyword in urgency_keywords:
            if keyword in description_lower:
                urgency += 0.2
        
        # Check capture context for urgency
        if concept.capture_context and "urgency" in concept.capture_context:
            urgency += concept.capture_context["urgency"]
        
        return min(urgency, 1.0)
    
    def assess_learning_value(self, concept: Concept) -> float:
        """Assess learning value of concept"""
        # Higher learning value for new domains and skills
        learning_value = 0.5  # Base value
        
        # Domain novelty (simplified)
        domain_novelty = {
            "genomic_research": 0.3,
            "civic_engagement": 0.2,
            "personal_assistance": 0.1,
            "creative_arts": 0.2,
            "technical": 0.1,
            "general": 0.0
        }
        
        learning_value += domain_novelty.get(concept.domain, 0.0)
        
        # Skill learning opportunities
        resource_requirements = self.assess_resource_requirements(concept)
        skills_count = len(resource_requirements["skills_needed"])
        learning_value += min(skills_count * 0.1, 0.3)
        
        return min(learning_value, 1.0)
    
    def determine_priority(self, evaluation: ConceptEvaluation) -> ConceptPriority:
        """Determine concept priority based on evaluation"""
        if evaluation.overall_score >= 0.8:
            return ConceptPriority.IMMEDIATE
        elif evaluation.overall_score >= 0.6:
            return ConceptPriority.HIGH
        elif evaluation.overall_score >= 0.4:
            return ConceptPriority.MEDIUM
        elif evaluation.overall_score >= 0.2:
            return ConceptPriority.LOW
        else:
            return ConceptPriority.DEFERRED
    
    def generate_recommendation(self, overall_score: float, constitutional_compliance: ComplianceLevel, strategic_value: float) -> str:
        """Generate recommendation based on evaluation"""
        if constitutional_compliance == ComplianceLevel.VIOLATION:
            return "DEFER - Concept violates constitutional principles"
        elif overall_score >= 0.8:
            return "PURSUE IMMEDIATELY - High value and feasibility"
        elif overall_score >= 0.6:
            return "PRIORITIZE - Good value, consider for active work"
        elif overall_score >= 0.4:
            return "CONSIDER - Moderate value, evaluate against current priorities"
        else:
            return "DEFER - Low value or high complexity, reconsider later"
    
    def calculate_confidence(self, constitutional_compliance: ComplianceLevel, strategic_value: float, resource_requirements: Dict[str, Any]) -> float:
        """Calculate confidence in evaluation"""
        confidence = 0.7  # Base confidence
        
        # Higher confidence with clear constitutional assessment
        if constitutional_compliance != ComplianceLevel.UNKNOWN:
            confidence += 0.1
        
        # Higher confidence with clear strategic value
        if strategic_value >= 0.7 or strategic_value <= 0.3:
            confidence += 0.1
        
        # Lower confidence with high complexity
        if resource_requirements["complexity"] > 0.8:
            confidence -= 0.1
        
        return min(confidence, 1.0)
    
    def generate_evaluation_reasoning(self, constitutional_compliance: ComplianceLevel, strategic_value: float, resource_requirements: Dict[str, Any], overall_score: float) -> str:
        """Generate reasoning for evaluation"""
        reasoning_parts = []
        
        # Constitutional compliance
        if constitutional_compliance == ComplianceLevel.VIOLATION:
            reasoning_parts.append("Concept violates constitutional principles")
        elif constitutional_compliance == ComplianceLevel.FULL:
            reasoning_parts.append("Concept fully complies with constitutional principles")
        else:
            reasoning_parts.append("Concept has partial constitutional compliance")
        
        # Strategic value
        if strategic_value >= 0.7:
            reasoning_parts.append("High strategic value")
        elif strategic_value <= 0.3:
            reasoning_parts.append("Low strategic value")
        else:
            reasoning_parts.append("Moderate strategic value")
        
        # Resource requirements
        complexity = resource_requirements["complexity"]
        if complexity >= 0.7:
            reasoning_parts.append("High resource requirements")
        elif complexity <= 0.3:
            reasoning_parts.append("Low resource requirements")
        else:
            reasoning_parts.append("Moderate resource requirements")
        
        # Overall score
        if overall_score >= 0.7:
            reasoning_parts.append("High overall evaluation score")
        elif overall_score <= 0.3:
            reasoning_parts.append("Low overall evaluation score")
        else:
            reasoning_parts.append("Moderate overall evaluation score")
        
        return ". ".join(reasoning_parts) + "."
    
    def get_active_concepts(self) -> List[Concept]:
        """Get currently active concepts"""
        active_concept_ids = self.concept_states[ConceptState.ACTIVE]
        return [self.concepts[concept_id] for concept_id in active_concept_ids]
    
    def get_concept_pipeline(self) -> Dict[str, List[Concept]]:
        """Get concept pipeline by state"""
        pipeline = {}
        for state, concept_ids in self.concept_states.items():
            pipeline[state.value] = [self.concepts[concept_id] for concept_id in concept_ids]
        return pipeline
    
    def get_focus_health(self) -> FocusHealth:
        """Get overall focus health"""
        active_concepts = self.get_active_concepts()
        
        if not active_concepts:
            return FocusHealth.WARNING
        
        # Check average progress
        avg_progress = sum(c.progress_percentage for c in active_concepts) / len(active_concepts)
        
        # Check for drift indicators
        drift_indicators = self.detect_focus_drift()
        
        if avg_progress > 0.7 and drift_indicators["drift_score"] < 0.3:
            return FocusHealth.EXCELLENT
        elif avg_progress > 0.5 and drift_indicators["drift_score"] < 0.5:
            return FocusHealth.GOOD
        elif drift_indicators["drift_score"] > 0.7:
            return FocusHealth.CRITICAL
        else:
            return FocusHealth.WARNING
    
    def detect_focus_drift(self) -> Dict[str, Any]:
        """Detect focus drift patterns"""
        drift_indicators = {
            "frequent_concept_switching": self.check_frequent_switching(),
            "premature_abandonment": self.check_premature_abandonment(),
            "resource_fragmentation": self.check_resource_fragmentation(),
            "strategic_misalignment": self.check_strategic_misalignment(),
            "completion_avoidance": self.check_completion_avoidance()
        }
        
        # Calculate overall drift score
        drift_score = sum(drift_indicators.values()) / len(drift_indicators)
        
        return {
            "drift_score": drift_score,
            "indicators": drift_indicators,
            "severity": "high" if drift_score > 0.7 else "medium" if drift_score > 0.3 else "low"
        }
    
    def check_frequent_switching(self) -> float:
        """Check for frequent concept switching"""
        # Simple check: too many concepts in active state
        active_count = len(self.concept_states[ConceptState.ACTIVE])
        
        if active_count > 5:
            return 0.8
        elif active_count > 3:
            return 0.5
        else:
            return 0.0
    
    def check_premature_abandonment(self) -> float:
        """Check for premature concept abandonment"""
        # Check concepts with low progress that were recently active
        recently_active = []
        
        for concept in self.concepts.values():
            if (concept.state == ConceptState.PAUSED and 
                concept.progress_percentage < 0.2 and
                (datetime.now() - concept.last_activity).days < 7):
                recently_active.append(concept)
        
        if len(recently_active) > 3:
            return 0.8
        elif len(recently_active) > 1:
            return 0.5
        else:
            return 0.0
    
    def check_resource_fragmentation(self) -> float:
        """Check for resource fragmentation"""
        # Check if active concepts have overlapping resource requirements
        active_concepts = self.get_active_concepts()
        
        if len(active_concepts) < 2:
            return 0.0
        
        # Check for skill overlap
        all_skills = []
        for concept in active_concepts:
            skills = self.detect_required_skills(concept)
            all_skills.extend(skills)
        
        # Calculate fragmentation (many unique skills across concepts)
        unique_skills = set(all_skills)
        fragmentation = len(unique_skills) / max(len(all_skills), 1)
        
        return fragmentation
    
    def check_strategic_misalignment(self) -> float:
        """Check for strategic misalignment"""
        # Check if active concepts have low strategic alignment
        active_concepts = self.get_active_concepts()
        
        if not active_concepts:
            return 0.0
        
        avg_strategic_value = sum(self.assess_strategic_value(c) for c in active_concepts) / len(active_concepts)
        
        if avg_strategic_value < 0.3:
            return 0.8
        elif avg_strategic_value < 0.5:
            return 0.5
        else:
            return 0.0
    
    def check_completion_avoidance(self) -> float:
        """Check for completion avoidance"""
        # Check for concepts with high progress that are not completed
        near_completion = []
        
        for concept in self.concepts.values():
            if (concept.progress_percentage > 0.8 and 
                concept.state != ConceptState.COMPLETED and
                (datetime.now() - concept.last_activity).days < 14):
                near_completion.append(concept)
        
        if len(near_completion) > 2:
            return 0.8
        elif len(near_completion) > 0:
            return 0.5
        else:
            return 0.0
    
    def get_focus_metrics(self) -> Dict[str, Any]:
        """Get comprehensive focus metrics"""
        return {
            "total_concepts": len(self.concepts),
            "active_concepts": len(self.concept_states[ConceptState.ACTIVE]),
            "completed_concepts": len(self.concept_states[ConceptState.COMPLETED]),
            "focus_health": self.get_focus_health().value,
            "drift_indicators": self.detect_focus_drift(),
            "concept_pipeline": {state.value: len(concepts) for state, concepts in self.concept_states.items()},
            "recent_captures": len([c for c in self.concepts.values() if (datetime.now() - c.capture_timestamp).days < 7]),
            "avg_evaluation_score": sum(c.evaluation_score for c in self.concepts.values()) / max(len(self.concepts), 1)
        }

# Global instance
focus_manager = FocusManager()