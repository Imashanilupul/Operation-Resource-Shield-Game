"""
Strategist Agent
Coordinates all agents and makes strategic decisions
"""
from config.game_config import *
from src.agents.base_agent import BaseAgent
from src.utils.helpers import distance


class StrategistAgent(BaseAgent):
    """Agent that coordinates team strategy - stays at base"""
    
    def __init__(self, agent_id: str, x: float, y: float):
        """
        Initialize strategist agent
        
        Args:
            agent_id: Unique identifier
            x: Starting X coordinate (should be base camp)
            y: Starting Y coordinate (should be base camp)
        """
        super().__init__(agent_id, AGENT_ROLE_STRATEGIST, x, y)
        self.known_agents = {}
        self.decision_counter = 0
        self.last_command_time = {}
        self.base_x = x  # Keep reference to base position
        self.base_y = y  # Keep reference to base position
    
    def move(self, obstacles=None) -> None:
        """
        Override move - strategist stays at base
        """
        # Strategist doesn't move, stays at base camp
        self.set_position(self.base_x, self.base_y)
    
    def think(self) -> None:
        """Strategist decision-making logic"""
        self.decision_counter += 1
        
        # Get current game state
        self._update_game_state()
        
        # Make strategic decisions
        if self.decision_counter % 30 == 0:  # Every 0.5 seconds
            self._make_strategic_decisions()
        
        # Process alerts and messages
        self._process_alerts()
        self._process_messages()
    
    def _update_game_state(self) -> None:
        """Update understanding of game state"""
        thief_pos = self.blackboard.read_data("thief_position")
        resources_at_base = self.blackboard.read_data("resources_at_base")
        base_status = self.blackboard.read_data("base_status")
        
        # Update strategist's knowledge
        self.current_state = {
            "thief_position": thief_pos,
            "resources_at_base": resources_at_base,
            "base_status": base_status
        }
    
    def _make_strategic_decisions(self) -> None:
        """Make strategic decisions and issue commands"""
        thief_pos = self.current_state.get("thief_position")
        resources = self.current_state.get("resources_at_base", 0)
        
        # Rule 1: If thief detected, intercept
        if thief_pos:
            self._command_intercept(thief_pos)
        
        # Rule 2: If resources low, increase collection
        if resources < 5:
            self._command_gather_resources()
        
        # Rule 3: If base breached, alert attacker
        if self.current_state.get("base_status") == "breached":
            self._command_defend_base()
    
    def _command_intercept(self, thief_position: tuple) -> None:
        """Command attacker to intercept thief"""
        self.send_message(
            f"agent_attacker_0",
            "intercept_command",
            {"target_position": thief_position}
        )
    
    def _command_gather_resources(self) -> None:
        """Command collectors to gather resources"""
        resource_locations = self.blackboard.read_data("resources_locations")
        
        if resource_locations:
            for idx, location in enumerate(resource_locations[:2]):  # Command first 2
                self.send_message(
                    f"agent_collector_{idx}",
                    "collect_resource",
                    {"position": location}
                )
    
    def _command_defend_base(self) -> None:
        """Command agents to defend base"""
        self.send_message(
            f"agent_attacker_0",
            "defend_base",
            {"base_position": (BASE_CAMP_X, BASE_CAMP_Y)}
        )
    
    def _process_alerts(self) -> None:
        """Process alerts from blackboard"""
        alerts = self.blackboard.get_alerts(clear=True)
        
        for alert in alerts:
            if alert['type'] == "thief_sighting":
                # Update threat level
                self.current_threat_level = "high"
            elif alert['type'] == "base_breached":
                # Immediate response
                self.blackboard.post_data("base_status", "breached")
    
    def _process_messages(self) -> None:
        """Process incoming messages from other agents"""
        messages = self.get_messages()
        
        for message in messages:
            if message.message_type == "resource_discovered":
                # Coordinator resource location
                pass
            elif message.message_type == "resources_delivered":
                # Update resource count
                content = message.content
                if "total_at_base" in content:
                    self.blackboard.post_data("resources_at_base", 
                                             content["total_at_base"])
            elif message.message_type == "base_breached":
                # Alert! Thief in base
                self.blackboard.post_data("base_status", "breached")
    
    def register_agent(self, agent_id: str, agent_role: str) -> None:
        """Register an agent under strategist's command"""
        self.known_agents[agent_id] = agent_role
    
    def get_team_status(self) -> dict:
        """Get status of entire team"""
        return {
            "agents": self.known_agents,
            "threat_level": getattr(self, 'current_threat_level', 'low'),
            "game_state": self.current_state
        }
