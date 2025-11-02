"""
Attacker Agent
Pursues and attempts to capture the thief
"""
from config.game_config import *
from src.agents.base_agent import BaseAgent
from src.utils.helpers import distance, move_towards


class AttackerAgent(BaseAgent):
    """Agent that pursues the thief"""
    
    def __init__(self, agent_id: str, x: float, y: float):
        """
        Initialize attacker agent
        
        Args:
            agent_id: Unique identifier
            x: Starting X coordinate
            y: Starting Y coordinate
        """
        super().__init__(agent_id, AGENT_ROLE_ATTACKER, x, y)
        self.speed = AGENT_SPEED * 1.1  # Slightly faster
        self.thief_position = None
        self.last_known_thief_position = None
        self.pursuit_cooldown = 0
        self.is_pursuing = False
    
    def think(self) -> None:
        """Attacker decision-making logic"""
        # Process messages
        self._process_messages()
        
        # Update thief position from blackboard
        self.thief_position = self.blackboard.read_data("thief_position")
        
        # If thief is detected, pursue
        if self.thief_position:
            self._pursue_thief()
            self.is_pursuing = True
        elif self.last_known_thief_position:
            # Move to last known position
            self._move_to_last_known_position()
            self.is_pursuing = False
        else:
            # Patrol near base camp
            self._patrol_base_defense()
    
    def _pursue_thief(self) -> None:
        """Pursue the thief"""
        if not self.thief_position:
            return
        
        self.last_known_thief_position = self.thief_position
        
        # Check if in catching range
        dist_to_thief = distance(self.get_position(), self.thief_position)
        
        if dist_to_thief < CATCHING_DISTANCE:
            # Caught the thief!
            self.broadcast_message("thief_caught", {
                "attacker_id": self.id,
                "thief_position": self.thief_position
            })
        else:
            # Move towards thief
            self.set_target(self.thief_position[0], self.thief_position[1], MOVEMENT_PURSUE)
    
    def _move_to_last_known_position(self) -> None:
        """Move to last known thief position"""
        if not self.last_known_thief_position:
            return
        
        # Check if reached position
        if distance(self.get_position(), self.last_known_thief_position) < 20:
            self.last_known_thief_position = None
        else:
            self.set_target(self.last_known_thief_position[0],
                          self.last_known_thief_position[1], MOVEMENT_PURSUE)
    
    def _patrol_base_defense(self) -> None:
        """Patrol around base camp for defense"""
        import random
        from config.game_config import BASE_CAMP_X, BASE_CAMP_Y
        
        if self.target_position is None or distance(self.get_position(), self.target_position) < 20:
            # Pick random position around base
            angle = random.uniform(0, 2 * 3.14159)
            radius = 100
            import math
            target_x = BASE_CAMP_X + radius * math.cos(angle)
            target_y = BASE_CAMP_Y + radius * math.sin(angle)
            self.set_target(target_x, target_y, MOVEMENT_PATROL)
    
    def _process_messages(self) -> None:
        """Process incoming messages"""
        messages = self.get_messages()
        for message in messages:
            if message.message_type == "thief_sighted":
                content = message.content
                if "position" in content:
                    self.thief_position = tuple(content["position"])
                    self.last_known_thief_position = self.thief_position
            elif message.message_type == "intercept_command":
                # Strategist gave interception command
                content = message.content
                if "target_position" in content:
                    self.set_target(content["target_position"][0],
                                  content["target_position"][1], MOVEMENT_PURSUE)
    
    def check_thief_collision(self, player_x: float, player_y: float, player_size: float) -> bool:
        """
        Check if caught the thief
        
        Args:
            player_x: Thief X coordinate
            player_y: Thief Y coordinate
            player_size: Thief size
            
        Returns:
            True if thief is caught
        """
        dist = distance(self.get_position(), (player_x, player_y))
        return dist < (self.size + player_size + CATCHING_DISTANCE)
