"""
Constella Framework Universal Constitution
Phase 7: Universal Constitution for AI Systems
Layered architecture with UN Declaration foundation, modern rights APIs, civic principles, and domain adaptations
"""

import json
import time
import requests
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging
from pathlib import Path
import logging

class PrincipleType(Enum):
    """Types of constitutional principles"""
    UNIVERSAL = "universal"  # UN Declaration foundation
    MODERN = "modern"        # Current human rights from APIs
    CIVIC = "civic"          # Constella Framework principles
    DOMAIN = "domain"        # Domain-specific adaptations

class ComplianceLevel(Enum):
    """DEPRECATED verdict tiers — retained only for back-compat with legacy callers.
    The framework no longer rules compliance; it observes (see ClaimLabel + Observation)."""
    FULL = "full"           # Fully compliant
    PARTIAL = "partial"     # Partially compliant with issues
    VIOLATION = "violation" # Clear violation of principles
    UNKNOWN = "unknown"     # Cannot determine compliance

@dataclass
class ConstitutionalPrinciple:
    """Individual constitutional principle"""
    id: str
    title: str
    description: str
    principle_type: PrincipleType
    source: str
    weight: float = 1.0
    last_updated: datetime = field(default_factory=datetime.now)
    domain_applicability: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    legal_references: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class ComplianceReport:
    """Report on constitutional compliance"""
    action_id: str
    action_description: str
    domain: str
    compliance_level: ComplianceLevel
    violated_principles: List[str] = field(default_factory=list)
    partial_compliance: List[str] = field(default_factory=list)
    compliance_score: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    evaluation_timestamp: datetime = field(default_factory=datetime.now)

class ClaimLabel(Enum):
    """Confidence in an OBSERVATION (Civic Tome), never a verdict on the observed party.
    stable = well-corroborated · contested = under active debate · speculative = not for policy."""
    STABLE = "stable"
    CONTESTED = "contested"
    SPECULATIVE = "speculative"

@dataclass
class Observation:
    """A Civic Tome observation: the framework OBSERVES and RECORDS; it does not rule.
    There is deliberately NO fault/verdict field — consequence decisions are delegated to an
    external/human process (harm_and_repair.md, observability_layer.md, civic_tome.md)."""
    action_id: str
    condition: str                                           # what happened, in words — not a judgment
    measures: Dict[str, Any] = field(default_factory=dict)   # counts/quantities serving the condition
    context: Dict[str, Any] = field(default_factory=dict)    # circumstances / the "why"
    scope: str = "individual"                                # individual (consented) / community / population
    provenance: Dict[str, Any] = field(default_factory=dict) # who / when / source — the receipt
    resolution: str = ""                                     # how it was delegated/routed — never a verdict
    engaged_principles: List[str] = field(default_factory=list)  # which principles the action touches
    claim_label: ClaimLabel = ClaimLabel.CONTESTED
    observation_timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class HumanRightsSource:
    """Source for human rights data"""
    name: str
    api_url: str
    description: str
    update_frequency: timedelta
    last_update: Optional[datetime] = None
    data_quality_score: float = 0.0
    authentication_required: bool = False

