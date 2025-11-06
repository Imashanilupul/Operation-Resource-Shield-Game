# File Structure & Architecture

## Directory Tree

```
Operation-Resource-Shield-Game/
│
├── 📄 main.py                           [ENTRY POINT]
│   └─ Starts the game
│
├── 📄 requirements.txt
│   └─ pip install pygame numpy
│
├── 📄 README.md
│   └─ Full documentation
│
├── 📄 QUICKSTART.md
│   └─ Quick start guide
│
├── 📁 config/
│   ├── __init__.py
│   └── 📄 game_config.py
│       └─ ALL game constants and settings
│
├── 📁 src/
│   │
│   ├── 📄 game_engine.py                [GAME LOOP]
│   │   └─ Main game orchestration
│   │
│   ├── 📄 player.py
│   │   └─ Player (Thief) character
│   │
│   ├── 📁 agents/
│   │   ├── __init__.py
│   │   ├── 📄 base_agent.py
│   │   │   └─ Abstract base class for all agents
│   │   ├── 📄 explorer.py
│   │   │   └─ Explorer agent implementation
│   │   ├── 📄 collector.py
│   │   │   └─ Collector agent implementation
│   │   ├── 📄 attacker.py
│   │   │   └─ Attacker agent implementation
│   │   └── 📄 strategist.py
│   │       └─ Strategist agent implementation
│   │
│   ├── 📁 environment/
│   │   ├── __init__.py
│   │   ├── 📄 map.py
│   │   │   └─ GameMap, Obstacle classes
│   │   ├── 📄 resource.py
│   │   │   └─ Resource, ResourceManager classes
│   │   └── 📄 base_camp.py
│   │       └─ BaseCamp, ThiefHideout classes
│   │
│   ├── 📁 communication/
│   │   ├── __init__.py
│   │   └── 📄 blackboard.py
│   │       └─ Blackboard, Message classes (agent communication)
│   │
│   ├── 📁 ui/
│   │   ├── __init__.py
│   │   └── 📄 ui_manager.py
│   │       └─ UIManager class (rendering and UI)
│   │
│   └── 📁 utils/
│       ├── __init__.py
│       └── 📄 helpers.py
│           └─ Utility functions (math, collision, etc.)
│
└── 📁 assets/
    └─ (for future: images, sounds, etc.)
```

---

## File-by-File Overview

### Core Entry Points

#### `main.py`
```python
# Start here!
from src.game_engine import GameEngine
game = GameEngine()
game.run()
```
- **Purpose**: Game entry point
- **Lines**: ~20
- **Dependencies**: GameEngine

---

### Configuration

#### `config/game_config.py`
```python
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
AGENT_SPEED = 3.5
PLAYER_CARRYING_CAPACITY = 3
```
- **Purpose**: All game constants and settings
- **Lines**: ~150
- **Contents**: Colors, sizes, speeds, difficulty settings, debug flags

---

### Game Engine

#### `src/game_engine.py`
```python
class GameEngine:
    def run(self):           # Main game loop
    def update(self):        # Update all entities
    def draw(self):          # Render everything
    def _check_win_conditions(self):
    def _check_player_interactions(self):
```
- **Purpose**: Central orchestration of all game systems
- **Lines**: ~350
- **Key Methods**: 
  - `run()`: Main loop
  - `_spawn_agents()`: Create AI agents
  - `_check_win_conditions()`: Game end logic
  - `update()`: Update entities
  - `draw()`: Render to screen

---

### Player Character

#### `src/player.py`
```python
class Player:
    def handle_input(self, keys):      # Keyboard controls
    def steal_resources(self, count):  # Steal from base
    def secure_resources(self, hideout):  # Secure at hideout
    def activate_stealth(self):        # Go invisible
    def update(self, obstacles):       # Update position/state
    def draw(self, surface):           # Render player
```
- **Purpose**: Player (thief) character
- **Lines**: ~200
- **Features**: Movement, stealth, inventory, collision detection

---

### Agent System

#### `src/agents/base_agent.py`
```python
class BaseAgent(ABC):
    def move(self, obstacles):         # Move towards target
    def think(self):                   # Abstract decision-making
    def send_message(self, ...):       # Send via blackboard
    def can_see(self, x, y):           # Vision check
    def update(self, obstacles):       # Update state
    def draw(self, surface):           # Render agent
```
- **Purpose**: Base class for all agents
- **Lines**: ~300
- **Key Features**: 
  - Movement and pathfinding
  - Communication methods
  - Vision system
  - Energy management

