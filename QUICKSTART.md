# Quick Start Guide

## Installation & Running

### Step 1: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Game
```bash
python main.py
```

The game window should open with:
- Your thief (cyan circle) at bottom-left
- Base camp (green circle) at center
- Your hideout (red circle) at top-left
- 4 AI agents defending the base
- 20 initial resources to steal

---

## First 60 Seconds

1. **Press W/A/S/D** to move your thief around the map
2. **Move to the green base camp** (center) to steal resources
3. **You can carry 3 resources** at a time
4. **Watch out for the red attacker agent** - it will chase you!
5. **Use SPACE to go invisible** for 3 seconds (allows escape)
6. **Return to your hideout** (red circle, top-left) to secure stolen resources
7. **If caught, agents win** - if you steal all resources, you win!

---

## Controls Quick Reference

| Key | Action |
|-----|--------|
| **W** / **↑** | Move up |
| **A** / **←** | Move left |
| **S** / **↓** | Move down |
| **D** / **→** | Move right |
| **SPACE** | Activate stealth (3 sec invisibility) |
| **P** | Pause game |
| **ESC** | Quit game |

---

## Strategy Tips

### Early Game (First 30 seconds)
- Scout the map, find the base camp
- Learn the positions of each agent
- Plan your first heist route

### Mid Game (30-90 seconds)
- Use stealth to bypass the Attacker
- Be quick and decisive
- Don't get surrounded

### Late Game (90+ seconds)
- Resources at base get depleted
- Agents get better at intercepting
- Speed and timing are critical

### Advanced Tips
1. **Stealth Timing**: Use stealth when you see the Attacker approaching
2. **Resource Routes**: Find the fastest path between base and hideout
3. **Agent Patterns**: Explorers have predictable patrol routes
4. **Safe Zones**: Stay behind obstacles when possible
5. **Collector Interference**: Block collectors to slow resource gathering

---

## Game Objects Legend

| Color | Object | Description |
|-------|--------|-------------|
| 🟢 Green | Base Camp | Enemy resource storage (steal here) |
| 🔴 Red | Hideout | Your safe zone (secure resources here) |
| 🔵 Cyan | You (Thief) | Player character |
| 🔵 Blue | Explorer | Scouts for threats and resources |
| 🟢 Green | Collector | Gathers resources for base |
| 🔴 Red | Attacker | Pursues the thief |
| 🟣 Purple | Strategist | Coordinates team strategy |
| 🟡 Yellow | Resource | Steal this to win |

---

## Win Conditions Explained

### You Win (Thief)
- Steal **all 20 resources** from the base, OR
- Secure **20 resources** at your hideout

### Agents Win
- **Attacker catches you** (collision)

---

## Common Mistakes to Avoid

❌ **Running straight to base**: You'll get caught
- ✅ Use stealth and obstacles for cover

❌ **Forgetting to return to hideout**: Resources in your inventory don't count
- ✅ Remember to go to the red circle to secure loot

❌ **Getting trapped**: Don't let agents corner you
- ✅ Keep moving and use stealth wisely

❌ **Wasting stealth cooldown**: It has a 5-second recharge
- ✅ Save it for when you really need it

---

## Troubleshooting

### Game won't start
```bash
# Make sure pygame is installed
pip install pygame==2.5.2

# Try running with Python explicitly
python3 main.py
```

### Game is too hard/easy
Edit `config/game_config.py`:
```python
# Make agents slower
AGENT_SPEED = 2.0  # default 3.5

# Make stealth longer
PLAYER_STEALTH_DURATION = 300  # default 180 (frames)

# Reduce resources to collect
RESOURCES_INITIAL_COUNT = 10  # default 20
```

### Game is lagging
```python
# In config/game_config.py:
FPS = 30  # default 60 - reduce for slower computers
```

---

## Learning the Game Systems

### Understanding Agent Communication
- Agents share information through the **blackboard**
- When Explorer sees you, it posts a message
- Strategist reads the message and orders Attacker
- Attacker then hunts you down

### Understanding Resources
- Collectors bring in resources constantly
- You need to steal them from base
- Carrying capacity is 3 (must trip to hideout)
- Agents adapt their defense based on theft patterns

---

## Customization

### Change Game Difficulty
```python
# config/game_config.py

# Slow down agents (easier)
AGENT_SPEED = 2.0

# Speed up agents (harder)
AGENT_SPEED = 5.0

# Make stealth longer (easier)
PLAYER_STEALTH_DURATION = 300

# More resources to steal (easier)
RESOURCES_INITIAL_COUNT = 30
```

### Enable Debug Features
```python
# config/game_config.py

DEBUG_MODE = True              # Show debug info
SHOW_AGENT_VISION = True       # Show vision ranges
SHOW_FPS = True                # Show frame rate
```

---

## Performance Tips

If game is slow:
1. Reduce FPS to 30 (config)
2. Disable debug visualizations
3. Reduce obstacle count
4. Use smaller window size

---

## Next Steps

1. **Play a few games** to understand mechanics
2. **Try different strategies** to steal resources
3. **Read the full README.md** for advanced info
4. **Modify config** to create custom difficulties
5. **Read the code** to learn how it works
6. **Add new features** if you want to extend it!

---

## Have Fun! 🎮

The goal is to outsmart the AI agents and prove you're the ultimate master thief!

Good luck! 🎯
