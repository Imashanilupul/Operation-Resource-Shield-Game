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
        # Process messages from explorer/strategist
        self._process_messages()
        
        # Check if at base
        if self.base_camp.is_agent_inside(self.x, self.y, self.size):
            if len(self.carrying) > 0:
                # Deliver resources immediately
                self._deliver_resources()
                self.returning_to_base = False
                self.current_target_resource = None
            else:
                # No resources to deliver, look for targets
                if not self.current_target_resource:
                    # Patrol near base while waiting for orders
                    self._patrol_base()
        # If returning to base, prioritize that
        elif self.returning_to_base:
            self._return_to_base()
        # If has target resource, move to it
        elif self.current_target_resource:
            self._move_to_resource()
        else:
            # Check if can see any resources nearby
            visible_resource = self._check_visible_resources()
            if visible_resource:
                self.current_target_resource = visible_resource
                self.set_target(visible_resource[0], visible_resource[1], MOVEMENT_COLLECT)
            else:
                # Idle near base, waiting for orders
                self._patrol_base()
    
    def _find_resource_target(self) -> None:
        """Find nearest resource to collect"""
        resource_locations = self.blackboard.read_data("resources_locations")
        
        if resource_locations:
            # Find nearest resource
            nearest = min(resource_locations,
                         key=lambda r: distance(self.get_position(), r))
            self.current_target_resource = nearest
            self.set_target(nearest[0], nearest[1], MOVEMENT_COLLECT)
    
    def _check_visible_resources(self) -> tuple:
        """
        Check for resources within vision range and return nearest one
        
        Returns:
            Tuple of (x, y) for nearest visible resource, or None
        """
        if not self.resource_manager:
            return None
        
        # Get all active resources
        resources = self.resource_manager.resources
        
        if not resources:
            return None
        
        # Find resources within vision range
        visible_resources = []
        for resource in resources:
            res_pos = resource.get_position()
            dist = distance(self.get_position(), res_pos)
            
            # Check if within collector's vision range
            if dist <= self.vision_range and len(self.carrying) < self.carrying_capacity:
                visible_resources.append((res_pos, dist))
        
        # Return nearest visible resource
        if visible_resources:
            nearest = min(visible_resources, key=lambda x: x[1])
            return nearest[0]
        
        return None
    
    def _move_to_resource(self) -> None:
        """Move to target resource"""
        if not self.current_target_resource:
            return
        
        # Check if reached resource (increased tolerance to 30px for easier collection)
        dist_to_resource = distance(self.get_position(), self.current_target_resource)
        if dist_to_resource < 30:
            self._collect_resource()
            # After collecting, clear target
            if not self.current_target_resource or self.current_target_resource is None:
                # Resource was collected, check if at capacity
                if len(self.carrying) >= self.carrying_capacity:
                    self.returning_to_base = True
        else:
            # Still moving to resource, update target to ensure we keep moving
            self.set_target(self.current_target_resource[0], self.current_target_resource[1], MOVEMENT_COLLECT)
    
    def _collect_resource(self) -> None:
        """Collect a resource"""
        if not self.current_target_resource or len(self.carrying) >= self.carrying_capacity:
            return
        
        if self.resource_manager:
            # Get resource at this position with larger search radius
            resource = self.resource_manager.get_resource_at(
                self.current_target_resource[0],
                self.current_target_resource[1],
                radius=50  # Increased search radius
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
                        "total_carrying": len(self.carrying),
                        "position": self.current_target_resource
                    })
                    # Clear target after successful collection
                    self.current_target_resource = None
            else:
                # Resource not found at target location - clear target and look elsewhere
                self.current_target_resource = None
    
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
        """Process incoming messages from explorer"""
        messages = self.get_messages()
        for message in messages:
            if message.message_type == "base_breached":
                # Alert! Return to base immediately
                self.returning_to_base = True
            elif message.message_type == "resource_found":
                # Explorer found a resource - go collect it
                content = message.content
                if "position" in content:
                    self.current_target_resource = tuple(content["position"])
                    # Set target to move to resource
                    self.set_target(self.current_target_resource[0], self.current_target_resource[1], MOVEMENT_COLLECT)
    
    def _patrol_base(self) -> None:
        """Patrol near base camp while waiting for orders"""
        import random
        import math
        
        # Patrol in a circle around base
        base_pos = self.base_camp.get_position()
        angle = random.uniform(0, 2 * math.pi)
        patrol_radius = 80
        
        patrol_x = base_pos[0] + patrol_radius * math.cos(angle)
        patrol_y = base_pos[1] + patrol_radius * math.sin(angle)
        
        self.set_target(patrol_x, patrol_y, MOVEMENT_PATROL)
    
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