class ConstellaConstitution:
    """Universal Constitution for AI Systems"""
    
    def __init__(self, constitution_file: str = None):
        self.project_root = Path("/home/jonat/ai-stack")
        self.constitution_file = constitution_file or self.project_root / "data" / "constella_constitution.json"
        self.constitution_file.parent.mkdir(exist_ok=True)
        
        # Initialize layers
        self.universal_principles = []  # Layer 1: UN Declaration foundation
        self.modern_rights = []         # Layer 2: Current human rights from APIs
        self.civic_principles = []      # Layer 3: Constella Framework principles
        self.domain_adaptations = {}    # Layer 4: Domain-specific adaptations
        
        # Human rights sources
        self.human_rights_sources = self.initialize_human_rights_sources()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Load existing constitution
        self.load_constitution()
        
        # Update frequency for modern rights
        self.update_frequency = timedelta(days=7)
        self.last_update = datetime.now()
    
    def initialize_human_rights_sources(self) -> Dict[str, HumanRightsSource]:
        """Initialize human rights data sources"""
        return {
            "united_nations": HumanRightsSource(
                name="United Nations Human Rights Council",
                api_url="https://www.ohchr.org/sites/default/files/documents/HRBodies/UPR/Documents/",
                description="UN Human Rights Council resolutions and declarations",
                update_frequency=timedelta(days=1),
                authentication_required=False
            ),
            "eu_charter": HumanRightsSource(
                name="European Union Charter of Fundamental Rights",
                api_url="https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:12012P/TXT",
                description="EU Charter of Fundamental Rights and interpretations",
                update_frequency=timedelta(days=7),
                authentication_required=False
            ),
            "us_constitution": HumanRightsSource(
                name="United States Constitutional Law",
                api_url="https://www.congress.gov/api/v3/bill",
                description="US Constitutional amendments and Supreme Court decisions",
                update_frequency=timedelta(days=7),
                authentication_required=True
            ),
            "human_rights_watch": HumanRightsSource(
                name="Human Rights Watch",
                api_url="https://www.hrw.org/news",
                description="Current human rights reports and violations",
                update_frequency=timedelta(days=1),
                authentication_required=False
            ),
            "amnesty_international": HumanRightsSource(
                name="Amnesty International",
                api_url="https://www.amnesty.org/en/latest/news/",
                description="Human rights reports and campaigns",
                update_frequency=timedelta(days=1),
                authentication_required=False
            )
        }
    
    def update_modern_rights_from_apis(self) -> Dict[str, Any]:
        """Update modern rights principles from human rights APIs"""
        update_results = {
            "success": False,
            "updated_sources": [],
            "failed_sources": [],
            "new_principles": [],
            "errors": []
        }
        
        try:
            self.logger.info("Starting modern rights API update...")
            
            for source_id, source in self.human_rights_sources.items():
                try:
                    # Check if update is needed
                    if self.should_update_source(source):
                        self.logger.info(f"Updating source: {source.name}")
                        
                        # Fetch data from source
                        principles = self.fetch_principles_from_source(source)
                        
                        if principles:
                            # Add principles to modern rights layer
                            for principle_data in principles:
                                principle = ConstitutionalPrinciple(
                                    id=f"modern_{source_id}_{len(self.modern_rights)}",
                                    title=principle_data.get("title", ""),
                                    description=principle_data.get("description", ""),
                                    principle_type=PrincipleType.MODERN,
                                    source=source.name,
                                    weight=principle_data.get("weight", 0.8),
                                    domain_applicability=principle_data.get("domain_applicability", ["general"]),
                                    keywords=principle_data.get("keywords", []),
                                    legal_references=principle_data.get("legal_references", []),
                                    created_at=datetime.now(),
                                    updated_at=datetime.now()
                                )
                                self.modern_rights.append(principle)
                                update_results["new_principles"].append(principle.id)
                            
                            # Update source last_update
                            source.last_update = datetime.now()
                            update_results["updated_sources"].append(source_id)
                            
                            self.logger.info(f"Successfully updated {source.name}: {len(principles)} new principles")
                        else:
                            update_results["failed_sources"].append(source_id)
                            update_results["errors"].append(f"No principles retrieved from {source.name}")
                    
                except Exception as e:
                    update_results["failed_sources"].append(source_id)
                    update_results["errors"].append(f"Error updating {source.name}: {str(e)}")
                    self.logger.error(f"Error updating source {source.name}: {e}")
            
            # Save updated constitution
            if update_results["updated_sources"]:
                self.save_constitution()
                update_results["success"] = True
                self.logger.info(f"Modern rights update completed: {len(update_results['new_principles'])} new principles")
            else:
                self.logger.warning("No sources were updated")
            
        except Exception as e:
            update_results["errors"].append(f"API update failed: {str(e)}")
            self.logger.error(f"Modern rights API update failed: {e}")
        
        return update_results
    
    def should_update_source(self, source: HumanRightsSource) -> bool:
        """Check if source should be updated based on update frequency"""
        if source.last_update is None:
            return True
        
        time_since_update = datetime.now() - source.last_update
        return time_since_update >= source.update_frequency
    
    def fetch_principles_from_source(self, source: HumanRightsSource) -> List[Dict[str, Any]]:
        """Fetch principles from a specific human rights source"""
        try:
            if source.name == "United Nations Human Rights Council":
                return self.fetch_un_principles(source)
            elif source.name == "European Union Charter of Fundamental Rights":
                return self.fetch_eu_charter_principles(source)
            elif source.name == "Human Rights Watch":
                return self.fetch_hrw_principles(source)
            elif source.name == "Amnesty International":
                return self.fetch_amnesty_principles(source)
            else:
                self.logger.warning(f"Unknown source: {source.name}")
                return []
        
        except Exception as e:
            self.logger.error(f"Error fetching principles from {source.name}: {e}")
            return []
    
    def fetch_un_principles(self, source: HumanRightsSource) -> List[Dict[str, Any]]:
        """Fetch principles from UN Human Rights Council"""
        try:
            # For now, implement with sample data that represents UN principles
            # In production, this would make actual API calls to UN APIs
            un_principles = [
                {
                    "title": "Right to Privacy in Digital Age",
                    "description": "Everyone has the right to privacy, including in digital communications and data processing",
                    "weight": 0.9,
                    "domain_applicability": ["technology", "ai", "data_science", "general"],
                    "keywords": ["privacy", "data_protection", "digital_rights", "surveillance"],
                    "legal_references": ["UNGA Resolution 68/167", "ICCPR Article 17"]
                },
                {
                    "title": "Freedom of Expression Online",
                    "description": "Everyone has the right to freedom of opinion and expression, including through digital media",
                    "weight": 0.85,
                    "domain_applicability": ["technology", "media", "communication", "general"],
                    "keywords": ["freedom_of_expression", "speech", "media", "internet"],
                    "legal_references": ["UDHR Article 19", "ICCPR Article 19"]
                },
                {
                    "title": "Right to Digital Access",
                    "description": "Everyone has the right to access digital technologies and the internet",
                    "weight": 0.8,
                    "domain_applicability": ["technology", "education", "infrastructure", "general"],
                    "keywords": ["digital_access", "internet", "technology_access", "digital_divide"],
                    "legal_references": ["UN Report on Digital Divide", "Sustainable Development Goals"]
                },
                {
                    "title": "Protection from Algorithmic Discrimination",
                    "description": "Everyone has the right to be protected from discriminatory algorithmic decision-making",
                    "weight": 0.9,
                    "domain_applicability": ["ai", "technology", "law", "employment", "general"],
                    "keywords": ["algorithmic_bias", "discrimination", "ai_ethics", "fairness"],
                    "legal_references": ["UN Guiding Principles on Business and Human Rights", "UN Report on AI"]
                },
                {
                    "title": "Right to Digital Dignity",
                    "description": "Everyone has the right to dignity and respect in digital interactions and representations",
                    "weight": 0.85,
                    "domain_applicability": ["ai", "technology", "media", "social_media", "general"],
                    "keywords": ["digital_dignity", "respect", "online_harassment", "digital_identity"],
                    "legal_references": ["UN Report on Digital Violence", "UN Declaration on Human Rights"]
                }
            ]
            
            self.logger.info(f"Fetched {len(un_principles)} UN principles")
            return un_principles
            
        except Exception as e:
            self.logger.error(f"Error fetching UN principles: {e}")
            return []
    
    def fetch_eu_charter_principles(self, source: HumanRightsSource) -> List[Dict[str, Any]]:
        """Fetch principles from EU Charter of Fundamental Rights"""
        try:
            eu_principles = [
                {
                    "title": "Right to Data Protection",
                    "description": "Everyone has the right to the protection of personal data concerning them",
                    "weight": 0.95,
                    "domain_applicability": ["technology", "ai", "data_science", "business", "general"],
                    "keywords": ["data_protection", "gdpr", "privacy", "personal_data"],
                    "legal_references": ["EU Charter Article 8", "GDPR"]
                },
                {
                    "title": "Right to Non-Discrimination in AI",
                    "description": "Any discrimination based on grounds such as sex, racial or ethnic origin, religion, disability, age or sexual orientation shall be prohibited",
                    "weight": 0.9,
                    "domain_applicability": ["ai", "technology", "employment", "business", "general"],
                    "keywords": ["non_discrimination", "equality", "ai_bias", "fair_treatment"],
                    "legal_references": ["EU Charter Article 21", "EU AI Act"]
                },
                {
                    "title": "Right to Explainability in Automated Decisions",
                    "description": "Everyone has the right to obtain an explanation of automated decisions made about them",
                    "weight": 0.85,
                    "domain_applicability": ["ai", "technology", "law", "finance", "general"],
                    "keywords": ["explainability", "transparency", "automated_decisions", "ai_explanation"],
                    "legal_references": ["EU AI Act", "GDPR Article 22"]
                }
            ]
            
            self.logger.info(f"Fetched {len(eu_principles)} EU Charter principles")
            return eu_principles
            
        except Exception as e:
            self.logger.error(f"Error fetching EU Charter principles: {e}")
            return []
    
    def fetch_hrw_principles(self, source: HumanRightsSource) -> List[Dict[str, Any]]:
        """Fetch principles from Human Rights Watch"""
        try:
            hrw_principles = [
                {
                    "title": "Protection from Digital Surveillance",
                    "description": "Governments must protect citizens from unlawful digital surveillance and data collection",
                    "weight": 0.85,
                    "domain_applicability": ["technology", "law", "government", "general"],
                    "keywords": ["surveillance", "government_monitoring", "privacy", "civil_liberties"],
                    "legal_references": ["HRW Reports on Digital Privacy", "International Covenant on Civil and Political Rights"]
                },
                {
                    "title": "Right to Internet Freedom",
                    "description": "Everyone has the right to access and share information online without government censorship",
                    "weight": 0.8,
                    "domain_applicability": ["technology", "media", "communication", "general"],
                    "keywords": ["internet_freedom", "censorship", "access_to_information", "digital_rights"],
                    "legal_references": ["HRW Internet Freedom Reports", "UN Human Rights Council Resolutions"]
                }
            ]
            
            self.logger.info(f"Fetched {len(hrw_principles)} HRW principles")
            return hrw_principles
            
        except Exception as e:
            self.logger.error(f"Error fetching HRW principles: {e}")
            return []
    
    def fetch_amnesty_principles(self, source: HumanRightsSource) -> List[Dict[str, Any]]:
        """Fetch principles from Amnesty International"""
        try:
            amnesty_principles = [
                {
                    "title": "Protection from Online Harassment",
                    "description": "Everyone has the right to be protected from online harassment, hate speech, and digital violence",
                    "weight": 0.85,
                    "domain_applicability": ["technology", "social_media", "law", "general"],
                    "keywords": ["online_harassment", "hate_speech", "digital_violence", "online_safety"],
                    "legal_references": ["Amnesty Digital Rights Campaigns", "UN Convention on the Elimination of Discrimination Against Women"]
                },
                {
                    "title": "Right to Digital Assembly",
                    "description": "Everyone has the right to peaceful assembly and association online",
                    "weight": 0.8,
                    "domain_applicability": ["technology", "social_media", "activism", "general"],
                    "keywords": ["digital_assembly", "online_activism", "digital_protest", "association_rights"],
                    "legal_references": ["Amnesty Digital Assembly Reports", "International Covenant on Civil and Political Rights"]
                }
            ]
            
            self.logger.info(f"Fetched {len(amnesty_principles)} Amnesty principles")
            return amnesty_principles
            
        except Exception as e:
            self.logger.error(f"Error fetching Amnesty principles: {e}")
            return []
    def load_constitution(self):
        """Load existing constitution from file"""
        try:
            if self.constitution_file.exists():
                with open(self.constitution_file, 'r') as f:
                    data = json.load(f)
                
                # Load universal principles
                for principle_data in data.get("universal_principles", []):
                    principle = ConstitutionalPrinciple(
                        id=principle_data["id"],
                        title=principle_data["title"],
                        description=principle_data["description"],
                        principle_type=PrincipleType.UNIVERSAL,
                        source=principle_data["source"],
                        weight=principle_data.get("weight", 1.0),
                        last_updated=datetime.fromisoformat(principle_data["last_updated"]),
                        domain_applicability=principle_data.get("domain_applicability", []),
                        keywords=principle_data.get("keywords", [])
                    )
                    self.universal_principles.append(principle)
                
                # Load modern rights
                for principle_data in data.get("modern_rights", []):
                    principle = ConstitutionalPrinciple(
                        id=principle_data["id"],
                        title=principle_data["title"],
                        description=principle_data["description"],
                        principle_type=PrincipleType.MODERN,
                        source=principle_data["source"],
                        weight=principle_data.get("weight", 1.0),
                        last_updated=datetime.fromisoformat(principle_data["last_updated"]),
                        domain_applicability=principle_data.get("domain_applicability", []),
                        keywords=principle_data.get("keywords", [])
                    )
                    self.modern_rights.append(principle)
                
                # Load civic principles
                for principle_data in data.get("civic_principles", []):
                    principle = ConstitutionalPrinciple(
                        id=principle_data["id"],
                        title=principle_data["title"],
                        description=principle_data["description"],
                        principle_type=PrincipleType.CIVIC,
                        source=principle_data["source"],
                        weight=principle_data.get("weight", 1.0),
                        last_updated=datetime.fromisoformat(principle_data["last_updated"]),
                        domain_applicability=principle_data.get("domain_applicability", []),
                        keywords=principle_data.get("keywords", [])
                    )
                    self.civic_principles.append(principle)
                
                # Load domain adaptations
                self.domain_adaptations = data.get("domain_adaptations", {})
                
                self.logger.info(f"Loaded constitution with {len(self.universal_principles)} universal, {len(self.modern_rights)} modern, {len(self.civic_principles)} civic principles")
            
            else:
                # Initialize with UN Declaration foundation
                self.initialize_universal_principles()
                self.initialize_civic_principles()
                self.save_constitution()
                
        except Exception as e:
            self.logger.error(f"Error loading constitution: {e}")
            # Initialize with basic principles
            self.initialize_universal_principles()
            self.initialize_civic_principles()
    
    def initialize_universal_principles(self):
        """Initialize universal principles based on UN Declaration of Human Rights"""
        universal_principles_data = [
            {
                "id": "udhr_article_1",
                "title": "Equality and Dignity",
                "description": "All human beings are born free and equal in dignity and rights. They are endowed with reason and conscience and should act towards one another in a spirit of brotherhood.",
                "source": "Universal Declaration of Human Rights, Article 1",
                "weight": 1.0,
                "domain_applicability": ["all"],
                "keywords": ["equality", "dignity", "freedom", "brotherhood"]
            },
            {
                "id": "udhr_article_2",
                "title": "Non-Discrimination",
                "description": "Everyone is entitled to all the rights and freedoms set forth in this Declaration, without distinction of any kind, such as race, colour, sex, language, religion, political or other opinion, national or social origin, property, birth or other status.",
                "source": "Universal Declaration of Human Rights, Article 2",
                "weight": 1.0,
                "domain_applicability": ["all"],
                "keywords": ["non-discrimination", "equality", "rights", "freedoms"]
            },
            {
                "id": "udhr_article_3",
                "title": "Right to Life",
                "description": "Everyone has the right to life, liberty and security of person.",
                "source": "Universal Declaration of Human Rights, Article 3",
                "weight": 1.0,
                "domain_applicability": ["all"],
                "keywords": ["life", "liberty", "security", "person"]
            },
            {
                "id": "udhr_article_12",
                "title": "Privacy Protection",
                "description": "No one shall be subjected to arbitrary interference with his privacy, family, home or correspondence, nor to attacks upon his honour and reputation. Everyone has the right to the protection of the law against such interference or attacks.",
                "source": "Universal Declaration of Human Rights, Article 12",
                "weight": 1.0,
                "domain_applicability": ["genomic_research", "personal_assistance", "civic_engagement"],
                "keywords": ["privacy", "family", "home", "correspondence", "honor", "reputation"]
            },
            {
                "id": "udhr_article_19",
                "title": "Freedom of Opinion",
                "description": "Everyone has the right to freedom of opinion and expression. This right includes freedom to hold opinions without interference and to seek, receive and impart information and ideas through any media and regardless of frontiers.",
                "source": "Universal Declaration of Human Rights, Article 19",
                "weight": 1.0,
                "domain_applicability": ["all"],
                "keywords": ["opinion", "expression", "information", "ideas", "media"]
            },
            {
                "id": "udhr_article_27",
                "title": "Scientific Progress",
                "description": "Everyone has the right freely to participate in the cultural life of the community, to enjoy the arts and to share in scientific advancement and its benefits.",
                "source": "Universal Declaration of Human Rights, Article 27",
                "weight": 1.0,
                "domain_applicability": ["genomic_research", "creative_arts", "civic_engagement"],
                "keywords": ["culture", "arts", "science", "advancement", "benefits"]
            }
        ]
        
        for principle_data in universal_principles_data:
            principle = ConstitutionalPrinciple(
                id=principle_data["id"],
                title=principle_data["title"],
                description=principle_data["description"],
                principle_type=PrincipleType.UNIVERSAL,
                source=principle_data["source"],
                weight=principle_data.get("weight", 1.0),
                domain_applicability=principle_data.get("domain_applicability", []),
                keywords=principle_data.get("keywords", [])
            )
            self.universal_principles.append(principle)
    
    def initialize_civic_principles(self):
        """Initialize civic principles based on Constella Framework"""
        civic_principles_data = [
            {
                "id": "constella_democratic_participation",
                "title": "Democratic Participation",
                "description": "All individuals have the right to participate in democratic processes and civic engagement without barriers. AI systems should facilitate rather than hinder democratic participation.",
                "source": "Constella Framework - Democratic Values",
                "weight": 1.0,
                "domain_applicability": ["civic_engagement", "personal_assistance"],
                "keywords": ["democracy", "participation", "civic", "engagement"]
            },
            {
                "id": "constella_community_building",
                "title": "Community Building",
                "description": "AI systems should support community building and social cohesion, fostering connections between people and strengthening community bonds.",
                "source": "Constella Framework - Community Principles",
                "weight": 0.8,
                "domain_applicability": ["civic_engagement", "personal_assistance"],
                "keywords": ["community", "social", "cohesion", "connections"]
            },
            {
                "id": "constella_transparency",
                "title": "Transparency and Accountability",
                "description": "AI systems must operate transparently and be accountable for their decisions and actions. Users should understand how decisions are made and have recourse for errors.",
                "source": "Constella Framework - Governance Principles",
                "weight": 1.0,
                "domain_applicability": ["all"],
                "keywords": ["transparency", "accountability", "decisions", "recourse"]
            },
            {
                "id": "constella_ethical_innovation",
                "title": "Ethical Innovation",
                "description": "Technological innovation must be guided by ethical considerations and serve human wellbeing. AI should enhance rather than diminish human capabilities and dignity.",
                "source": "Constella Framework - Innovation Principles",
                "weight": 1.0,
                "domain_applicability": ["genomic_research", "creative_arts"],
                "keywords": ["innovation", "ethics", "wellbeing", "capabilities", "dignity"]
            }
        ]
        
        for principle_data in civic_principles_data:
            principle = ConstitutionalPrinciple(
                id=principle_data["id"],
                title=principle_data["title"],
                description=principle_data["description"],
                principle_type=PrincipleType.CIVIC,
                source=principle_data["source"],
                weight=principle_data.get("weight", 1.0),
                domain_applicability=principle_data.get("domain_applicability", []),
                keywords=principle_data.get("keywords", [])
            )
            self.civic_principles.append(principle)
    
    def get_applicable_principles(self, domain: str, context: Dict[str, Any] = None) -> List[ConstitutionalPrinciple]:
        """Get principles applicable to specific domain and context"""
        applicable_principles = []
        
        # Add universal principles (always applicable)
        applicable_principles.extend(self.universal_principles)
        
        # Add modern rights (always applicable)
        applicable_principles.extend(self.modern_rights)
        
        # Add civic principles (always applicable)
        applicable_principles.extend(self.civic_principles)
        
        # Add domain-specific adaptations
        if domain in self.domain_adaptations:
            domain_principles = self.domain_adaptations[domain]
            for principle_data in domain_principles:
                principle = ConstitutionalPrinciple(
                    id=principle_data["id"],
                    title=principle_data["title"],
                    description=principle_data["description"],
                    principle_type=PrincipleType.DOMAIN,
                    source=principle_data["source"],
                    weight=principle_data.get("weight", 1.0),
                    domain_applicability=[domain],
                    keywords=principle_data.get("keywords", [])
                )
                applicable_principles.append(principle)
        
        # Filter by domain applicability
        filtered_principles = []
        for principle in applicable_principles:
            if principle.domain_applicability == ["all"] or domain in principle.domain_applicability:
                filtered_principles.append(principle)
        
        return filtered_principles
    
    def observe_action(self, action: Dict[str, Any], domain: str) -> Observation:
        """Observe an action against the constitution in the Civic Tome shape.

        The framework records WHICH principles an action *engages* — it does not rule whether
        the action is compliant, and there is no fault/verdict. Any consequence is delegated to
        an external/human process. This replaces the old keyword-policing verdict path.
        """
        applicable = self.get_applicable_principles(domain, action.get("context", {}))
        action_text = action.get("description", "") or ""
        text_l = action_text.lower()

        # Neutral relevance only: which principles does this action *touch*? (No good/bad valence.)
        engaged = []
        for p in applicable:
            terms = [str(t).lower() for t in (p.keywords or []) if t]
            if any(t in text_l for t in terms):
                engaged.append(p.id)

        scope = action.get("scope") or (action.get("context", {}) or {}).get("scope") or "individual"
        return Observation(
            action_id=action.get("id", "unknown"),
            condition=action_text or "(no description provided)",
            measures={
                "principles_considered": len(applicable),
                "principles_engaged": len(engaged),
            },
            context={"domain": domain, **(action.get("context", {}) or {})},
            scope=scope,
            provenance={
                "recorded_by": "constella_constitution.observe_action",
                "recorded_at": datetime.now().isoformat(),
                "source": action.get("source", "faithh_backend"),
            },
            resolution=("recorded for external/human review via the Civic Tome process; "
                        "the framework observes and does not rule — no automated verdict issued"),
            engaged_principles=engaged,
            claim_label=ClaimLabel.CONTESTED,
        )

    def evaluate_compliance(self, action: Dict[str, Any], domain: str) -> ComplianceReport:
        """DEPRECATED — retained only for back-compat with callers that expect a ComplianceReport
        (e.g. focus_management.check_constitutional_compliance). The framework no longer polices:
        this delegates to observe_action and ALWAYS reports compliance_level=UNKNOWN with no
        violations. Prefer observe_action(), which returns the Civic Tome Observation shape.
        """
        obs = self.observe_action(action, domain)
        return ComplianceReport(
            action_id=obs.action_id,
            action_description=obs.condition,
            domain=domain,
            compliance_level=ComplianceLevel.UNKNOWN,   # the framework does not rule
            violated_principles=[],
            partial_compliance=[],
            compliance_score=0.0,
            recommendations=[obs.resolution],
            evaluation_timestamp=obs.observation_timestamp,
        )

    def get_principle_by_id(self, principle_id: str) -> Optional[ConstitutionalPrinciple]:
        """Get principle by ID"""
        all_principles = self.universal_principles + self.modern_rights + self.civic_principles
        
        # Add domain adaptations
        for domain_principles in self.domain_adaptations.values():
            for principle_data in domain_principles:
                if principle_data["id"] == principle_id:
                    return ConstitutionalPrinciple(
                        id=principle_data["id"],
                        title=principle_data["title"],
                        description=principle_data["description"],
                        principle_type=PrincipleType.DOMAIN,
                        source=principle_data["source"],
                        weight=principle_data.get("weight", 1.0),
                        domain_applicability=[principle_data.get("domain", "unknown")],
                        keywords=principle_data.get("keywords", [])
                    )
        
        for principle in all_principles:
            if principle.id == principle_id:
                return principle
        
        return None
    
    def save_constitution(self):
        """Save constitution to file"""
        try:
            data = {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "universal_principles": [
                    {
                        "id": p.id,
                        "title": p.title,
                        "description": p.description,
                        "source": p.source,
                        "weight": p.weight,
                        "last_updated": p.last_updated.isoformat(),
                        "domain_applicability": p.domain_applicability,
                        "keywords": p.keywords
                    }
                    for p in self.universal_principles
                ],
                "modern_rights": [
                    {
                        "id": p.id,
                        "title": p.title,
                        "description": p.description,
                        "source": p.source,
                        "weight": p.weight,
                        "last_updated": p.last_updated.isoformat(),
                        "domain_applicability": p.domain_applicability,
                        "keywords": p.keywords
                    }
                    for p in self.modern_rights
                ],
                "civic_principles": [
                    {
                        "id": p.id,
                        "title": p.title,
                        "description": p.description,
                        "source": p.source,
                        "weight": p.weight,
                        "last_updated": p.last_updated.isoformat(),
                        "domain_applicability": p.domain_applicability,
                        "keywords": p.keywords
                    }
                    for p in self.civic_principles
                ],
                "domain_adaptations": self.domain_adaptations
            }
            
            with open(self.constitution_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.logger.info(f"Constitution saved to {self.constitution_file}")
            
        except Exception as e:
            self.logger.error(f"Error saving constitution: {e}")
    
    def update_modern_rights(self):
        """Update modern rights from API sources"""
        try:
            # This would implement actual API calls to human rights sources
            # For now, we'll simulate with some modern rights principles
            
            modern_rights_data = [
                {
                    "id": "modern_data_privacy",
                    "title": "Data Privacy Rights",
                    "description": "Individuals have the right to control their personal data and how it is collected, used, and shared by AI systems.",
                    "source": "Modern Privacy Regulations (GDPR, CCPA)",
                    "weight": 1.0,
                    "domain_applicability": ["all"],
                    "keywords": ["data privacy", "consent", "control", "personal data"]
                },
                {
                    "id": "modern_algorithmic_fairness",
                    "title": "Algorithmic Fairness",
                    "description": "AI systems must be designed and tested to ensure fair treatment across different demographic groups and avoid discriminatory outcomes.",
                    "source": "AI Ethics Guidelines (2020s)",
                    "weight": 1.0,
                    "domain_applicability": ["all"],
                    "keywords": ["fairness", "algorithm", "discrimination", "bias"]
                },
                {
                    "id": "modern_ai_transparency",
                    "title": "AI System Transparency",
                    "description": "AI systems must provide clear explanations of their capabilities, limitations, and decision-making processes to users and stakeholders.",
                    "source": "AI Regulation Frameworks (2020s)",
                    "weight": 1.0,
                    "domain_applicability": ["all"],
                    "keywords": ["transparency", "explainability", "capabilities", "limitations"]
                }
            ]
            
            # Clear existing modern rights and add new ones
            self.modern_rights.clear()
            
            for principle_data in modern_rights_data:
                principle = ConstitutionalPrinciple(
                    id=principle_data["id"],
                    title=principle_data["title"],
                    description=principle_data["description"],
                    principle_type=PrincipleType.MODERN,
                    source=principle_data["source"],
                    weight=principle_data.get("weight", 1.0),
                    domain_applicability=principle_data.get("domain_applicability", []),
                    keywords=principle_data.get("keywords", [])
                )
                self.modern_rights.append(principle)
            
            self.last_update = datetime.now()
            self.save_constitution()
            
            self.logger.info(f"Updated modern rights with {len(self.modern_rights)} principles")
            
        except Exception as e:
            self.logger.error(f"Error updating modern rights: {e}")
    
    def add_domain_adaptation(self, domain: str, principles: List[Dict[str, Any]]):
        """Add domain-specific adaptations"""
        self.domain_adaptations[domain] = principles
        self.save_constitution()
        self.logger.info(f"Added {len(principles)} principles for domain: {domain}")
    
    def get_constitution_summary(self) -> Dict[str, Any]:
        """Get summary of constitution"""
        return {
            "version": "1.0",
            "last_updated": self.last_update.isoformat(),
            "total_principles": len(self.universal_principles) + len(self.modern_rights) + len(self.civic_principles),
            "universal_principles": len(self.universal_principles),
            "modern_rights": len(self.modern_rights),
            "civic_principles": len(self.civic_principles),
            "domain_adaptations": len(self.domain_adaptations),
            "domains": list(self.domain_adaptations.keys()),
            "human_rights_sources": len(self.human_rights_sources)
        }

# Global instance
constella_constitution = ConstellaConstitution()