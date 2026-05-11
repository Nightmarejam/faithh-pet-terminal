#!/usr/bin/env python3
"""
FAITHH Knowledge Graph Loader
Loads and queries the YAML knowledge graph for self-awareness capabilities.

This module provides FAITHH with the ability to reason about:
- Its own architecture and capabilities
- Project relationships
- Development priorities
- Shared vocabulary

Usage:
    from knowledge_graph import KnowledgeGraph
    
    kg = KnowledgeGraph()
    kg.load("faithh_knowledge_graph.yaml")
    
    # Query examples
    priorities = kg.get("entities.faithh.development_priorities.high")
    relationships = kg.get_relationships("faithh")
    vocab = kg.get_vocabulary("tom_cat_sound")
"""

import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class Relationship:
    """Represents a relationship between entities"""
    from_entity: Union[str, List[str]]
    to_entity: str
    rel_type: str
    description: str


class KnowledgeGraph:
    """
    Loads and queries the FAITHH knowledge graph.
    
    The knowledge graph is a YAML file containing:
    - entities: Projects, people, systems
    - relationships: How entities connect
    - indexing_rules: Quality filter configuration
    - vocabulary: Shared terminology
    """
    
    DEFAULT_PATH = Path.home() / "ai-stack" / "faithh_knowledge_graph.yaml"
    
    def __init__(self, path: Optional[Path] = None):
        """Initialize with optional path to knowledge graph."""
        self.path = path or self.DEFAULT_PATH
        self._data: Dict = {}
        self._loaded = False
        self._load_time: Optional[datetime] = None
    
    def load(self, path: Optional[Path] = None) -> bool:
        """
        Load the knowledge graph from YAML.
        
        Args:
            path: Optional path override
            
        Returns:
            True if loaded successfully
        """
        load_path = path or self.path
        
        if not load_path.exists():
            print(f"Warning: Knowledge graph not found at {load_path}")
            return False
        
        try:
            with open(load_path, 'r') as f:
                # Handle multi-document YAML
                docs = list(yaml.safe_load_all(f))
            
            # Merge all documents
            self._data = {}
            for doc in docs:
                if doc:
                    self._data.update(doc)
            
            self._loaded = True
            self._load_time = datetime.now()
            return True
            
        except Exception as e:
            print(f"Error loading knowledge graph: {e}")
            return False
    
    def ensure_loaded(self):
        """Ensure the knowledge graph is loaded."""
        if not self._loaded:
            self.load()
    
    def get(self, path: str, default: Any = None) -> Any:
        """
        Get a value from the knowledge graph using dot notation.
        
        Args:
            path: Dot-separated path (e.g., "entities.faithh.status")
            default: Default value if path not found
            
        Returns:
            Value at path or default
        """
        self.ensure_loaded()
        
        keys = path.split('.')
        current = self._data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        
        return current
    
    def get_entity(self, name: str) -> Optional[Dict]:
        """Get an entity by name."""
        return self.get(f"entities.{name}")
    
    def get_relationships(self, entity: str) -> List[Relationship]:
        """
        Get all relationships involving an entity.
        
        Args:
            entity: Entity name to find relationships for
            
        Returns:
            List of Relationship objects
        """
        self.ensure_loaded()
        
        relationships = []
        raw_rels = self.get("relationships", [])
        
        for rel in raw_rels:
            from_ent = rel.get('from', '')
            to_ent = rel.get('to', '')
            
            # Check if entity is involved
            is_from = (entity == from_ent or 
                      (isinstance(from_ent, list) and entity in from_ent))
            is_to = entity == to_ent
            
            if is_from or is_to:
                relationships.append(Relationship(
                    from_entity=from_ent,
                    to_entity=to_ent,
                    rel_type=rel.get('type', 'unknown'),
                    description=rel.get('description', '')
                ))
        
        return relationships
    
    def get_vocabulary(self, term: str) -> List[str]:
        """
        Get all aliases for a term.
        
        Args:
            term: Term to look up (e.g., "tom_cat_sound")
            
        Returns:
            List of aliases including the original term
        """
        # Check project names
        aliases = self.get(f"vocabulary.project_names.{term}", [])
        if aliases:
            return aliases
        
        # Check people
        aliases = self.get(f"vocabulary.people.{term}", [])
        if aliases:
            return aliases
        
        # Check concepts
        concept = self.get(f"vocabulary.concepts.{term}")
        if concept:
            return [term, concept]  # Return term and its definition
        
        return [term]
    
    def get_indexing_rules(self) -> Dict:
        """Get indexing rules for quality filter."""
        return self.get("indexing_rules", {})
    
    def get_development_priorities(self) -> Dict[str, List[str]]:
        """Get FAITHH development priorities by level."""
        return self.get("entities.faithh.development_priorities", {})
    
    def get_known_issues(self) -> Dict[str, List[str]]:
        """Get known issues by component."""
        issues = {}
        components = self.get("entities.faithh.architecture.components", {})
        
        for comp_name, comp_data in components.items():
            comp_issues = comp_data.get('known_issues', [])
            if comp_issues:
                issues[comp_name] = comp_issues
        
        return issues
    
    def get_decisions_log(self) -> List[Dict]:
        """Get the decisions log."""
        return self.get("entities.faithh.decisions_log", [])
    
    def add_decision(self, decision: str, reasoning: str) -> bool:
        """
        Add a new decision to the log.
        
        Args:
            decision: What was decided
            reasoning: Why it was decided
            
        Returns:
            True if added successfully
        """
        self.ensure_loaded()
        
        try:
            # Get current log
            log = self.get("entities.faithh.decisions_log", [])
            
            # Add new entry
            log.append({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "decision": decision,
                "reasoning": reasoning
            })
            
            # Update in memory
            if "entities" not in self._data:
                self._data["entities"] = {}
            if "faithh" not in self._data["entities"]:
                self._data["entities"]["faithh"] = {}
            self._data["entities"]["faithh"]["decisions_log"] = log
            
            # Save to file
            return self.save()
            
        except Exception as e:
            print(f"Error adding decision: {e}")
            return False
    
    def save(self, path: Optional[Path] = None) -> bool:
        """
        Save the knowledge graph back to YAML.
        
        Args:
            path: Optional path override
            
        Returns:
            True if saved successfully
        """
        save_path = path or self.path
        
        try:
            with open(save_path, 'w') as f:
                yaml.dump(self._data, f, default_flow_style=False, sort_keys=False)
            return True
        except Exception as e:
            print(f"Error saving knowledge graph: {e}")
            return False
    
    def get_context_for_query(self, query: str) -> str:
        """
        Generate context string relevant to a query.
        
        This can be injected into prompts to give FAITHH self-awareness.
        
        Args:
            query: User's query
            
        Returns:
            Context string with relevant knowledge graph info
        """
        self.ensure_loaded()
        
        query_lower = query.lower()
        context_parts = []
        
        # Check if asking about FAITHH itself
        if any(term in query_lower for term in ['faithh', 'yourself', 'your', 'you']):
            faithh = self.get_entity('faithh')
            if faithh:
                context_parts.append(
                    f"FAITHH Status: {faithh.get('status', 'unknown')}\n"
                    f"Purpose: {faithh.get('purpose', {}).get('primary', 'Unknown')}"
                )
                
                # Add priorities if asking about what to do
                if any(word in query_lower for word in ['priority', 'next', 'should', 'todo']):
                    priorities = self.get_development_priorities()
                    if priorities.get('high'):
                        context_parts.append(
                            f"High Priorities: {', '.join(priorities['high'])}"
                        )
        
        # Check if asking about projects
        for project in ['tom_cat_sound', 'constella']:
            aliases = self.get_vocabulary(project)
            if any(alias.lower() in query_lower for alias in aliases):
                entity = self.get_entity(project)
                if entity:
                    context_parts.append(
                        f"{project} Status: {entity.get('status', 'unknown')}"
                    )
        
        # Check if asking about relationships
        if any(word in query_lower for word in ['connect', 'relate', 'relationship', 'between']):
            # Find mentioned entities
            for entity in ['tom_cat_sound', 'faithh', 'constella']:
                if entity.replace('_', ' ') in query_lower or entity in query_lower:
                    rels = self.get_relationships(entity)
                    for rel in rels[:3]:  # Limit to 3
                        context_parts.append(
                            f"{rel.from_entity} → {rel.rel_type} → {rel.to_entity}: {rel.description}"
                        )
        
        # Check if asking about issues
        if any(word in query_lower for word in ['issue', 'problem', 'bug', 'broken', 'fix']):
            issues = self.get_known_issues()
            for comp, issue_list in issues.items():
                context_parts.append(f"{comp} issues: {', '.join(issue_list)}")
        
        if context_parts:
            return "\n[Knowledge Graph Context]\n" + "\n".join(context_parts) + "\n"
        return ""
    
    def to_markdown(self) -> str:
        """
        Export knowledge graph summary as markdown.
        
        Useful for injecting into system prompts.
        """
        self.ensure_loaded()
        
        lines = ["# FAITHH Knowledge Graph Summary\n"]
        
        # Entities
        lines.append("## Entities\n")
        entities = self.get("entities", {})
        for name, data in entities.items():
            if isinstance(data, dict):
                status = data.get('status', 'unknown')
                lines.append(f"- **{name}**: {status}")
        
        # Relationships
        lines.append("\n## Relationships\n")
        for rel in self.get("relationships", [])[:5]:
            lines.append(
                f"- {rel.get('from')} → {rel.get('type')} → {rel.get('to')}"
            )
        
        # Priorities
        lines.append("\n## Current Priorities\n")
        priorities = self.get_development_priorities()
        for item in priorities.get('high', [])[:3]:
            lines.append(f"- 🔴 {item}")
        
        return "\n".join(lines)


