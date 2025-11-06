"""
Game Map and Environment Management
Handles map layout, obstacles, and spatial queries
"""
from typing import List, Tuple
import pygame
import random
from config.game_config import *
from src.utils.helpers import distance, clamp_position


class Obstacle:
    """Represents an obstacle on the map"""
    
    def __init__(self, x: float, y: float, width: float, height: float):
        """
        Initialize an obstacle
        
        Args:
            x: X coordinate
            y: Y coordinate
            width: Width of obstacle
            height: Height of obstacle
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def contains_point(self, x: float, y: float) -> bool:
        """Check if point is inside obstacle"""
        return self.rect.collidepoint(x, y)
    
    def contains_circle(self, x: float, y: float, radius: float) -> bool:
        """Check if circle overlaps with obstacle"""
        # Find closest point on rectangle to circle center
        closest_x = max(self.x, min(x, self.x + self.width))
        closest_y = max(self.y, min(y, self.y + self.height))
        
        # Distance between circle center and closest point
        dist = distance((x, y), (closest_x, closest_y))
        return dist < radius
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw obstacle on surface"""
        pygame.draw.rect(surface, COLOR_DARK_GRAY, self.rect)
        pygame.draw.rect(surface, COLOR_GRAY, self.rect, 2)


class GameMap:
    """Manages the game map and environment"""
    
    def __init__(self, width: int = WINDOW_WIDTH, height: int = WINDOW_HEIGHT):
        """
        Initialize the game map
        
        Args:
            width: Map width
            height: Map height
        """
        self.width = width
        self.height = height
        self.obstacles: List[Obstacle] = []
        self.explored_areas = set()
        
        self._generate_obstacles()
    
    def _generate_obstacles(self) -> None:
        """Generate random obstacles on the map"""
        # Create obstacles around the edges and scattered throughout
        
        # Top and bottom barriers
        self.obstacles.append(Obstacle(0, 0, self.width, 20))  # Top
        self.obstacles.append(Obstacle(0, self.height - 20, self.width, 20))  # Bottom
        
        # Left and right barriers
        self.obstacles.append(Obstacle(0, 0, 20, self.height))  # Left
        self.obstacles.append(Obstacle(self.width - 20, 0, 20, self.height))  # Right
        
        # Generate scattered obstacles
        for _ in range(OBSTACLE_COUNT):
            width = random.randint(*OBSTACLE_SIZE_RANGE)
            height = random.randint(*OBSTACLE_SIZE_RANGE)
            
            # Define safe zones where obstacles should NOT spawn
            # Base camp zone - agents spawn 150px away from base, so buffer must be >= 150px
            base_zone = (BASE_CAMP_X - 150, BASE_CAMP_Y - 150, 300, 300)
            # Hideout zone - player starts here
            hideout_zone = (HIDEOUT_X - 50, HIDEOUT_Y - 50, 100, 100)
            
            def is_in_safe_zone(x: float, y: float) -> bool:
                """Check if position overlaps with any safe zone"""
                # Check base camp zone
                if (base_zone[0] < x < base_zone[0] + base_zone[2] and
                    base_zone[1] < y < base_zone[1] + base_zone[3]):
                    return True
                # Check hideout zone
                if (hideout_zone[0] < x < hideout_zone[0] + hideout_zone[2] and
                    hideout_zone[1] < y < hideout_zone[1] + hideout_zone[3]):
                    return True
                return False
            
            while True:
                x = random.randint(50, self.width - width - 50)
                y = random.randint(50, self.height - height - 50)
                
                # Check if position is outside all safe zones
                if not is_in_safe_zone(x, y):
                    break
            
            self.obstacles.append(Obstacle(x, y, width, height))
    
    def is_blocked(self, x: float, y: float, radius: float = 5) -> bool:
        """
        Check if a position is blocked by obstacles
        
        Args:
            x: X coordinate
            y: Y coordinate
            radius: Collision radius
            
        Returns:
            True if blocked
        """
        for obstacle in self.obstacles:
            if obstacle.contains_circle(x, y, radius):
                return True
        return False
    
    def get_nearest_free_position(self, x: float, y: float, radius: float = 5,
                                   search_range: int = 50) -> Tuple[float, float]:
        """
        Get the nearest free position to the given coordinates
        
        Args:
            x: X coordinate
            y: Y coordinate
            radius: Collision radius
            search_range: Search range for free position
            
        Returns:
            Free position
        """
        if not self.is_blocked(x, y, radius):
            return (x, y)
        
        # Spiral search for free position
        for distance_offset in range(1, search_range, 5):
            for angle_step in range(0, 360, 45):
                import math
                angle = math.radians(angle_step)
                new_x = x + distance_offset * math.cos(angle)
                new_y = y + distance_offset * math.sin(angle)
                
                new_x, new_y = clamp_position((new_x, new_y), self.width, self.height)
                
                if not self.is_blocked(new_x, new_y, radius):
                    return (new_x, new_y)
        
        return clamp_position((x, y), self.width, self.height)
    
    def mark_explored(self, x: float, y: float, radius: float = 50) -> None:
        """
        Mark an area as explored
        
        Args:
            x: X coordinate of exploration
            y: Y coordinate of exploration
            radius: Exploration radius
        """
        # Add cells within radius to explored set
        step = 10
        for dx in range(-int(radius), int(radius) + 1, step):
            for dy in range(-int(radius), int(radius) + 1, step):
                self.explored_areas.add((int(x + dx), int(y + dy)))
    
    def is_explored(self, x: float, y: float) -> bool:
        """
        Check if an area has been explored
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if explored
        """
        return (int(x), int(y)) in self.explored_areas
    
    def get_obstacles(self) -> List[Obstacle]:
        """Get all obstacles"""
        return self.obstacles
    
    def draw(self, surface: pygame.Surface, show_explored: bool = False) -> None:
        """
        Draw the map on a surface
        
        Args:
            surface: Pygame surface to draw on
            show_explored: Whether to show explored areas
        """
        # Draw explored areas (debug)
        if show_explored and DEBUG_MODE:
            for x, y in self.explored_areas:
                pygame.draw.circle(surface, (100, 100, 100), (x, y), 3)
        
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(surface)
    
    def reset(self) -> None:
        """Reset the map"""
        self.obstacles.clear()
        self.explored_areas.clear()
        self._generate_obstacles()
