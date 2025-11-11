# Therapy Simulator 1987

## Game Concept
A darkly humorous turn-based RPG where you play as a therapist dealing with increasingly absurd clients. Navigate through five different therapy locations, engage in psychological "combat" with difficult clients, and try to maintain your sanity while helping others (or making things worse).

## Features

### Character Creation
Choose from three distinct therapist classes:
- **Empath**: Insight-focused (Base stats: Patience 4, Empathy 4, Insight 8, Composure 5) - Special ability: "Sad Realization"
- **Counselor**: Empathy-focused (Base stats: Patience 5, Empathy 8, Insight 3, Composure 6) - Special ability: "Fake Sympathy"
- **Burnout**: Patience-focused (Base stats: Patience 8, Empathy 4, Insight 3, Composure 4) - Special ability: "Dead Inside Stare"

Each class has unique base stats that affect your therapeutic approach and effectiveness.

### Multi-Stage Story Progression
Progress through five therapy environments (automatic advancement after completing required clients):
1. **Community Center** - Run-down center where therapy happens between bingo nights (2 clients needed)
2. **Corporate Wellness Program** - Sterile office building for broken employees (2 clients needed)
3. **Crisis Intervention Center** - Where the really messed up cases end up (2 clients needed)
4. **Private Practice** - Your own office with premium rates (2 clients needed)
5. **State Mental Hospital** - Rock bottom of the therapy world (1 client needed)

Each location has unique:
- **Location Effects**: Special bonuses (e.g., empathy bonus, insight bonus, patience bonus)
- **Difficulty Modifiers**: Clients become more challenging at higher stages
- **Stage Bonuses**: Rewards when advancing (XP, reputation, stat increases, special items)
- **Client Pool**: Different clients appear at different locations

### Turn-Based Combat System
When clients have psychological breakdowns, engage in therapeutic "combat" with dice-based mechanics:
- **Emotional Support**: Reduces client chaos using Empathy stat + dice roll (1-6)
- **Logical Analysis**: Breaks client delusions using Insight stat + dice roll (1-6)
- **Patient Listening**: Heals your sanity using Patience stat + dice roll (1-4), reduces incoming damage
- **Use Item**: Consume inventory items for healing effects

**Combat Mechanics:**
- Player starts with Composure + 5 bonus sanity (max 20)
- Client has HP = absurdity + resistance
- Dice rolls add unpredictability to damage
- Victory grants +1 Empathy and sets client absurdity to 0
- Defeat reduces Composure and restarts the client session (slightly harder)

### Inventory & Items
Collect and use various therapeutic tools (click items to use):
- **Coffee**: Restores Patience +2 (2 uses initially)
- **Notepad**: Restores Empathy +2 (1 use initially)
- **Meditation Guide**: Restores Insight +2 (1 use initially)
- **Energy Drink**: Restores Composure +2 (1 use initially)

Items can be used during regular sessions or combat. Each use restores stats by 2 points (max 15).

### Branching Choices & Multiple Endings
- **Complex dialogue trees** with client replies that provide context before continuing
- **Meaningful stat changes** based on choice types:
  - Empathetic responses increase Empathy, reduce client absurdity (extra effective with high Empathy)
  - Analytical responses increase Insight, reduce client absurdity (breakthroughs with high Insight)
  - Patient responses increase Patience, reduce client absurdity (calming effect with high Patience)
  - Dismissive responses increase Composure (professional detachment)
  - Challenging responses decrease Patience and Composure
- **Location-specific bonuses** enhance certain approaches
- **Low stat penalties** make sessions harder when stats drop below 2-3
- **15+ unique endings** based on flags and final stats:
  - Success endings (The Life Changer, The Zen Master, Celebrity Therapist)
  - Specialized endings (The Unbreakable, The Heart Whisperer, The Mind Reader)
  - Controversial endings (The Provocateur, The Convert)
  - Failure endings (Mental Breakdown)

### Stats System
Four core stats that affect all gameplay (range 1-15):
- **Patience**: How much nonsense you can tolerate before snapping (affects patient responses and composure recovery)
- **Empathy**: How well you connect with clients (affects supportive responses and breakthrough chances)
- **Insight**: Your ability to analyze psychological issues (affects analytical responses and understanding)
- **Composure**: Your mental stability (low composure causes problems, affects combat sanity and detached responses)

**Stat Progression:**
- Level up every 5 XP with class-specific bonuses
- Choices during sessions modify stats dynamically
- High stats (10+) unlock better endings and improve effectiveness
- Low stats (≤2) cause complications and reduce success rates

## How to Run

### Requirements
- Python 3.8 or higher
- Tkinter (included with standard Python installation)
- No external dependencies required

### Installation & Execution
1. Ensure Python 3.8+ is installed on your system
2. Download `therpaysim.py.py` to your desired directory
3. Open terminal/command prompt in that directory
4. Run the game:
   ```bash
   python therpaysim.py.py
   ```
   or on Unix/Mac:
   ```bash
   python3 therpaysim.py.py
   ```

### Controls
- **Mouse**: Click dialogue choices and buttons
- **Typewriter Speed Slider** (2-20 ms): Adjust text display speed (smaller = faster)
- **Continue Button**: Appears after client replies - click to proceed
- **Inventory Buttons**: Click items in the right panel to use them immediately
- **Quick Action Buttons**: Use Item, Show Stats, Check Progress, End Day Early

## Gameplay Interface

### Main Window Layout
- **Left Panel** (640x660): Client dialogue area with choice buttons and quick actions
- **Right Panel** (310x660): Therapist stats, inventory, and session log
- **Bottom Bar**: Typewriter speed slider, Debate Client button, View Progress button
- **Top Banner**: Game title display

