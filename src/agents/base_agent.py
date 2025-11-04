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
        
        # Set vision range based on role
        if role == AGENT_ROLE_COLLECTOR:
            self.vision_range = COLLECTOR_VISION_RANGE
        else:
            self.vision_range = AGENT_VISION_RANGE
            
        self.communication_range = AGENT_COMMUNICATION_RANGE
        
        # Movement state
        self.vx = 0
        self.vy = 0
        self.target_position: Optional[Tuple[float, float]] = None
        self.movement_type = MOVEMENT_PATROL
        self.last_positions = []  # Track last positions to detect stuck state
        self.stuck_counter = 0
        
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
        Move the agent towards target with advanced obstacle avoidance
        
        Args:
            obstacles: List of obstacles to avoid
        """
        if not self.target_position or not self.active:
            return
        
        current = self.get_position()
        target = self.target_position
        dist_to_target = distance(current, target)
        
        # Check if reached target (with proper tolerance)
        if dist_to_target < self.speed + 5:
            # Move exactly to target for final smoothness
            self.set_position(target[0], target[1])
            self.target_position = None
            return
        
        # Calculate desired movement
        desired_pos = move_towards(current, target, self.speed)
        
        # Check if desired position is blocked
        if self._is_position_blocked(desired_pos, obstacles):
            # Use steering to navigate around obstacle
            best_pos = self._find_best_path(current, target, obstacles)
            # Smooth the movement - use the found path
            self.set_position(best_pos[0], best_pos[1])
        else:
            # Path is clear - move smoothly
            self.set_position(desired_pos[0], desired_pos[1])
    
    def _is_position_blocked(self, pos: Tuple[float, float], obstacles) -> bool:
        """Check if a position is blocked by obstacles"""
        if not obstacles:
            return False
        
        # Check with larger buffer to detect walls even earlier
        buffer = self.size + 20  # Increased from 15 to 20
        for obs in obstacles:
            if obs.contains_circle(pos[0], pos[1], buffer):
                return True
        
        return False
    
    def _find_best_path(self, current: Tuple[float, float], target: Tuple[float, float], obstacles) -> Tuple[float, float]:
        """
        Find the best path around obstacles using steering (smooth version)
        
        Args:
            current: Current position
            target: Target position
            obstacles: List of obstacles
            
        Returns:
            Best position to move to
        """
        import math
        
        # Calculate angle to target
        angle_to_target = math.atan2(target[1] - current[1], target[0] - current[0])
        
        # First try: straight ahead (no deviation)
        test_x = current[0] + math.cos(angle_to_target) * self.speed
        test_y = current[1] + math.sin(angle_to_target) * self.speed
        test_pos = clamp_position((test_x, test_y), WINDOW_WIDTH, WINDOW_HEIGHT)
        
        if not self._is_position_blocked(test_pos, obstacles):
            return test_pos
        
        # Second: try angles in increasing steps (smoother turning)
        # Check both left and right, alternating for smooth curves
        for offset in [15, -15, 30, -30, 45, -45, 60, -60, 75, -75, 90, -90]:
            test_angle = angle_to_target + math.radians(offset)
            test_x = current[0] + math.cos(test_angle) * self.speed
            test_y = current[1] + math.sin(test_angle) * self.speed
            test_pos = clamp_position((test_x, test_y), WINDOW_WIDTH, WINDOW_HEIGHT)
            
            if not self._is_position_blocked(test_pos, obstacles):
                return test_pos
        
        # Third: try strafe movement (lateral dodge)
        for strafe_angle in [120, -120, 135, -135, 150, -150]:
            test_angle = angle_to_target + math.radians(strafe_angle)
            test_x = current[0] + math.cos(test_angle) * self.speed * 0.6
            test_y = current[1] + math.sin(test_angle) * self.speed * 0.6
            test_pos = clamp_position((test_x, test_y), WINDOW_WIDTH, WINDOW_HEIGHT)
            
            if not self._is_position_blocked(test_pos, obstacles):
                return test_pos
        
        # Fourth: try backward escape
        for back_mult in [0.6, 0.4, 0.2]:
            backward_x = current[0] - math.cos(angle_to_target) * self.speed * back_mult
            backward_y = current[1] - math.sin(angle_to_target) * self.speed * back_mult
            backward_pos = clamp_position((backward_x, backward_y), WINDOW_WIDTH, WINDOW_HEIGHT)
            
            if not self._is_position_blocked(backward_pos, obstacles):
                return backward_pos
        
        # Last resort: stay in place
        return current
    
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
        
        # Check if stuck near wall and try to escape
        if obstacles:
            self._escape_if_stuck(obstacles)
        
        # Move towards target or patrol
        if self.target_position:
            self.move(obstacles)
        else:
            self.patrol(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Restore some energy
        if self.energy < self.max_energy:
            self.restore_energy(0.5)
    
    def _escape_if_stuck(self, obstacles) -> None:
        """Detect if stuck near wall and try to escape"""
        current = self.get_position()
        
        # Track movement history
        self.last_positions.append(current)
        if len(self.last_positions) > 30:  # Increased window for more stable detection
            self.last_positions.pop(0)
        
        # Check if agent has moved significantly in last frames
        if len(self.last_positions) >= 30:
            distance_moved = distance(self.last_positions[0], current)
            if distance_moved < 8:  # Very little movement
                self.stuck_counter += 1
            else:
                self.stuck_counter = 0
        
        # Check how close to walls/obstacles
        min_dist_to_obstacle = float('inf')
        for obs in obstacles:
            # Distance from current position to obstacle
            closest_x = max(obs.x, min(current[0], obs.x + obs.width))
            closest_y = max(obs.y, min(current[1], obs.y + obs.height))
            dist = distance(current, (closest_x, closest_y))
            min_dist_to_obstacle = min(min_dist_to_obstacle, dist)
        
        # Only trigger escape if truly stuck for a longer period
        if self.stuck_counter > 10:  # Much higher threshold - only after 10 frames of being stuck
            import random
            import math
            # Generate random escape direction, away from current position
            escape_angle = random.uniform(0, 2 * 3.14159)
            escape_distance = 200
            escape_x = current[0] + math.cos(escape_angle) * escape_distance
            escape_y = current[1] + math.sin(escape_angle) * escape_distance
            
            # Clamp to map bounds
            from src.utils.helpers import clamp_position
            target_pos = clamp_position((escape_x, escape_y), WINDOW_WIDTH, WINDOW_HEIGHT)
            self.set_target(target_pos[0], target_pos[1], MOVEMENT_PATROL)
            self.stuck_counter = 0
    
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