#### `src/agents/explorer.py`
```python
class ExplorerAgent(BaseAgent):
    def think(self):
    def report_resource(self, x, y):
    def report_thief_sighting(self, x, y):
```
- **Purpose**: Scout agent
- **Lines**: ~150
- **Behavior**: Explores map, detects thief, finds resources

#### `src/agents/collector.py`
```python
class CollectorAgent(BaseAgent):
    def think(self):
    def _collect_resource(self):
    def _deliver_resources(self):
```
- **Purpose**: Resource gathering agent
- **Lines**: ~150
- **Behavior**: Collects resources, brings to base

#### `src/agents/attacker.py`
```python
class AttackerAgent(BaseAgent):
    def think(self):
    def _pursue_thief(self):
    def check_thief_collision(self, ...):
```
- **Purpose**: Thief pursuit agent
- **Lines**: ~130
- **Behavior**: Hunts thief, captures on contact

#### `src/agents/strategist.py`
```python
class StrategistAgent(BaseAgent):
    def think(self):
    def _make_strategic_decisions(self):
    def _command_intercept(self, ...):
```
- **Purpose**: Team coordinator
- **Lines**: ~170
- **Behavior**: Processes info, makes decisions, issues commands

---

### Environment

#### `src/environment/map.py`
```python
class Obstacle:
    def contains_circle(self, x, y, radius):

class GameMap:
    def is_blocked(self, x, y, radius):
    def get_nearest_free_position(self, ...):
    def get_obstacles(self):
```
- **Purpose**: Map terrain and collision
- **Lines**: ~200
- **Features**: Obstacle generation, collision detection, pathfinding

#### `src/environment/resource.py`
```python
class Resource:
    def get_position(self):

class ResourceManager:
    def spawn_resource(self, ...):
    def collect_resource(self, resource):
    def get_nearest_resource(self, x, y):
```
- **Purpose**: Resource spawning and management
- **Lines**: ~200
- **Features**: Resource generation, collection tracking

#### `src/environment/base_camp.py`
```python
class BaseCamp:
    def add_resources(self, count):
    def remove_resources(self, count):

class ThiefHideout:
    def secure_resources(self, count):
```
- **Purpose**: Base camp and hideout mechanics
- **Lines**: ~200
- **Features**: Resource storage, breach detection

---

### Communication System

#### `src/communication/blackboard.py`
```python
class Message:
    # sender, recipient, message_type, content, priority

class Blackboard:
    def post_data(self, key, value):
    def read_data(self, key):
    def send_message(self, message):
    def get_messages(self, recipient):
    def broadcast_message(self, ...):
```
- **Purpose**: Multi-agent communication
- **Lines**: ~350
- **Features**: 
  - Shared memory (blackboard)
  - Message passing
  - Alert system
  - Thread-safe operations

---

### User Interface

#### `src/ui/ui_manager.py`
```python
class UIManager:
    def draw_hud(self, surface, game_state):
    def draw_game_over_screen(self, ...):
    def draw_debug_info(self, ...):
    def draw_objective_panel(self, ...):
    def draw_legend(self, ...):
    def draw_message_log(self, ...):
```
- **Purpose**: Game rendering and UI
- **Lines**: ~400
- **Features**: HUD, overlays, debug display, game over screen

---

### Utilities

