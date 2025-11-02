# Operation Guardian: Multi-Agent Defense System

**A Multi-Agent System Simulation Game** where AI agents work together to protect resources while the player (as a thief) tries to steal them.

## 🎯 Game Overview

This is an interactive strategy game built with **Pygame** that demonstrates multi-agent cooperation, communication, and coordinated decision-making. The player takes the role of a **thief** trying to steal resources from a heavily defended base, while **AI agents** collaborate using a blackboard communication system to catch the thief and protect their resources.

### Core Concept
- **Player**: Thief trying to steal resources and escape
- **AI Agents**: Team of 5 specialized agents working together
  - Explorer: Scouts for resources and threats
  - Collectors (2): Gather resources for the base
  - Attacker: Pursues and captures the thief
  - Strategist: Coordinates team strategy

---

## 🏗️ Project Structure

```
Operation-Resource-Shield-Game/
│
├── main.py                          # Entry point - run this to start the game
├── requirements.txt                 # Python dependencies
│
├── config/
│   ├── __init__.py
│   └── game_config.py              # All game constants and settings
│
├── src/
│   ├── __init__.py
│   │
│   ├── game_engine.py              # Main game loop and orchestration
│   ├── player.py                   # Player (Thief) character
│   │
│   ├── agents/                     # AI Agent implementations
│   │   ├── __init__.py
│   │   ├── base_agent.py          # Base class for all agents
│   │   ├── explorer.py            # Explorer agent
│   │   ├── collector.py           # Collector agent
│   │   ├── attacker.py            # Attacker agent
│   │   └── strategist.py          # Strategist agent
│   │
│   ├── environment/                # Game world components
│   │   ├── __init__.py
│   │   ├── map.py                 # Map, obstacles, terrain
│   │   ├── resource.py            # Resource spawning and management
│   │   └── base_camp.py           # Base camp and hideout
│   │
│   ├── communication/              # Multi-agent communication system
│   │   ├── __init__.py
│   │   └── blackboard.py          # Shared blackboard communication
│   │
│   ├── ui/                         # User interface and rendering
│   │   ├── __init__.py
│   │   └── ui_manager.py          # UI rendering and displays
│   │
│   └── utils/                      # Utility functions
│       ├── __init__.py
│       └── helpers.py             # Math, collision, pathfinding helpers
│
└── assets/                         # Game assets (for future use)
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Pygame 2.5.2

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/Imashanilupul/Operation-Resource-Shield-Game.git
cd Operation-Resource-Shield-Game
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the game**:
```bash
python main.py
```

---

## 🎮 How to Play

### Controls
- **W/A/S/D** or **Arrow Keys**: Move the thief
- **SPACE**: Activate stealth (3-second invisibility, 5-second cooldown)
- **ESC**: Quit game
- **P**: Pause/Resume

### Objectives (As Thief)

✅ **Primary Goal**: Steal all resources from the base camp or secure enough stolen resources at your hideout

🎯 **Secondary Goals**:
- Avoid getting caught by the Attacker agent
- Use stealth to hide from Explorer agents
- Return stolen resources to your hideout to secure them

### Game Mechanics

#### Resources
- Base starts with 20 resources
- Collectors bring in new resources every few seconds
- You can carry up to 3 resources at a time
- Steal from the base, then deliver to your hideout to secure them

#### Base Camp
- Located at center of map (green circle)
- Contains stored resources
- Heavily monitored by agents

#### Your Hideout
- Located at top-left corner (red circle)
- Deliver stolen resources here to "win"
- Safe from agents

#### Stealth System
- Press SPACE to become invisible for 3 seconds
- Agents cannot see you while in stealth
- 5-second cooldown between uses
- Strategic use is key!

---

## 🤖 AI Agent System

### 1. Explorer Agent (Blue)
**Role**: Scout and detect threats

- Explores different map zones
- Detects resources and marks them
- Alerts team when thief is spotted
- Uses vision range of 150 pixels
- Reports findings to strategist

### 2. Collector Agent (Green)
**Role**: Gather resources for the base

- Moves to resource locations
- Carries up to 5 resources per trip
- Delivers to base camp
- Reports theft if base is breached
- Follows strategist's commands

### 3. Attacker Agent (Red)
**Role**: Pursue and capture the thief

- Waits for thief detection alert
- Moves to thief's last known position
- Faster than normal agents (1.1x speed)
- Captures thief on contact
- Patrols base defense when idle

### 4. Strategist Agent (Magenta)
**Role**: Coordinate team strategy

- Central command and control
- Processes information from all agents
- Makes strategic decisions
- Issues commands to other agents
- Maintains shared team knowledge

---

## 🗣️ Communication System (Blackboard)

Agents communicate via a **shared blackboard** system:

### Blackboard Data
```python
blackboard = {
    "thief_position": (x, y),
    "thief_last_seen": {"position": (x,y), "observer": "id", "timestamp": time},
    "resources_at_base": 20,
    "resources_locations": [(x,y), ...],
    "base_status": "safe" or "breached",
    "agents_status": {...},
    "strategist_commands": [...],
}
```

### Message Types
- `thief_sighted`: Explorer spotted the thief
- `resource_discovered`: New resource found
- `resource_collected`: Collector picked up resources
- `base_breached`: Thief stealing from base
- `intercept_command`: Strategist orders attack
- `collect_resource`: Strategist assigns collection task

### Communication Flow
```
Explorer sees thief
    ↓
Posts "thief_sighted" to blackboard
    ↓
Strategist reads message
    ↓
Strategist posts "intercept_command"
    ↓
Attacker sees command
    ↓
Attacker pursues thief
```

---

## ⚙️ Configuration

Edit `config/game_config.py` to customize:

### Game Settings
```python
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 60

