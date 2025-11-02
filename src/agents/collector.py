"""
Collector Agent
Gathers resources and delivers them to base camp
"""
from config.game_config import *
from src.agents.base_agent import BaseAgent
from src.utils.helpers import distance


class CollectorAgent(BaseAgent):
    """Agent that collects resources"""
    
    def __init__(self, agent_id: str, x: float, y: float, base_camp, resource_manager=None):
        """
        Initialize collector agent
        
        Args:
            agent_id: Unique identifier
            x: Starting X coordinate
            y: Starting Y coordinate
            base_camp: Reference to base camp
            resource_manager: Reference to resource manager
        """
        super().__init__(agent_id, AGENT_ROLE_COLLECTOR, x, y)
        self.base_camp = base_camp
        self.resource_manager = resource_manager
        self.carrying_capacity = 5
        self.current_target_resource = None
        self.returning_to_base = False
    
    def think(self) -> None:
        """Collector decision-making logic"""
        # Process messages
        self._process_messages()
        
        # Check if at base
        if self.base_camp.is_agent_inside(self.x, self.y, self.size):
            if len(self.carrying) > 0:
                self._deliver_resources()
                self.returning_to_base = False
            else:
                self._find_resource_target()
        
        # If returning to base
        if self.returning_to_base:
            self._return_to_base()
        # If has target resource, move to it
        elif self.current_target_resource:
            self._move_to_resource()
        else:
            self._find_resource_target()
    
    def _find_resource_target(self) -> None:
        """Find nearest resource to collect"""
        resource_locations = self.blackboard.read_data("resources_locations")
        
        if resource_locations:
            # Find nearest resource
            nearest = min(resource_locations,
                         key=lambda r: distance(self.get_position(), r))
            self.current_target_resource = nearest
            self.set_target(nearest[0], nearest[1], MOVEMENT_COLLECT)
    
    def _move_to_resource(self) -> None:
        """Move to target resource"""
        if not self.current_target_resource:
            return
        
        # Check if reached resource
        if distance(self.get_position(), self.current_target_resource) < 20:
            self._collect_resource()
            self.current_target_resource = None
            
            # If at carrying capacity, return to base
            if len(self.carrying) >= self.carrying_capacity:
                self.returning_to_base = True
    
    def _collect_resource(self) -> None:
        """Collect a resource"""
        if len(self.carrying) < self.carrying_capacity and self.resource_manager:
            # Get resource at this position
            resource = self.resource_manager.get_resource_at(
                self.current_target_resource[0],
                self.current_target_resource[1],
                radius=30
            )
            
            if resource:
                # Collect from resource manager (removes it)
                if self.resource_manager.collect_resource(resource):
                    self.carrying.append({
                        "position": self.current_target_resource,
                        "value": RESOURCE_VALUE
                    })
                    self.broadcast_message("resource_collected", {
                        "collector_id": self.id,
                        "total_carrying": len(self.carrying)
                    })
    
    def _return_to_base(self) -> None:
        """Return to base camp"""
        base_pos = self.base_camp.get_position()
        self.set_target(base_pos[0], base_pos[1], MOVEMENT_RETURN_HOME)
    
    def _deliver_resources(self) -> None:
        """Deliver resources to base"""
        delivered_count = len(self.carrying)
        self.base_camp.add_resources(delivered_count)
        self.carrying.clear()
        
        self.broadcast_message("resources_delivered", {
            "collector_id": self.id,
            "count": delivered_count,
            "total_at_base": self.base_camp.get_resources()
        })
    
    def _process_messages(self) -> None:
        """Process incoming messages"""
        messages = self.get_messages()
        for message in messages:
            if message.message_type == "base_breached":
                # Alert! Return to base immediately
                self.returning_to_base = True
            elif message.message_type == "collect_resource":
                # Strategist assigned a resource
                content = message.content
                if "position" in content:
                    self.current_target_resource = tuple(content["position"])
    
    def check_for_theft(self, base_resources_before: int, base_resources_after: int) -> None:
        """
        Check if base was robbed
        
        Args:
            base_resources_before: Resource count before
            base_resources_after: Resource count after
        """
        if base_resources_after < base_resources_before:
            stolen_count = base_resources_before - base_resources_after
            self.broadcast_message("base_breached", {
                "collector_id": self.id,
                "resources_stolen": stolen_count
            })
