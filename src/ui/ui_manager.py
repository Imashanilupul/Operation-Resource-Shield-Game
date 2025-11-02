"""
UI/Display Manager
Handles game rendering and UI elements
"""
import pygame
from typing import Tuple
from config.game_config import *
from src.utils.helpers import format_time


class UIManager:
    """Manages game UI and rendering"""
    
    def __init__(self, width: int = WINDOW_WIDTH, height: int = WINDOW_HEIGHT):
        """
        Initialize UI manager
        
        Args:
            width: Screen width
            height: Screen height
        """
        self.width = width
        self.height = height
        self.font_large = pygame.font.Font(None, FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL)
    
    def draw_hud(self, surface: pygame.Surface, game_state: dict) -> None:
        """
        Draw the heads-up display
        
        Args:
            surface: Pygame surface to draw on
            game_state: Current game state dictionary
        """
        # Draw background for HUD
        hud_height = 80
        pygame.draw.rect(surface, (0, 0, 0, 180), (0, 0, self.width, hud_height))
        pygame.draw.line(surface, COLOR_GRAY, (0, hud_height), (self.width, hud_height), 2)
        
        # Prepare text
        elapsed_time = game_state.get("elapsed_time", 0)
        resources_at_base = game_state.get("resources_at_base", 0)
        player_carrying = game_state.get("player_carrying", 0)
        game_status = game_state.get("status", "RUNNING")
        
        # Draw HUD information
        y_offset = UI_PADDING
        
        # Timer
        time_text = self.font_medium.render(f"Time: {format_time(elapsed_time)}", True, COLOR_WHITE)
        surface.blit(time_text, (UI_PADDING, y_offset))
        
        # Resources at base
        resources_text = self.font_medium.render(f"Base Resources: {resources_at_base}", True, COLOR_GREEN)
        surface.blit(resources_text, (self.width // 3, y_offset))
        
        # Player resources
        player_text = self.font_medium.render(f"Player Carrying: {player_carrying}/{PLAYER_CARRYING_CAPACITY}", True, COLOR_CYAN)
        surface.blit(player_text, (2 * self.width // 3 - 50, y_offset))
        
        # Game status
        status_color = COLOR_GREEN if game_status == "RUNNING" else COLOR_RED
        status_text = self.font_small.render(game_status, True, status_color)
        surface.blit(status_text, (self.width - UI_PADDING - 150, y_offset + 5))
        
        # FPS display
        if SHOW_FPS:
            fps_text = self.font_small.render(f"FPS: {game_state.get('fps', 0):.1f}", True, COLOR_YELLOW)
            surface.blit(fps_text, (self.width - 100, UI_PADDING))
    
    def draw_game_over_screen(self, surface: pygame.Surface, winner: str, stats: dict) -> None:
        """
        Draw game over screen
        
        Args:
            surface: Pygame surface to draw on
            winner: Winner ('thief' or 'agents')
            stats: Game statistics
        """
        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # Draw title
        if winner == "thief":
            title_text = self.font_large.render("THIEF WINS!", True, COLOR_CYAN)
            title_color = COLOR_CYAN
        else:
            title_text = self.font_large.render("AGENTS WIN!", True, COLOR_GREEN)
            title_color = COLOR_GREEN
        
        title_rect = title_text.get_rect(center=(self.width // 2, self.height // 2 - 100))
        surface.blit(title_text, title_rect)
        
        # Draw statistics
        y = self.height // 2 - 20
        stat_lines = [
            f"Time: {format_time(stats.get('elapsed_time', 0))}",
            f"Resources Stolen: {stats.get('resources_stolen', 0)}",
            f"Resources Secured: {stats.get('resources_secured', 0)}",
            f"Agent Actions: {stats.get('agent_actions', 0)}",
        ]
        
        for line in stat_lines:
            stat_text = self.font_medium.render(line, True, COLOR_WHITE)
            stat_rect = stat_text.get_rect(center=(self.width // 2, y))
            surface.blit(stat_text, stat_rect)
            y += 40
        
        # Draw restart instruction
        restart_text = self.font_small.render("Press SPACE to return to menu", True, COLOR_YELLOW)
        restart_rect = restart_text.get_rect(center=(self.width // 2, self.height - 50))
        surface.blit(restart_text, restart_rect)
    
    def draw_debug_info(self, surface: pygame.Surface, debug_info: dict) -> None:
        """
        Draw debug information
        
        Args:
            surface: Pygame surface to draw on
            debug_info: Debug information dictionary
        """
        if not DEBUG_MODE:
            return
        
        y = self.height - 100
        x = 10
        
        for key, value in debug_info.items():
            text = self.font_small.render(f"{key}: {value}", True, COLOR_WHITE)
            surface.blit(text, (x, y))
            y += 20
    
    def draw_objective_panel(self, surface: pygame.Surface, role: str) -> None:
        """
        Draw objective panel
        
        Args:
            surface: Pygame surface to draw on
            role: Player role ('thief')
        """
        panel_width = 250
        panel_height = 100
        panel_x = self.width - panel_width - 10
        panel_y = 100
        
        # Draw panel background
        pygame.draw.rect(surface, (20, 20, 20), (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(surface, COLOR_CYAN, (panel_x, panel_y, panel_width, panel_height), 2)
        
        # Title
        title = self.font_medium.render("OBJECTIVES", True, COLOR_CYAN)
        surface.blit(title, (panel_x + 10, panel_y + 5))
        
        # Objectives based on role
        objectives = [
            "• Steal resources from base",
            "• Avoid getting caught",
            "• Secure loot at hideout",
        ]
        
        y = panel_y + 30
        for obj in objectives:
            text = self.font_small.render(obj, True, COLOR_WHITE)
            surface.blit(text, (panel_x + 10, y))
            y += 20
    
    def draw_legend(self, surface: pygame.Surface) -> None:
        """
        Draw map legend
        
        Args:
            surface: Pygame surface to draw on
        """
        legend_items = [
            (COLOR_GREEN_DARK, "Base Camp"),
            (COLOR_CYAN, "Player (Thief)"),
            (COLOR_BLUE, "Explorer"),
            (COLOR_GREEN, "Collector"),
            (COLOR_RED, "Attacker"),
            (COLOR_MAGENTA, "Strategist"),
            (COLOR_YELLOW, "Resource"),
        ]
        
        panel_x = 10
        panel_y = 100
        max_width = 180
        
        # Draw legend background
        legend_height = len(legend_items) * 20 + 20
        pygame.draw.rect(surface, (20, 20, 20), (panel_x, panel_y, max_width, legend_height))
        pygame.draw.rect(surface, COLOR_GRAY, (panel_x, panel_y, max_width, legend_height), 1)
        
        # Draw legend title
        title = self.font_small.render("LEGEND", True, COLOR_WHITE)
        surface.blit(title, (panel_x + 10, panel_y + 5))
        
        # Draw legend items
        y = panel_y + 25
        for color, label in legend_items:
            pygame.draw.circle(surface, color, (panel_x + 15, y), 4)
            text = self.font_small.render(label, True, COLOR_WHITE)
            surface.blit(text, (panel_x + 30, y - 8))
            y += 20
    
    def draw_agent_vision_ranges(self, surface: pygame.Surface, agents: list) -> None:
        """
        Draw agent vision ranges as circles (except strategist)
        
        Args:
            surface: Pygame surface to draw on
            agents: List of agents
        """
        if not SHOW_AGENT_VISION:
            return
        
        # Create a temporary surface for semi-transparent circles
        vision_surface = pygame.Surface((self.width, self.height))
        vision_surface.set_colorkey((0, 0, 0))
        vision_surface.fill((0, 0, 0))
        
        for agent in agents:
            # Skip strategist - don't show their vision range
            if agent.role == AGENT_ROLE_STRATEGIST:
                continue
            
            # Get agent color based on role
            if agent.role == AGENT_ROLE_EXPLORER:
                color = (0, 150, 255, 100)  # Cyan
            elif agent.role == AGENT_ROLE_COLLECTOR:
                color = (255, 165, 0, 100)  # Orange
            elif agent.role == AGENT_ROLE_ATTACKER:
                color = (255, 0, 0, 100)  # Red
            else:
                color = (128, 128, 128, 100)  # Gray
            
            # Draw vision range circle
            pygame.draw.circle(vision_surface, color[:3], (int(agent.x), int(agent.y)), 
                             agent.vision_range, 1)
            
            # Draw semi-transparent filled circle
            pygame.draw.circle(vision_surface, color[:3], (int(agent.x), int(agent.y)), 
                             agent.vision_range // 2, 0)
        
        # Set alpha and blend
        vision_surface.set_alpha(50)
        surface.blit(vision_surface, (0, 0))
    
    def draw_message_log(self, surface: pygame.Surface, messages: list, max_messages: int = 8) -> None:
        """
        Draw recent messages log
        
        Args:
            surface: Pygame surface to draw on
            messages: List of message strings
            max_messages: Maximum messages to display
        """
        if not messages:
            return
        
        panel_x = 10
        panel_y = self.height - 200
        panel_width = 400
        panel_height = 190
        
        # Draw panel background
        pygame.draw.rect(surface, (10, 10, 20), (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(surface, (100, 150, 255), (panel_x, panel_y, panel_width, panel_height), 2)
        
        # Title
        title = self.font_small.render("📡 COMMUNICATIONS LOG", True, (100, 200, 255))
        surface.blit(title, (panel_x + 10, panel_y + 5))
        
        # Messages
        y = panel_y + 25
        for message in messages[-max_messages:]:
            # Truncate if too long
            if len(message) > 50:
                message = message[:47] + "..."
            
            text = self.font_small.render(message, True, COLOR_WHITE)
            surface.blit(text, (panel_x + 10, y))
            y += 20
