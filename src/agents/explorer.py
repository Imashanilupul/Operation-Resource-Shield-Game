"""
Explorer Agent
Scouts the map to discover resources and detect the thief
"""
import random
from config.game_config import *
from src.agents.base_agent import BaseAgent
from src.utils.helpers import distance, random_position


class ExplorerAgent(BaseAgent):
    """Agent that explores the map"""
    
    def __init__(self, agent_id: str, x: float, y: float):
        """
        Initialize explorer agent
        
        Args:
            agent_id: Unique identifier
            x: Starting X coordinate
            y: Starting Y coordinate
        """
        super().__init__(agent_id, AGENT_ROLE_EXPLORER, x, y)
        self.explored_zones = set()
        self.current_zone = None
        self.thief_last_seen = None
        self.detection_cooldown = 0
    
    def think(self) -> None:
        """Explorer decision-making logic"""
        # Process messages
        self._process_messages()
        
        # Decrement detection cooldown
        if self.detection_cooldown > 0:
            self.detection_cooldown -= 1
        
        # Select zone to explore if needed
        if self.current_zone is None:
            self._select_zone_to_explore()
        
        # Check for thief in vision range (with cooldown)
        if self.detection_cooldown <= 0:
            self._check_for_thief()
        
        # Look for resources
        self._scan_for_resources()
        
        # Report status to strategist
        self._report_status()
    
    def _select_zone_to_explore(self) -> None:
        """Select a zone to explore"""
        zones = ZONES
        # Pick unexplored zone
        unexplored = [z for z in zones if z not in self.explored_zones]
        
        if unexplored:
            self.current_zone = random.choice(unexplored)
            zone_bounds = ZONES[self.current_zone]
            target_x = (zone_bounds[0] + zone_bounds[2]) / 2
            target_y = (zone_bounds[1] + zone_bounds[3]) / 2
            self.set_target(target_x, target_y, MOVEMENT_PATROL)
            self.explored_zones.add(self.current_zone)
        else:
            # All zones explored, pick random area
            target_x = random.uniform(50, WINDOW_WIDTH - 50)
            target_y = random.uniform(50, WINDOW_HEIGHT - 50)
            self.set_target(target_x, target_y, MOVEMENT_PATROL)
            self.current_zone = None
    
    def _check_for_thief(self) -> None:
        """Check if thief is visible"""
        # This will be called with thief position from game
        # Will be implemented during game integration
        pass
    
    def _scan_for_resources(self) -> None:
        """Scan for resources in vision range"""
        # This will be called during game loop
        # Will check for resources and post to blackboard
        pass
    
    def _report_status(self) -> None:
        """Report exploration status to strategist"""
        if random.random() < 0.05:  # Report occasionally
            self.send_message(f"agent_strategist", "exploration_update", {
                "explorer_id": self.id,
                "position": self.get_position(),
                "explored_zones": len(self.explored_zones)
            })
    
    def _process_messages(self) -> None:
        """Process incoming messages"""
        messages = self.get_messages()
        for message in messages:
            if message.message_type == "scan_zone":
                # Strategist ordered to scan specific zone
                content = message.content
                if "zone" in content:
                    self.set_target(content["zone"][0], content["zone"][1])
    
    def report_resource(self, x: float, y: float) -> None:
        """Report a discovered resource directly to collector"""
        self.blackboard.add_resource_location((x, y), self.id)
        
        # Report directly to collector
        self.send_message("agent_collector_0", "resource_found", {
            "position": (x, y),
            "explorer_id": self.id
        })
        
        # Broadcast for all to know
        self.broadcast_message("resource_discovered", {
            "position": (x, y),
            "explorer_id": self.id
        })
    
    def report_thief_sighting(self, x: float, y: float) -> None:
        """Report sighting of thief to strategist"""
        # Only report if cooldown expired
        if self.detection_cooldown > 0:
            return
            
        self.thief_last_seen = (x, y)
        self.blackboard.update_thief_position((x, y), self.id)
        
        # Send message to strategist (not broadcast)
        self.send_message("agent_strategist", "thief_sighted", {
            "position": (x, y),
            "observer": self.id,
            "timestamp": self.blackboard.read_data("elapsed_time")
        })
        
        # Also broadcast alert for awareness
        self.broadcast_message("thief_sighted", {
            "position": (x, y),
            "observer": self.id
        })
        
        # Set cooldown to prevent spam (60 frames = 1 second at 60 FPS)
        self.detection_cooldown = 60