### Quick Action Buttons
- **Use Item**: Opens item selection dialog (alternative to clicking items directly)
- **Show Stats**: Display current stats in a popup
- **Check Progress**: View ending progress and requirements
- **End Day Early**: Manually end session and see ending
- **Debate Client**: Initiates combat encounter (also triggered by certain client escalations)
- **View Progress**: Shows current location, clients completed, and stage unlock info

### Combat Interface
When psychological combat is triggered:
- **Health bars**: Your Sanity (blue) vs Client Chaos (red)
- **Turn count**: Tracks battle progression
- **Combat log**: Details all actions and dice rolls
- **Four action buttons**: Emotional Support, Logical Analysis, Patient Listening, Use Item
- **Automatic turn resolution**: Client attacks after each player action
- **Victory**: +1 Empathy, client absurdity set to 0, session completes normally
- **Defeat**: -1 Composure, same client restarts with +1 absurdity

### Session Flow
1. Client dialogue appears with typewriter effect
2. Multiple choice buttons appear after text completes
3. Click a choice to respond
4. Client reply appears (if specified in dialogue)
5. Click "Continue →" button to proceed
6. Stats update based on choice type and current stats
7. Session continues until dialogue tree ends or combat triggers
8. Session completion awards XP, reputation, and possibly items
9. Automatic advancement to next location after meeting client requirements

### Error Handling
The game includes comprehensive error handling for:
- Invalid dialogue node references (ends session gracefully)
- Widget destruction during state changes (prevents Tcl errors)
- Multiple rapid button clicks (prevented with in-progress flags)
- Empty inventory usage (shows appropriate messages)
- Client loading errors (logs warnings and continues)
- Combat state management (proper cleanup on victory/defeat)

All errors display user-friendly messages and attempt graceful recovery.

## Client Roster

The game features 9 unique clients with distinct personalities and dialogue trees:
- **Toaster Guy**: Man whose toaster burns existential messages into his toast
- **Mime Lady**: Communicates only through mime about social anxiety and depression
- **Business Guy**: CEO with no empathy who monetizes everything including his midlife crisis
- **Office Supply Choir**: Person who started a death metal band with office supplies
- **Weird Cult Person**: Escaped a death cult but thinks regular life is worse
- **Wannabe Influencer**: Aspiring TikTok star with 3 followers (one is mom's alt account)
- **Conspiracy Guy**: Believes coffee chains are psychological warfare
- **Failed Artist**: Studied in Vienna, now has student debt and no career
- **Anxious Parent**: Terrified they're ruining their child based on Google searches

Each client has:
- Multiple dialogue nodes with branching paths
- Base absurdity and resistance levels (modified by location difficulty)
- Special effects that can trigger (breakthroughs, heated arguments, joined delusions)
- Contextual replies that respond to your specific choices

## Game Features Summary

✅ **Character Classes**: 3 unique therapist specializations with distinct base stats  
✅ **Multi-Stage Progression**: 5 therapy locations with automatic advancement and unique bonuses  
✅ **Turn-Based Combat**: Dice-based psychological battles (d6 rolls + stat bonuses)  
✅ **Inventory System**: 4 therapeutic items with stat restoration (+2 each)  
✅ **Branching Dialogue**: Complex choice trees with client replies and continue buttons  
✅ **Dynamic Stats**: Stat changes based on choice types, with high/low stat effects  
✅ **Location Effects**: Each stage provides unique bonuses to specific approaches  
✅ **Multiple Endings**: 15+ distinct endings based on flags and final stats  
✅ **Experience System**: Level up every 5 XP with class-specific stat bonuses  
✅ **Session Rewards**: XP, reputation, breakthrough bonuses, item drops  
✅ **Error Handling**: Comprehensive error recovery and user-friendly messages  
✅ **GUI Interface**: 980x740 window with typewriter effects and visual feedback

## Tips for New Players
1. **Choose your class based on playstyle** - Empath for analysis, Counselor for empathy, Burnout for patience
2. **Manage your Composure** - Low composure (<2) causes problems and backfires
3. **Match approaches to locations** - Community Center rewards empathy, Corporate rewards insight, Crisis rewards patience
4. **Use items strategically** - They restore 2 stat points and can turn difficult sessions around
5. **Read client replies carefully** - They provide context and personality before you continue
6. **Aim for breakthroughs** - Reduce client absurdity to ≤2 for bonus XP and reputation
7. **Track ending progress** - Use "Check Progress" button to see what endings you're working toward
8. **Combat is optional** - Avoid heated arguments unless you want The Provocateur ending
9. **High stats matter** - Stats at 10+ significantly improve effectiveness and unlock better endings
10. **Embrace the absurdity** - The game is darkly comedic by design

## Ending Requirements (Spoiler Alert)

**Catastrophic:**
- Mental Breakdown: Composure ≤0 or melted_down flag

**Controversial:**
- The Provocateur: 3+ heated arguments
- The Convert: 2+ joined delusions

**Excellent:**
- The Life Changer: 2+ life-changing breakthroughs
- The Zen Master: 4+ breakthroughs + Composure ≥5

**Success:**
- Celebrity Therapist: Reputation ≥16
- Experienced Professional: XP ≥25

**Specialized:**
- The Unbreakable: Patience ≥15
- The Heart Whisperer: Empathy ≥15
- The Mind Reader: Insight ≥15

**Neutral:**
- The Reliable Professional: Reputation ≥12
- The Steady Hand: Composure ≥8
- The Decent Therapist: Reputation ≥8

**Poor:**
- The Questionable Professional: Reputation ≤5
- The Quiet Exit: Default ending

Enjoy your descent into the world of therapeutic dysfunction!