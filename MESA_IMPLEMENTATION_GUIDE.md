# Mesa Framework Integration - Implementation Guide

## Quick Start

### 1. Install Mesa
```bash
pip install mesa
```

### 2. Update requirements.txt
```
pygame==2.5.2
numpy==1.24.3
mesa>=0.9.0
```

### 3. Current Architecture Overview

```
Your Game
├── GameEngine (manual scheduler)
├── BaseAgent (custom base class)
├── Specialized Agents (Explorer, Collector, Attacker, Strategist)
├── Communication (Blackboard)
├── Environment (Map, Resources, BaseCamp)
└── Rendering (Pygame UI)
```

### 4. Mesa Architecture Overview

```
Mesa Model
├── Model (game container + scheduler)
├── Agent (base class for all agents)
├── Scheduler (manages agent execution order)
├── DataCollector (optional - gather statistics)
└── Agents (Explorer, Collector, Attacker, Strategist)
```

## Phase 1: Setup & Initial Integration (Recommended Start)

### Step 1.1: Update requirements.txt

```python
# requirements.txt
pygame==2.5.2
numpy==1.24.3
mesa>=0.9.0
```

### Step 1.2: Create Mesa Model Wrapper

Create new file: `src/mesa_model.py`

```python
"""
Mesa Framework Model for Operation Guardian Game
Wraps game engine with Mesa's model and scheduler
"""
from mesa import Model
from mesa.time import RandomActivationScheduler
from typing import List, Dict
from config.game_config import *
from src.game_engine import GameEngine


class OperationGuardianModel(Model):
    """Mesa Model wrapper for the game"""
    
    def __init__(self, difficulty: str = "easy"):
        """
        Initialize the Mesa model
        
        Args:
            difficulty: Game difficulty level
        """
        super().__init__()
        
        # Create scheduler
        self.scheduler = RandomActivationScheduler(self)
        
        # Delegate to existing game engine
        self.engine = GameEngine()
        self.engine.current_difficulty = difficulty
        
        # Store difficulty
        self.difficulty = difficulty
        
        # Initialize game when ready
        self.is_initialized = False
    
    def initialize_game(self) -> None:
        """Initialize game with Mesa scheduler"""
        if self.is_initialized:
            return
        
        # Setup game
        self.engine._initialize_game()
        
        # Register agents with Mesa scheduler
        for agent in self.engine.agents:
            self.scheduler.add(agent)
        
        self.is_initialized = True
    
    def step(self) -> None:
        """Execute one step of the model"""
        if not self.is_initialized:
            return
        
        # Mesa scheduler calls step() on all agents in order
        self.scheduler.step()
        
        # Update game state (collision detection, win conditions, etc.)
        self.engine._update_game_state()
    
    def get_game_state(self) -> Dict:
        """Get current game state"""
        return {
            "elapsed_time": self.engine.elapsed_time,
            "frame_count": self.engine.frame_count,
            "game_state": self.engine.game_state,
            "player_resources": self.engine.player.resources_collected,
            "base_resources": self.engine.base_camp.get_resources(),
            "agent_count": len(self.engine.agents),
        }


def create_game_model(difficulty: str = "easy") -> OperationGuardianModel:
    """Factory function to create a new game model"""
    model = OperationGuardianModel(difficulty)
    model.initialize_game()
    return model
```

### Step 1.3: Verify Installation

```bash
python -c "import mesa; print(mesa.__version__)"
```

Expected output: `0.9.0` or later

### Step 1.4: Test Mesa Integration

Create test file: `tests/test_mesa_integration.py`

```python
"""Test Mesa integration"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.mesa_model import create_game_model


def test_model_creation():
    """Test creating a Mesa model"""
    model = create_game_model("easy")
    assert model is not None
    assert model.is_initialized
    print("✓ Model creation successful")


def test_scheduler():
    """Test scheduler has agents"""
    model = create_game_model("medium")
    assert len(model.scheduler.agents) > 0
    print(f"✓ Scheduler has {len(model.scheduler.agents)} agents")


def test_step():
    """Test model stepping"""
    model = create_game_model("hard")
    initial_state = model.get_game_state()
    
    model.step()
    
    new_state = model.get_game_state()
    assert new_state["frame_count"] > initial_state["frame_count"]
    print("✓ Model stepping works")


if __name__ == "__main__":
    test_model_creation()
    test_scheduler()
    test_step()
    print("\n✅ All Mesa integration tests passed!")
```

Run with: `python tests/test_mesa_integration.py`

## Phase 2: Migrate Base Agent to Mesa

### Step 2.1: Create Mesa Agent Base Class

Create new file: `src/agents/mesa_base_agent.py`

