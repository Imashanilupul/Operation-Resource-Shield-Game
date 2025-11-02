"""
Base Agent Class
Foundation for all agent types with common functionality
"""
from abc import ABC, abstractmethod
from typing import Tuple, Optional
import pygame
from config.game_config import *
from src.utils.helpers import distance, clamp_position, move_towards, random_direction
from src.communication.blackboard import get_blackboard, Message


class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, agent_id: str, role: str, x: float, y: float):
        """
        Initialize a base agent
        
        Args:
            agent_id: Unique identifier for the agent
            role: Role of the agent
            x: Starting X coordinate
            y: Starting Y coordinate
        """
        self.id = agent_id
        self.role = role
        self.x = x
        self.y = y
        self.speed = AGENT_SPEED
        self.size = AGENT_SIZE
        self.vision_range = AGENT_VISION_RANGE
        self.communication_range = AGENT_COMMUNICATION_RANGE
        
        # Movement state
        self.vx = 0
        self.vy = 0
        self.target_position: Optional[Tuple[float, float]] = None
        self.movement_type = MOVEMENT_PATROL
        
        # State
        self.active = True
        self.carrying = []  # For collector agents
        self.energy = 100
        self.max_energy = 100
        
        # Communication
        self.blackboard = get_blackboard()
        self.messages = []
        
        # Debug
        self.path_points = []
    
    def get_position(self) -> Tuple[float, float]:
        """Get agent position"""
        return (self.x, self.y)
    
    def set_position(self, x: float, y: float) -> None:
        """Set agent position"""
        self.x, self.y = clamp_position((x, y), WINDOW_WIDTH, WINDOW_HEIGHT)
    
    def set_target(self, target_x: float, target_y: float, movement_type: str = MOVEMENT_PATROL) -> None:
        """
        Set movement target
        
        Args:
            target_x: Target X coordinate
            target_y: Target Y coordinate
            movement_type: Type of movement
        """
        self.target_position = (target_x, target_y)
        self.movement_type = movement_type
    
    def move(self, obstacles=None) -> None:
        """
        Move the agent towards target
        
        Args:
            obstacles: List of obstacles to avoid
        """
        if not self.target_position or not self.active:
            return
        
        # Move towards target
        new_pos = move_towards(self.get_position(), self.target_position, self.speed)
        
        # Check if blocked by obstacle
        if obstacles and any(obs.contains_circle(new_pos[0], new_pos[1], self.size) 
                            for obs in obstacles):
            # Attempt to move around obstacle
            self._move_around_obstacle(new_pos, obstacles)
        else:
            self.set_position(new_pos[0], new_pos[1])
        
        # Check if reached target
        if distance(self.get_position(), self.target_position) < self.speed:
            self.target_position = None
    
    def _move_around_obstacle(self, blocked_pos: Tuple[float, float], obstacles) -> None:
        """Try to move around an obstacle"""
        # Simple avoidance: try adjacent positions
        for dx in [-5, 5]:
            for dy in [-5, 5]:
                test_pos = (blocked_pos[0] + dx, blocked_pos[1] + dy)
                if not any(obs.contains_circle(test_pos[0], test_pos[1], self.size) 
                          for obs in obstacles):
                    self.set_position(test_pos[0], test_pos[1])
                    return
        
        # If can't move around, stay in place
        return
    
    def patrol(self, map_width: float, map_height: float) -> None:
        """
        Patrol randomly
        
        Args:
            map_width: Map width
            map_height: Map height
        """
        if self.target_position is None or distance(self.get_position(), self.target_position) < 10:
            # Pick new random target
            import random
            target_x = random.uniform(30, map_width - 30)
            target_y = random.uniform(30, map_height - 30)
            self.set_target(target_x, target_y, MOVEMENT_PATROL)
    
    def send_message(self, recipient: str, message_type: str, content) -> None:
        """
        Send a message through blackboard
        
        Args:
            recipient: Recipient agent ID
            message_type: Type of message
            content: Message content
        """
        message = Message(self.id, recipient, message_type, content)
        self.blackboard.send_message(message)
    
    def broadcast_message(self, message_type: str, content) -> None:
        """
        Broadcast a message to all agents
        
        Args:
            message_type: Type of message
            content: Message content
        """
        self.blackboard.broadcast_message(self.id, message_type, content)
    
    def get_messages(self) -> list:
        """Get unread messages for this agent"""
        return self.blackboard.get_messages(self.id, unread_only=True)
    
    def can_see(self, x: float, y: float) -> bool:
        """
        Check if agent can see a position
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if within vision range
        """
        return distance(self.get_position(), (x, y)) <= self.vision_range
    
    def can_communicate(self, agent: 'BaseAgent') -> bool:
        """
        Check if can communicate with another agent
        
        Args:
            agent: Other agent
            
        Returns:
            True if within communication range
        """
        return distance(self.get_position(), agent.get_position()) <= self.communication_range
    
    def consume_energy(self, amount: float) -> None:
        """Consume energy"""
        self.energy = max(0, self.energy - amount)
    
    def restore_energy(self, amount: float = 10) -> None:
        """Restore energy"""
        self.energy = min(self.max_energy, self.energy + amount)
    
    def update(self, obstacles=None) -> None:
        """
        Update agent state
        
        Args:
            obstacles: List of obstacles
        """
        if not self.active:
            return
        
        # Move towards target or patrol
        if self.target_position:
            self.move(obstacles)
        else:
            self.patrol(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Restore some energy
        if self.energy < self.max_energy:
            self.restore_energy(0.5)
    
    @abstractmethod
    def think(self) -> None:
        """Agent decision-making logic - to be implemented by subclasses"""
        pass
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the agent"""
        # Draw agent circle
        color_map = {
            AGENT_ROLE_EXPLORER: COLOR_BLUE,
            AGENT_ROLE_COLLECTOR: COLOR_GREEN,
            AGENT_ROLE_ATTACKER: COLOR_RED,
            AGENT_ROLE_STRATEGIST: COLOR_MAGENTA,
        }
        color = color_map.get(self.role, COLOR_GRAY)
        
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(surface, COLOR_WHITE, (int(self.x), int(self.y)), self.size, 2)
        
        # Draw vision range (debug)
        if SHOW_AGENT_VISION and DEBUG_MODE:
            pygame.draw.circle(surface, color, (int(self.x), int(self.y)), 
                              self.vision_range, 1)
        
        # Draw role label
        font = pygame.font.Font(None, 16)
        label = font.render(self.role[0].upper(), True, COLOR_WHITE)
        surface.blit(label, (self.x - 4, self.y - 4))
    
    def reset(self) -> None:
        """Reset agent to initial state"""
        self.vx = 0
        self.vy = 0
        self.target_position = None
        self.movement_type = MOVEMENT_PATROL
        self.active = True
        self.carrying.clear()
        self.energy = self.max_energy
        self.messages.clear()
