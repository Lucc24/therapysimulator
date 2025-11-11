# Therapy Simulator 1987

## Game Concept
A darkly humorous turn-based RPG where you play as a therapist dealing with increasingly absurd clients. Navigate through different therapy locations, engage in psychological "combat" with difficult clients, and try to maintain your sanity while helping others (or making things worse).

## Features

### Character Creation
Choose from three distinct therapist classes:
- **Empath**: High Insight, understands why people are broken but can't fix them either
- **Counselor**: High Empathy, pretends to care about people's problems for money  
- **Burnout**: High Patience, gave up caring years ago but somehow that helps

Each class has unique stats and special abilities that affect gameplay.

### Multi-Stage Story Progression
Progress through different therapy environments:
1. **Community Center** (Start) - Run-down center where therapy happens between bingo nights
2. **Corporate Wellness Program** (5+ XP) - Sterile office building for broken employees
3. **Crisis Intervention Center** (15+ XP) - Where the really messed up cases end up

Each location offers different clients and stage bonuses.

### Turn-Based Combat System
When clients have psychological breakdowns, engage in therapeutic "combat":
- **Empathy Attack**: Use emotional connection (Empathy stat + dice roll)
- **Insight Strike**: Apply psychological analysis (Insight stat + dice roll)  
- **Patient Defense**: Endure and heal (Patience stat + dice roll)
- **Use Item**: Consume inventory items for various effects

Combat uses dice rolls for unpredictability and stat-based damage calculations.

### Inventory & Items
Collect and use various therapeutic tools:
- **Coffee**: Restores Patience (+2 uses)
- **Notepad**: Restores Empathy (1 use)
- **Meditation Guide**: Restores Insight (1 use)
- **Energy Drink**: Restores Composure (1 use)

Items can be used during regular sessions or combat encounters.

### Branching Choices & Multiple Endings
- **Dialogue trees** with meaningful consequences that affect client outcomes
- **At least 15+ unique endings** based on your choices and performance:
  - Success endings (high stats, good reputation)
  - Failure endings (burnout, malpractice)
  - Absurd endings (joining client delusions)
  - Neutral endings (barely surviving the profession)

### Stats System
Four core stats that affect all gameplay:
- **Patience**: How much nonsense you can tolerate before snapping
- **Empathy**: How well you pretend to care about other people's problems  
- **Insight**: Your ability to see why everyone is doomed
- **Composure**: Your mental stability and sanity level

Stats range from 0-10 and directly impact success rates, combat effectiveness, and available dialogue options.

## How to Run

### Requirements
- Python 3.8 or higher
- Tkinter (included with most Python installations)
- No additional dependencies required

### Installation & Execution
1. Ensure Python 3.8+ is installed on your system
2. Download `therpaysim.py.py` to your desired directory
3. Open terminal/command prompt in that directory
4. Run the game:
   ```bash
   python therpaysim.py.py
   ```
   or
   ```bash
   python3 therpaysim.py.py
   ```

### Controls
- **Mouse**: Click buttons to make dialogue choices and use items
- **Typewriter Speed Slider**: Adjust text display speed to your preference
- **Stage Selection**: Choose therapy locations as you unlock them
- **Inventory Management**: Click item buttons to use therapeutic tools

## Gameplay Commands

### Main Interface
- **Dialogue Choices**: Click response buttons to interact with clients
- **Use Item**: Open inventory and select items to restore stats
- **Stage Selection**: Access different therapy locations (unlocked by XP)

### Combat Interface  
- **Empathy Attack**: Primary offensive action using Empathy stat
- **Insight Strike**: High-damage attack using Insight stat
- **Patient Defense**: Defensive action that heals and reduces incoming damage
- **Use Item**: Quick item usage during psychological combat

### Error Handling
The game includes comprehensive error handling for:
- Invalid client dialogue states
- Empty inventory usage attempts
- Missing or corrupted game data
- Unexpected player inputs
- Save/load errors and edge cases

All errors display user-friendly messages and gracefully recover when possible.

## Game Features Summary

✅ **Character Classes**: 3 unique therapist specializations with distinct stats and abilities  
✅ **Multi-Stage Progression**: 3 therapy locations with unlock requirements and unique content  
✅ **Turn-Based Combat**: Dice-based psychological battles with multiple action types  
✅ **Inventory System**: Collectible items with usage limits and stat restoration  
✅ **Branching Dialogue**: Complex choice trees leading to multiple story paths  
✅ **Multiple Endings**: 15+ distinct endings based on player choices and performance  
✅ **Error Handling**: Comprehensive input validation and graceful error recovery  
✅ **Documentation**: Complete README with installation and gameplay instructions

## Tips for New Players
1. **Choose your class wisely** - Each specialization excels in different situations
2. **Manage your items carefully** - They have limited uses and are crucial for difficult encounters
3. **Pay attention to client absurdity levels** - Higher levels indicate more challenging sessions
4. **Experiment with dialogue choices** - The humor and outcomes vary significantly based on your responses
5. **Don't take it too seriously** - The game is intentionally absurd and darkly comedic

Enjoy your descent into the world of therapeutic dysfunction!