```python
"""
Mesa-compatible base agent
Extends Mesa's Agent class while maintaining backward compatibility
"""
from mesa import Agent
from abc import abstractmethod
import pygame
from typing import Tuple
from config.game_config import *
from src.utils.helpers import distance, move_towards, clamp_position


class MesaBaseAgent(Agent):
    """
    Base class for all Mesa agents
    Wraps existing agent functionality within Mesa framework
    """
    
    def __init__(self, agent_id: str, role: str, x: float, y: float, model):
        """
        Initialize Mesa agent
        
        Args:
            agent_id: Unique identifier
            role: Agent role (explorer, collector, etc.)
            x: Starting X position
            y: Starting Y position
            model: Reference to Mesa model
        """
        super().__init__(model)  # Initialize Mesa Agent
        
        # Agent identity
        self.id = agent_id
        self.role = role
        
        # Position and movement
        self.x = x
        self.y = y
        self.speed = AGENT_SPEED
        self.size = AGENT_SIZE
        self.active = True
        
        # Target and movement
        self.target_position = None
        self.movement_type = None
        
        # Capabilities
        self.vision_range = AGENT_VISION_RANGE
        self.communication_range = AGENT_COMMUNICATION_RANGE
        self.energy = self.max_energy = AGENT_MAX_ENERGY
        
        # State
        self.carrying = []
        self.last_positions = []
        self.stuck_counter = 0
        
        # Communication (using Mesa model's blackboard)
        self.blackboard = model.scheduler.model.engine.blackboard
    
    def step(self) -> None:
        """Mesa step method - called each tick by scheduler"""
        if not self.active:
            return
        
        # Call agent's decision-making logic
        self.think()
        
        # Update movement
        if self.target_position:
            self.move()
        else:
            self.patrol(WINDOW_WIDTH, WINDOW_HEIGHT)
    
    def get_position(self) -> Tuple[float, float]:
        """Get agent's position"""
        return (self.x, self.y)
    
    def set_position(self, x: float, y: float) -> None:
        """Set agent's position"""
        self.x = x
        self.y = y
    
    def set_target(self, x: float, y: float, movement_type: str) -> None:
        """Set movement target"""
        self.target_position = (x, y)
        self.movement_type = movement_type
    
    def move(self, obstacles=None) -> None:
        """Move towards target"""
        if not self.target_position:
            return
        
        current = self.get_position()
        target = self.target_position
        dist_to_target = distance(current, target)
        
        if dist_to_target < self.speed + 5:
            self.set_position(target[0], target[1])
            self.target_position = None
            return
        
        desired_pos = move_towards(current, target, self.speed)
        
        if self._is_position_blocked(desired_pos, obstacles):
            best_pos = self._find_best_path(current, target, obstacles)
            self.set_position(best_pos[0], best_pos[1])
        else:
            self.set_position(desired_pos[0], desired_pos[1])
    
    def patrol(self, width: float, height: float) -> None:
        """Patrol in random direction"""
        import random
        import math
        
        if not self.target_position or \
           distance(self.get_position(), self.target_position) < self.speed:
            angle = random.uniform(0, 2 * math.pi)
            distance_to_target = 100
            
            patrol_x = self.x + distance_to_target * math.cos(angle)
            patrol_y = self.y + distance_to_target * math.sin(angle)
            
            self.set_target(
                clamp_position((patrol_x, patrol_y), width, height)[0],
                clamp_position((patrol_x, patrol_y), width, height)[1],
                MOVEMENT_PATROL
            )
        
        self.move()
    
    @abstractmethod
    def think(self) -> None:
        """Agent decision-making logic - implemented by subclasses"""
        pass
    
    def _is_position_blocked(self, pos: Tuple[float, float], obstacles) -> bool:
        """Check if position is blocked"""
        if not obstacles:
            return False
        
        from src.utils.helpers import distance
        for obs in obstacles:
            closest_x = max(obs.x, min(pos[0], obs.x + obs.width))
            closest_y = max(obs.y, min(pos[1], obs.y + obs.height))
            dist = distance(pos, (closest_x, closest_y))
            
            if dist < self.size + 20:
                return True
        
        return False
    
    def _find_best_path(self, current: Tuple[float, float], 
                        target: Tuple[float, float], obstacles) -> Tuple[float, float]:
        """Find best path around obstacles"""
        import math
        
        angles = [0, 15, -15, 30, -30, 45, -45, 60, -60, 75, -75, 90, -90]
        
        for angle in angles:
            rad = math.radians(angle)
            check_x = current[0] + self.speed * math.cos(rad)
            check_y = current[1] + self.speed * math.sin(rad)
            
            if not self._is_position_blocked((check_x, check_y), obstacles):
                return (check_x, check_y)
        
        return current
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw agent (to be implemented by subclasses)"""
        color_map = {
            AGENT_ROLE_EXPLORER: EXPLORER_COLOR,
            AGENT_ROLE_COLLECTOR: COLLECTOR_COLOR,
            AGENT_ROLE_ATTACKER: ATTACKER_COLOR,
            AGENT_ROLE_STRATEGIST: STRATEGIST_COLOR,
        }
        
        color = color_map.get(self.role, (255, 255, 255))
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)
```

## Phase 3: Update Game Engine to Work with Mesa

### Step 3.1: Modify GameEngine

Update `src/game_engine.py` to maintain compatibility:

```python
# In game_engine.py, add methods that Mesa model will call:

def _update_game_state(self) -> None:
    """Update game state without rendering"""
    # Check collisions
    self._check_collisions()
    
    # Check win conditions
    self._check_win_condition()
    
    # Update resources
    self.resource_manager.update()
    
    # Increment time
    self.elapsed_time += FRAME_DURATION_MS
    self.frame_count += 1

def get_current_state(self) -> Dict:
    """Get current game state for display"""
    return {
        "game_state": self.game_state,
        "elapsed_time": self.elapsed_time,
        "frame_count": self.frame_count,
        "player_resources": self.player.resources_collected,
        "base_resources": self.base_camp.get_resources(),
        "agents_remaining": len([a for a in self.agents if a.active]),
    }
```

## Next: Which Phase to Start?

**Recommendation**: Start with Phase 1 (non-breaking setup)

### Benefits of Phase 1:
- ✅ No changes to existing code
- ✅ Mesa installed and working
- ✅ Foundation for future phases
- ✅ Can test Mesa alongside current system
- ✅ Easy rollback if issues

### To Start Phase 1:
1. Update `requirements.txt`
2. Install Mesa: `pip install mesa`
3. Create `src/mesa_model.py`
4. Run verification test

Would you like me to proceed with Phase 1?
