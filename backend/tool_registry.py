"""
Tool Registry - Manages available battle chips/tools

This module provides the registry for all available tools (battle chips)
in the FAITHH system. It handles registration, lookup, and categorization
of tools.
"""
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Registry for managing tool definitions (Battle Chips)"""
    
    def __init__(self):
        """Initialize the tool registry"""
        self.tools: Dict[str, dict] = {}
        self.categories: Dict[str, List[str]] = {}
        logger.info("Tool Registry initialized")
    
    def register_tool(self, tool_definition: dict) -> bool:
        """
        Register a new tool in the registry
        
        Args:
            tool_definition: Dictionary containing tool metadata
                Required keys:
                - name: str - Unique tool identifier
                - description: str - What the tool does
                - category: str - Tool category (filesystem, process, rag, etc.)
                - executor: str - Which executor handles this tool
                - permissions: List[str] - Required permissions
                Optional keys:
                - code: str - Battle chip code (A-Z)
                - parameters: dict - Expected input parameters
        
        Returns:
            bool: True if registration successful, False otherwise
        """
        # TODO: Implement validation logic
        # - Check required fields exist
        # - Validate tool name is unique
        # - Validate executor exists
        # - Validate permission strings
        
        if not tool_definition.get('name'):
            logger.error("Tool registration failed: missing 'name'")
            return False
        
        tool_name = tool_definition['name']
        
        # Store tool definition
        self.tools[tool_name] = tool_definition
        
        # Add to category index
        category = tool_definition.get('category', 'uncategorized')
        if category not in self.categories:
            self.categories[category] = []
        self.categories[category].append(tool_name)
        
        logger.info(f"Registered tool: {tool_name} (category: {category})")
        return True
    
    def get_tool(self, name: str) -> Optional[dict]:
        """
        Get tool definition by name
        
        Args:
            name: Tool name to lookup
            
        Returns:
            dict: Tool definition or None if not found
        """
        return self.tools.get(name)
    
    def list_tools(self, category: Optional[str] = None) -> List[dict]:
        """
        List all available tools, optionally filtered by category
        
        Args:
            category: Optional category filter
            
        Returns:
            List of tool definitions
        """
        if category:
            # Return tools in specific category
            tool_names = self.categories.get(category, [])
            return [self.tools[name] for name in tool_names]
        
        # Return all tools
        return list(self.tools.values())
    
    def get_categories(self) -> List[str]:
        """
        Get list of all tool categories
        
        Returns:
            List of category names
        """
        return list(self.categories.keys())
    
    def unregister_tool(self, name: str) -> bool:
        """
        Remove a tool from the registry
        
        Args:
            name: Tool name to remove
            
        Returns:
            bool: True if removed, False if not found
        """
        if name not in self.tools:
            return False
        
        # Remove from category index
        tool_def = self.tools[name]
        category = tool_def.get('category', 'uncategorized')
        if category in self.categories:
            self.categories[category].remove(name)
        
        # Remove tool
        del self.tools[name]
        logger.info(f"Unregistered tool: {name}")
        return True


# Global registry instance
_registry = None

def get_registry() -> ToolRegistry:
    """Get the global tool registry instance"""
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
    return _registry