RESOURCES_INITIAL_COUNT = 20
PLAYER_CARRYING_CAPACITY = 3
```

### Agent Settings
```python
AGENT_SPEED = 3.5
AGENT_VISION_RANGE = 150
AGENT_COMMUNICATION_RANGE = 300

PLAYER_SPEED = 5
PLAYER_STEALTH_DURATION = 180  # frames
PLAYER_STEALTH_COOLDOWN = 300
```

### Difficulty Presets
```python
DIFFICULTY_EASY = {"agent_count": 2, "agent_speed_multiplier": 0.8}
DIFFICULTY_NORMAL = {"agent_count": 4, "agent_speed_multiplier": 1.0}
DIFFICULTY_HARD = {"agent_count": 6, "agent_speed_multiplier": 1.3}
```

### Debug Options
```python
DEBUG_MODE = False              # Enable debug info
SHOW_AGENT_VISION = False       # Show agent vision ranges
SHOW_COMMUNICATION = False      # Show communication lines
SHOW_FPS = True                 # Display FPS counter
```

---

## 🎯 Win Conditions

### Thief Wins
✅ Steal all resources from base (resources reach 0)
✅ Secure enough resources at hideout (20 total)

### Agents Win
✅ Attacker catches the thief (contact)

---

## 🧠 Agent Decision Making

Agents use **rule-based decision making**:

### Explorer Logic
```python
if not explored_zones:
    select_new_zone()
    
if thief_in_vision():
    report_thief_sighting()
    
if resource_found():
    report_resource_location()
```

### Collector Logic
```python
if at_base_and_loaded():
    deliver_resources()
else:
    if target_resource:
        move_to_target()
    else:
        find_nearest_resource()
```

### Attacker Logic
```python
if thief_detected():
    pursue_thief()
elif last_known_position:
    move_to_last_position()
else:
    patrol_base()
```

### Strategist Logic
```python
if thief_position_known():
    command_intercept()
    
if resources_low():
    command_collect()
    
if base_breached():
    command_defend()
```

---

## 📊 Game States

| State | Description |
|-------|-------------|
| `RUNNING` | Active gameplay |
| `PAUSED` | Game paused (P key) |
| `PLAYER_WIN` | Thief succeeded |
| `AGENTS_WIN` | Agents caught thief |

---

## 🧩 Key Classes

### Core Systems
- **GameEngine**: Main game loop, orchestrates all systems
- **Blackboard**: Shared communication and knowledge system
- **UIManager**: Handles all rendering and UI

### Game Entities
- **Player**: Thief character (player-controlled)
- **BaseAgent**: Abstract base class for all agents
- **ExplorerAgent**: Scouting and detection
- **CollectorAgent**: Resource gathering
- **AttackerAgent**: Thief pursuit
- **StrategistAgent**: Team coordination

### Environment
- **GameMap**: Map terrain and obstacles
- **ResourceManager**: Resource spawning and tracking
- **BaseCamp**: Team base and storage
- **ThiefHideout**: Thief's safe location

---

## 🔧 Extending the Game

### Add New Agent Type
1. Create new file in `src/agents/`
2. Inherit from `BaseAgent`
3. Implement `think()` method
4. Register in `GameEngine._spawn_agents()`

Example:
```python
class ScoutAgent(BaseAgent):
    def __init__(self, agent_id, x, y):
        super().__init__(agent_id, "scout", x, y)
    
    def think(self):
        # Your decision logic here
        pass
```

### Add New Game Mechanic
1. Modify `game_config.py` for constants
2. Implement logic in relevant class
3. Update `GameEngine.update()` if needed

### Add UI Element
1. Create rendering method in `UIManager`
2. Call from `GameEngine.draw()`

---

## 📈 Game Statistics

Tracked during gameplay:
- **Elapsed Time**: Game duration
- **Resources Collected**: By agents
- **Resources Stolen**: By thief
- **Agent Communications**: Message count
- **Exploration Progress**: Areas covered
- **Base Breach Count**: Number of thefts

---

## 🐛 Debugging

Enable debug mode in `config/game_config.py`:

```python
DEBUG_MODE = True
SHOW_AGENT_VISION = True
SHOW_COMMUNICATION = True
```

This displays:
- Agent vision ranges
- Communication paths
- Explored areas
- Collision boxes (coming soon)

---

## 🎓 Educational Value

This project demonstrates:
- **Multi-Agent Systems**: Agents with independent behavior
- **Communication Patterns**: Blackboard architecture
- **Coordination Algorithms**: Team strategy and decision-making
- **Game Development**: Pygame, game loops, rendering
- **AI Concepts**: Decision trees, pathfinding, state management

---

## 📝 Future Enhancements

- [ ] Difficulty levels (Easy/Normal/Hard)
- [ ] Power-ups and special abilities
- [ ] Different map layouts
- [ ] Procedural resource generation
- [ ] Agent learning/adaptation
- [ ] Sound effects and music
- [ ] Replay system
- [ ] Level editor
- [ ] Multiplayer support
- [ ] Advanced pathfinding (A*)

---

## 📄 License

This project is open source and available under the MIT License.

---

## 👥 Author

Created as an educational project demonstrating multi-agent systems and game development.

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

---

## 📞 Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

## 📚 Resources

- [Pygame Documentation](https://www.pygame.org/docs/)
- [Multi-Agent Systems](https://en.wikipedia.org/wiki/Multi-agent_system)
- [Blackboard Architecture](https://en.wikipedia.org/wiki/Blackboard_system)
- [Game Development Patterns](https://gameprogrammingpatterns.com/)

---

**Enjoy the game and may the best team win! 🎮**