#### `src/utils/helpers.py`
```python
def distance(pos1, pos2):
def direction(from_pos, to_pos):
def move_towards(from_pos, to_pos, speed):
def is_in_range(pos1, pos2, range_val):
def circle_overlap(pos1, radius1, pos2, radius2):
def line_of_sight(from_pos, to_pos, obstacles, sight_range):
def clamp_position(pos, width, height):
```
- **Purpose**: Mathematical and utility functions
- **Lines**: ~300
- **Features**: Math operations, collision detection, geometry

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      GAME ENGINE                             │
│                   (game_engine.py)                           │
└─────────────────────────────────────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
    ┌───────▼────────┐  ┌────▼──────────┐  ┌──▼──────────────┐
    │   PLAYER       │  │   AGENTS      │  │  ENVIRONMENT   │
    │  (player.py)   │  │ (agents/*.py) │  │(environment/*) │
    └───────┬────────┘  └────┬──────────┘  └──┬──────────────┘
            │                 │                │
            │                 │                │
            └────────┬────────┴────────────────┘
                     │
            ┌────────▼────────────────┐
            │   BLACKBOARD SYSTEM     │
            │ (communication/*.py)    │
            │                         │
            │ - Shared Knowledge      │
            │ - Message Passing       │
            │ - Team Coordination     │
            └────────┬────────────────┘
                     │
            ┌────────▼────────────────┐
            │   UI RENDERING          │
            │   (ui/*.py)             │
            └─────────────────────────┘
```

---

## Class Relationships

```
BaseAgent (Abstract)
    ├── ExplorerAgent
    ├── CollectorAgent
    ├── AttackerAgent
    └── StrategistAgent

Blackboard
    ├── messages: List[Message]
    ├── data: Dict
    └── alerts: List

GameMap
    └── obstacles: List[Obstacle]

ResourceManager
    └── resources: List[Resource]

GameEngine
    ├── player: Player
    ├── agents: List[BaseAgent]
    ├── map: GameMap
    ├── resource_manager: ResourceManager
    ├── base_camp: BaseCamp
    ├── hideout: ThiefHideout
    └── ui_manager: UIManager
```

---

## Execution Flow

### Startup
```
main.py
  → GameEngine.__init__()
    → Initialize all systems
    → Spawn agents
    → Setup blackboard
  → GameEngine.run()
```

### Game Loop (60 FPS)
```
Each Frame:
  1. Handle Events (keyboard, mouse, close)
  2. Update (player, agents, resources, collisions)
  3. Check Win Conditions
  4. Update Blackboard
  5. Render (draw all entities)
  6. Control Frame Rate
```

### Update Phase
```
GameEngine.update()
  1. Update Player
     - Handle input
     - Update position
     - Check stealth
  2. Update Resources
     - Spawn new
     - Manage state
  3. Update Agents
     - Update position
     - Make decisions
     - Send messages
  4. Check Interactions
     - Player-base collisions
     - Agent-player collisions
     - Resource pickups
  5. Check Win Conditions
     - Resources depleted
     - Thief caught
     - Time limit
```

### Agent AI Cycle
```
Agent.update() → Agent.think()
  1. Read blackboard
  2. Process messages
  3. Evaluate current state
  4. Make decisions
  5. Send commands/alerts
  6. Update movement target
```

---

## Key Design Patterns

### 1. **Blackboard Pattern**
- Centralized communication
- Agents read/write to shared memory
- Decouples agent implementations

### 2. **Observer Pattern**
- Agents "observe" blackboard for updates
- Message system for notifications

### 3. **State Machine**
- Agents have movement states (patrol, pursue, etc.)
- Player has states (normal, stealth, carrying, etc.)

### 4. **Factory Pattern**
- `GameEngine._spawn_agents()` creates agent instances
- Scalable agent creation

### 5. **Singleton Pattern**
- Blackboard has single global instance
- Ensures consistency across all agents

---

## Dependencies Between Modules

```
main.py
  └─ GameEngine (game_engine.py)
     ├─ Player (player.py)
     ├─ Agents (agents/*.py)
     │  └─ BaseAgent (agents/base_agent.py)
     │     └─ Blackboard (communication/blackboard.py)
     ├─ Environment
     │  ├─ GameMap (environment/map.py)
     │  ├─ ResourceManager (environment/resource.py)
     │  └─ BaseCamp (environment/base_camp.py)
     ├─ Blackboard (communication/blackboard.py)
     └─ UIManager (ui/ui_manager.py)

All use: helpers.py (utils/helpers.py)
All use: game_config.py (config/game_config.py)
```

---

## Adding New Features

### To Add New Agent Type:
1. Create `src/agents/new_agent.py`
2. Inherit from `BaseAgent`
3. Implement `think()` method
4. Register in `GameEngine._spawn_agents()`

### To Add New Mechanic:
1. Modify relevant environment file
2. Update `GameEngine.update()`
3. Add UI in `UIManager`
4. Configure in `game_config.py`

### To Add New UI Element:
1. Add method to `UIManager`
2. Call from `GameEngine.draw()`

---

## Performance Considerations

- **Agents**: ~5-10 agents updates per frame
- **Pathfinding**: Simple target-based (O(1))
- **Collision**: O(n) with obstacles
- **Communication**: O(1) blackboard access
- **Rendering**: Scaled with entity count

Total typical: 30-60 FPS on modern hardware