# Singleton instance for easy access
_kg_instance: Optional[KnowledgeGraph] = None


def get_knowledge_graph() -> KnowledgeGraph:
    """Get the global knowledge graph instance."""
    global _kg_instance
    if _kg_instance is None:
        _kg_instance = KnowledgeGraph()
        _kg_instance.load()
    return _kg_instance


# CLI for testing
if __name__ == "__main__":
    import sys
    
    print("=" * 70)
    print("FAITHH Knowledge Graph - Test Mode")
    print("=" * 70)
    
    # Try to load
    kg = KnowledgeGraph()
    
    # Check if file exists in current directory
    local_path = Path("faithh_knowledge_graph.yaml")
    if local_path.exists():
        kg.path = local_path
    
    if kg.load():
        print(f"✅ Loaded from {kg.path}")
        print(f"   Load time: {kg._load_time}")
        print()
        
        # Test queries
        print("Testing queries:\n")
        
        print("1. FAITHH status:")
        print(f"   {kg.get('entities.faithh.status')}")
        
        print("\n2. Development priorities (high):")
        for p in kg.get_development_priorities().get('high', []):
            print(f"   - {p}")
        
        print("\n3. Tom Cat Sound relationships:")
        for rel in kg.get_relationships('tom_cat_sound'):
            print(f"   - {rel.rel_type} → {rel.to_entity}")
        
        print("\n4. Known issues:")
        for comp, issues in kg.get_known_issues().items():
            print(f"   {comp}: {issues}")
        
        print("\n5. Vocabulary test (tom_cat_sound):")
        print(f"   {kg.get_vocabulary('tom_cat_sound')}")
        
        print("\n6. Context for query 'What should FAITHH work on next?':")
        print(kg.get_context_for_query("What should FAITHH work on next?"))
        
    else:
        print(f"❌ Could not load knowledge graph")
        print(f"   Expected at: {kg.path}")
        print("\n   Create it by copying faithh_knowledge_graph.yaml to ~/ai-stack/")
