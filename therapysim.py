#!/usr/bin/env python3
"""
Therapy Simulator 1987 — Python GUI Turn-Based RPG

A darkly humorous therapy simulator where you play as a therapist dealing with absurd clients.
Features turn-based combat, character classes, multi-stage progression, and branching storylines.

GAME FEATURES:
- Character Creation: 3 therapist classes (Empath, Counselor, Burnout) with unique stats
- Multi-Stage Progression: 3 therapy locations that unlock based on XP progression  
- Turn-Based Combat: Dice-based psychological battles when clients have breakdowns
- Inventory System: Collectible therapeutic items with limited uses
- Branching Dialogue: Complex choice trees leading to 15+ different endings
- Error Handling: Comprehensive input validation and graceful error recovery

TECHNICAL REQUIREMENTS:
- Python 3.8+ with tkinter (included in standard Python installation)
- No external dependencies required
- Single-file executable for easy distribution

CONTROLS:
- Mouse: Click dialogue choices and item buttons
- Typewriter Speed: Adjustable text display speed
- Stage Selection: Choose therapy locations as they unlock
- Combat Actions: Turn-based battle system with multiple action types
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time
import random
import threading

# ---------------------------
# Game constants & data
# ---------------------------

TYPE_SPEED_DEFAULT = 6  # ms per character (smaller -> faster)

# Multi-stage story progression - different therapy environments with unique client pools
THERAPY_STAGES = [
    {
        "name": "Community Center",
        "desc": "A run-down community center where therapy happens between bingo nights",
        "clients": ["toaster", "mime"],  # Quirky local cases
        "clients_needed": 2,
        "stage_bonus": {"reputation": 1},
        "location_effects": {
            "empathy_bonus": 1,
            "difficulty_modifier": 0,
            "special_items": ["Coffee"],
            "description": "The community setting makes clients more receptive to empathy"
        }
    },
    {
        "name": "Corporate Wellness Program", 
        "desc": "Sterile office building where companies dump their broken employees",
        "clients": ["business", "choir"],  # Work-related breakdown cases
        "clients_needed": 2,
        "stage_bonus": {"xp": 2, "reputation": 1},
        "location_effects": {
            "insight_bonus": 1,
            "difficulty_modifier": 1,
            "special_items": ["Energy Drink", "Notepad"],
            "description": "Corporate environment rewards analytical thinking but clients are more guarded"
        }
    },
    {
        "name": "Crisis Intervention Center",
        "desc": "Where the really messed up cases end up after everything else failed", 
        "clients": ["cult", "influencer"],  # Extreme crisis cases
        "clients_needed": 2,
        "stage_bonus": {"all_stats": 1, "xp": 1},
        "location_effects": {
            "patience_bonus": 2,
            "difficulty_modifier": 2,
            "special_items": ["Meditation Guide", "Coffee"],
            "description": "Crisis situations demand extreme patience but clients' problems are severe"
        }
    },
    {
        "name": "Private Practice",
        "desc": "Your own office where you can charge premium rates for the same failure",
        "clients": ["conspiracy", "artist"],  # Affluent clients with specific issues
        "clients_needed": 2,
        "stage_bonus": {"reputation": 3, "xp": 3, "all_stats": 1},
        "location_effects": {
            "all_bonus": 1,
            "difficulty_modifier": 0,
            "special_items": ["Coffee", "Notepad", "Energy Drink"],
            "description": "Your own practice allows maximum flexibility and effectiveness"
        }
    },
    {
        "name": "State Mental Hospital",
        "desc": "Rock bottom of the therapy world where hope goes to die",
        "clients": ["parent"],  # The most challenging case
        "clients_needed": 1,
        "stage_bonus": {"all_stats": 2, "xp": 5},
        "location_effects": {
            "composure_bonus": 2,
            "difficulty_modifier": 3,
            "special_items": ["Meditation Guide", "Energy Drink"],
            "description": "The worst cases require emotional detachment to survive"
        }
    }
]

STAT_DESCRIPTIONS = {
    "Patience": "How much nonsense you can tolerate before snapping. Higher patience = more effective patient responses and prevents impatient mistakes.",
    "Empathy": "How well you connect with and understand clients. Higher empathy = more effective supportive responses and breakthrough chances.",
    "Insight": "Your ability to analyze and understand psychological issues. Higher insight = more effective analytical responses and better client understanding.",
    "Composure": "Your mental stability and professional detachment. Higher composure = better stress management and effective detached responses. Low composure causes problems!"
}

CLASS_TEMPLATES = {
    "Empath": {"desc": "Insight-focused. Understands why people are broken but can't fix them either.", "base": {"Patience": 4, "Empathy": 4, "Insight": 8, "Composure": 5}, "ability": "Sad Realization"},
    "Counselor": {"desc": "Empathy-focused. Pretends to care about people's problems for money.", "base": {"Patience": 5, "Empathy": 8, "Insight": 3, "Composure": 6}, "ability": "Fake Sympathy"},
    "Burnout": {"desc": "Patience-focused. Gave up caring years ago but somehow that helps.", "base": {"Patience": 8, "Empathy": 4, "Insight": 3, "Composure": 4}, "ability": "Dead Inside Stare"},
}

ITEMS = {
    "Coffee": {"desc": "Restores Patience (+2)", "uses": 2, "stat": "Patience"},
    "Notepad": {"desc": "Restores Empathy (+2)", "uses": 1, "stat": "Empathy"},
    "Meditation Guide": {"desc": "Restores Insight (+2)", "uses": 1, "stat": "Insight"},
    "Energy Drink": {"desc": "Restores Composure (+2)", "uses": 1, "stat": "Composure"}
}

# Each client built as nodes where choices lead to next nodes (None ends session)
def build_clients_data():
    clients = []

    # Toaster Guy
    toaster_nodes = {
        "start": {"text": "Toaster Guy: \"My toaster started burning existential dread into my bread this morning and honestly it's the most attention I've gotten all year\"",
                  "choices": [
                      {"text": "Cool story", "next": "explain", "effects": None, "reply": "Yeah well at least someone in my kitchen cares about my feelings even if it's trying to kill me with carbs"},
                      {"text": "What does it burn exactly", "next": "paranoid", "effects": None, "reply": "Little skulls mostly, sometimes a middle finger when I forget to clean the crumb tray"},
                      {"text": "Maybe buy a new toaster", "next": "defensive", "effects": {"absurdity": +1}, "reply": "Oh sure abandon the one relationship where someone actually communicates with me"},
                      {"text": "How does that make you feel", "next": "hopeful", "effects": {"absurdity": -1}, "reply": "Like my appliances have higher emotional intelligence than my family which is both sad and accurate"},
                  ]},
        "explain": {"text": "Toaster Guy: \"Yesterday it burned 'your life is toast' into my english muffin which was both literally accurate and emotionally devastating\"",
                  "choices": [
                      {"text": "Mm-hmm", "next": "paranoid", "effects": {"absurdity": -1}, "reply": "I mean it's not wrong my life is basically burnt bread at this point"},
                      {"text": "And how did that feel", "next": "deeper", "effects": None, "reply": "Like my breakfast was roasting me harder than my ex-wife did in court"},
                      {"text": "What else does it say", "next": "escalate", "effects": {"absurdity": +1}, "reply": "This morning it burned 'kill me' into my bagel but I think that was actually my subconscious talking"}
                  ]},
        "paranoid": {"text": "Toaster Guy: \"Last week it burned 'you disappoint your ancestors' into my wonder bread which really hit different you know\"",
                     "choices": [
                         {"text": "Sure", "next": "deeper", "effects": None, "reply": "My great grandmother survived the depression and I'm out here crying over toast messages from a kitchen appliance"},
                         {"text": "That sounds hard", "next": "hopeful", "effects": {"absurdity": -1}, "reply": "The worst part is it's probably right like my ancestors didn't die in wars so I could have a breakdown over carbs"},
                         {"text": "Toasters don't think", "next": "escalate", "effects": {"absurdity": +1}, "reply": "Neither do most people but at least my toaster has the decency to be upfront about wanting me dead"}
                     ]},
        "defensive": {"text": "Toaster Guy: \"I know what you're thinking but at least my toaster's death threats are creative unlike my family's which are just boring and repetitive\"",
                    "choices": [
                        {"text": "Right", "next": "hopeful", "effects": {"absurdity": -1}, "reply": "See this is why I like you you don't judge my relationships with household appliances"},
                        {"text": "What do they say", "next": "deeper", "effects": None, "reply": "Same old disappointment speeches but with less artistic flair than burnt toast"}
                    ]},
        "deeper": {"text": "Toaster Guy: \"My toaster burned 'you have daddy issues' into my pop tart and honestly that's the most accurate psychological assessment I've ever received\"",
                      "choices": [
                          {"text": "Interesting", "next": None, "effects": {"absurdity": -1, "breakthrough": True}, "reply": "Yeah my dad left when I was twelve and apparently my breakfast pastries remember better than my therapist"},
                          {"text": "How do you feel about that", "next": None, "effects": None, "reply": "Like I'm paying you to do what my toaster does for free except with less emotional depth"}
                      ]},
        "hopeful": {"text": "Toaster Guy: \"Do you think it's weird that my toaster gives better life advice than my divorced parents and my dead-end job combined\"",
                    "choices": [
                        {"text": "Not really", "next": None, "effects": {"absurdity": -1, "breakthrough": True}, "reply": "Cool because I'm pretty sure my microwave is writing my resume and it's doing better than I ever did"},
                        {"text": "Maybe try human contact", "next": None, "effects": None, "reply": "Nah people are disappointing but kitchen appliances really commit to the bit"}
                    ]},
        "escalate": {"text": "Toaster Guy: \"This morning my toaster burned 'kill yourself' into my bagel and honestly it was the most honest conversation I've had all week\"",
                     "choices": [
                         {"text": "Okay", "next": "paranoid", "effects": {"absurdity": -1}, "reply": "At least someone's being direct with me instead of this passive aggressive therapy nonsense"},
                         {"text": "That's concerning", "next": None, "effects": {"start_debate": True, "heated_argument": True}, "reply": None}
                     ]}
    }
    clients.append({"id": "toaster", "name": "Toaster Guy", "nodes": toaster_nodes, "absurdity": 6, "resistance": 4})

    # Social Anxiety Client
    mime_nodes = {
        "start": {"text": "Mime Lady: *mimes being dead inside while maintaining perfect invisible box technique*",
                  "choices": [
                      {"text": "Sure", "next": "comfortable", "effects": {"absurdity": -1}, "reply": "*mimes that her existential crisis has better stage presence than most Broadway shows*"},
                      {"text": "Are you actually mute", "next": "nervous", "effects": None, "reply": "*mimes that talking is for people who have something worth saying*"},
                      {"text": "This is stupid", "next": "defensive", "effects": {"absurdity": +1}, "reply": "*mimes agreeing but also that life itself is pretty stupid so why not commit to the bit*"},
                      {"text": "Cool let me try", "next": "breakthrough", "effects": {"absurdity": -2}, "reply": "*mimes being shocked that someone else understands the art of communicating through aggressive silence*"}
                  ]},
        "comfortable": {"text": "Mime Lady: *mimes that her depression has excellent mime technique and really commits to the performance*",
                      "choices": [
                          {"text": "Mm-hmm", "next": "opening", "effects": None, "reply": "*mimes that at least her mental illness is artistically expressed*"},
                          {"text": "How do you feel", "next": "anxious", "effects": {"absurdity": +1}, "reply": "*mimes being crushed by the invisible weight of having to pretend everything is fine*"},
                          {"text": "What happened", "next": "opening", "effects": None, "reply": "*elaborate mime performance depicting her family's disappointment in her life choices*"}
                      ]},
        "breakthrough": {"text": "Mime Lady: *mimes that her crippling social anxiety has better performance art value than most people's personalities*",
                        "choices": [
                            {"text": "Right", "next": None, "effects": {"absurdity": -2, "breakthrough": True}, "reply": "*mimes that at least her psychological damage is aesthetically pleasing*"},
                            {"text": "Try talking", "next": None, "effects": {"absurdity": -1}, "reply": "Words are just noise but miming is pure emotional truth also I can't afford real therapy"}
                        ]},
        "nervous": {"text": "Mime Lady: *mimes that her vocal cords died of neglect but her depression is still very much alive and thriving*",
                  "choices": [
                      {"text": "That's rough", "next": "opening", "effects": {"absurdity": -1}, "reply": "*mimes that emotional pain builds character and also excellent upper body strength*"},
                      {"text": "What triggers it", "next": "anxious", "effects": None, "reply": "*mimes the crushing weight of human interaction and also rent payments*"}
                  ]},
        "defensive": {"text": "Mime Lady: *mimes building a wall but it's clearly made of her own insecurities and daddy issues*",
                   "choices": [
                       {"text": "Whatever", "next": "comfortable", "effects": {"absurdity": -1}, "reply": "*mimes that the wall is mostly to keep her own self-loathing contained*"},
                       {"text": "Take your time", "next": "comfortable", "effects": None, "reply": "*mimes that time is a social construct but trauma is forever*"}
                   ]},
        "opening": {"text": "Mime Lady: *mimes that her heart is in a display case like a museum exhibit called 'emotions that died in childhood'*",
                      "choices": [
                          {"text": "That's poetic", "next": None, "effects": {"absurdity": -1, "breakthrough": True}, "reply": "*mimes that maybe she could charge admission to her emotional trauma*"},
                          {"text": "Who gets you", "next": None, "effects": None, "reply": "*mimes her therapist but points out that you're getting paid to pretend to care*"}
                      ]},
        "anxious": {"text": "Mime Lady: *mimes that social anxiety is like being murdered by invisible people every time someone makes eye contact*",
                    "choices": [
                        {"text": "Try breathing exercises", "next": None, "effects": {"absurdity": -1}, "reply": "*mimes that breathing is overrated but dying from social interaction is underrated*"},
                        {"text": "Yeah people suck", "next": None, "effects": None, "reply": "*mimes vigorous agreement and also that you're surprisingly honest for a therapist*"}
                    ]}

    }
    clients.append({"id": "mime", "name": "Mime Lady", "nodes": mime_nodes, "absurdity": 5, "resistance": 5})

    # Corporate CEO (Business Guy)
    business_nodes = {
        "start": {"text": "Business Guy: \"I laid off three hundred people last month and my therapist says I have quote unquote emotional baggage but honestly I sleep fine on my pile of money\"",
                  "choices": [
                      {"text": "How does that make you feel", "next": "nostalgia", "effects": {"absurdity": -1}, "reply": "Rich mostly though sometimes I wake up screaming but that might be unrelated"},
                      {"text": "Do you feel guilty", "next": "defensive", "effects": None, "reply": "Guilt is just inefficient resource allocation according to my business model"},
                      {"text": "What about their families", "next": "laugh", "effects": {"absurdity": -1}, "reply": "They should have thought about that before choosing to be poor and expendable"}
                  ]},
        "nostalgia": {"text": "Business Guy: \"When I was seven I wanted to help people but then I realized people don't generate quarterly profits so I pivoted to crushing dreams instead\"",
                      "choices": [
                          {"text": "Uh huh", "next": None, "effects": {"absurdity": -1}, "reply": "Yeah turns out human suffering is a renewable resource with excellent ROI"},
                          {"text": "That's dark", "next": None, "effects": None, "reply": "Dark is just another word for realistic market analysis"}
                      ]},
        "defensive": {"text": "Business Guy: \"I tried to monetize my midlife crisis but turns out existential dread has terrible market penetration\"",
                      "choices": [
                          {"text": "What about happiness", "next": "confused", "effects": None, "reply": "Happiness is just a luxury good that poor people think they deserve for some reason"},
                          {"text": "Maybe try meditation", "next": None, "effects": {"absurdity": -1}, "reply": "I meditate on profit margins does that count"}
                      ]},
        "laugh": {"text": "Business Guy: \"I fired my son's little league coach because his win-loss ratio was negatively impacting my quarterly emotional investments\"",
                  "choices": [
                      {"text": "That's insane", "next": None, "effects": None, "reply": "Insane is just another word for innovative market disruption"},
                      {"text": "How's your son", "next": None, "effects": {"absurdity": -1}, "reply": "He's generating excellent character-building losses which should pay dividends later"}
                  ]},
        "confused": {"text": "Business Guy: \"Sometimes I think about all the lives I've ruined and I get this weird feeling but then I remember it's just indigestion from eating caviar off of eviction notices\"",
                    "choices": [
                        {"text": "That feeling has a name", "next": None, "effects": {"absurdity": -1, "breakthrough": True}, "reply": "Yeah it's called being successful but sometimes success tastes like other people's tears"},
                        {"text": "Whatever", "next": None, "effects": None, "reply": "Right like why would I care about poor people when I could buy more yachts instead"}
                    ]}
    }
    clients.append({"id": "business", "name": "Business Guy", "nodes": business_nodes, "absurdity": 6, "resistance": 6})

    # Cult Survivor
    cult_nodes = {
        "start": {"text": "Weird Cult Person: \"I escaped a death cult but honestly my regular life is way more likely to kill me so I'm thinking about going back\"",
                  "choices": [
                      {"text": "That's concerning", "next": "haunted", "effects": None, "reply": "Yeah but at least the cult had free meals and a sense of community unlike my soul-crushing minimum wage job"},
                      {"text": "What's your life like now", "next": "cats", "effects": {"absurdity": -1}, "reply": "I work retail and live alone with cats who judge me harder than any cult leader ever did"},
                      {"text": "Maybe try therapy", "next": "grounded", "effects": {"absurdity": -1}, "reply": "You mean like right now with you because this is already more depressing than ritual sacrifice"}
                  ]},
        "haunted": {"text": "Weird Cult Person: \"The cult promised eternal damnation but my student loans already delivered that for a much higher price\"",
                    "choices": [
                        {"text": "How much do you owe", "next": None, "effects": {"absurdity": -1}, "reply": "Enough that death seems like a reasonable payment plan at this point"},
                        {"text": "That's dark", "next": None, "effects": None, "reply": "Dark is just capitalism without the pretty marketing but at least cults are honest about wanting your soul"}
                    ]},
        "cats": {"text": "Weird Cult Person: \"My cats watch me cry every morning and I swear they're taking notes for some kind of feline psychological study\"",
                 "choices": [
                     {"text": "What do they conclude", "next": None, "effects": {"absurdity": -1, "breakthrough": True}, "reply": "That I'm a disappointment to the entire species and should probably just become cat food to complete the circle of failure"},
                     {"text": "Maybe get a dog", "next": None, "effects": None, "reply": "Dogs are too optimistic I need pets that understand that life is meaningless suffering"}
                 ]},
        "grounded": {"text": "Weird Cult Person: \"At least when the cult wanted to sacrifice me it was for a higher purpose but now I'm just slowly dying for capitalism\"",
                     "choices": [
                         {"text": "That's one way to see it", "next": None, "effects": {"absurdity": -1}, "reply": "Yeah at least cult death has meaning but wage slavery is just death with extra steps and no cool robes"},
                         {"text": "You seem tired", "next": None, "effects": None, "reply": "Tired is just another word for spiritually bankrupt but with less community support"}
                     ]}
    }
    clients.append({"id": "cult", "name": "Weird Cult Person", "nodes": cult_nodes, "absurdity": 7, "resistance": 5})

    # Delusional Choir
    choir_nodes = {
        "start": {"text": "Office Supply Choir: \"I started a death metal band with office supplies because my coworkers have the emotional range of a stapler so I figured why not make it literal\"",
                  "choices": [
                      {"text": "Cool", "next": "harmony", "effects": {"absurdity": -1}, "reply": "Yeah the paper shredder does excellent vocals about the meaninglessness of corporate existence"},
                      {"text": "What do they sing about", "next": "tiles", "effects": None, "reply": "Mostly about how we're all slowly dying in fluorescent hell while pretending productivity has meaning"},
                      {"text": "Do you get paid extra", "next": "stapler", "effects": None, "reply": "No but at least when the hole punch screams about workplace depression it's more honest than HR"}
                  ]},
        "harmony": {"text": "Office Supply Choir: \"The printer joined our band but it only screams about paper jams which is basically my internal monologue anyway\"",
                    "choices": [
                        {"text": "That sounds accurate", "next": None, "effects": {"absurdity": -1}, "reply": "Right like finally something that understands that everything is broken and nothing works correctly"},
                        {"text": "What's your favorite song", "next": None, "effects": None, "reply": "We do a cover of Sound of Silence but it's just the copy machine having an existential crisis"}
                    ]},
        "tiles": {"text": "Office Supply Choir: \"The ceiling tiles write better lyrics about corporate despair than most actual musicians who've never experienced the slow death of office life\"",
                  "choices": [
                      {"text": "What do they say", "next": None, "effects": None, "reply": "Mostly variations on how we're all trapped under artificial light waiting to die while making rich people richer"},
                      {"text": "Tiles don't write lyrics", "next": None, "effects": {"absurdity": -1, "breakthrough": True}, "reply": "Neither do most pop stars but at least my ceiling tiles have experienced real suffering"}
                  ]},
        "stapler": {"text": "Office Supply Choir: \"The stapler keeps a steady beat that matches my heart rate during panic attacks so it's basically my emotional support percussion instrument\"",
                    "choices": [
                        {"text": "That's oddly touching", "next": None, "effects": {"absurdity": -1}, "reply": "Yeah at least my mental breakdown has good rhythm unlike everything else in my life"},
                        {"text": "Do you have panic attacks often", "next": None, "effects": None, "reply": "Only every day but who's counting besides the stapler apparently"}
                    ]}
    }
    clients.append({"id": "choir", "name": "Office Supply Choir", "nodes": choir_nodes, "absurdity": 8, "resistance": 6})

    # Aspiring Influencer
    influencer_nodes = {
        "start": {"text": "Wannabe Influencer: \"I have three followers on TikTok and one of them is my mom's alt account but I still think I'm gonna be famous for eating cereal dramatically\"",
                  "choices": [
                      {"text": "That's ambitious", "next": "delusion", "effects": None, "reply": "Yeah my personal brand is 'millennial breakdown with good lighting' and it's gonna revolutionize mental health content"},
                      {"text": "How's that working out", "next": "reality", "effects": {"absurdity": -1}, "reply": "Well I've monetized my anxiety attacks but turns out the return on investment for public emotional collapse is surprisingly low"},
                      {"text": "Maybe focus on therapy first", "next": "defensive", "effects": {"absurdity": -1}, "reply": "Therapy doesn't get views like my daily crisis content does plus you don't even have ring lights"}
                  ]},
        "delusion": {"text": "Wannabe Influencer: \"I'm gonna start a podcast about my trust issues called 'Red Flags and Ring Lights' where I interview my ex-boyfriends about why they're trash\"",
                     "choices": [
                         {"text": "Interesting concept", "next": None, "effects": None, "reply": "Right like finally someone's gonna expose how dating is just emotional terrorism with worse special effects than my TikToks"},
                         {"text": "Would they agree to that", "next": None, "effects": {"absurdity": -1}, "reply": "They'll do anything for clout even if it means admitting they're human garbage on my platform"}
                     ]},
        "reality": {"text": "Wannabe Influencer: \"My biggest video got twelve views and half of them were me checking if it uploaded correctly but at least my breakdown content is consistent\"",
                    "choices": [
                        {"text": "Quality over quantity", "next": None, "effects": {"absurdity": -1, "breakthrough": True}, "reply": "You're right my mental health crisis content really captures the authentic desperation of my generation"},
                        {"text": "Maybe try a different approach", "next": None, "effects": None, "reply": "Different how like actually being interesting instead of just documenting my slow descent into irrelevance"}
                    ]},
        "defensive": {"text": "Wannabe Influencer: \"At least when I have a public mental breakdown online people can double-tap to show they care unlike real therapy where you just sit there judging me\"",
                      "choices": [
                          {"text": "I'm not judging", "next": None, "effects": {"absurdity": -1}, "reply": "You're literally getting paid to listen to my problems while my followers do it for free because they love the authentic trauma content"},
                          {"text": "Social media isn't real connection", "next": None, "effects": None, "reply": "Neither is therapy but at least online I can filter my depression with better lighting"}
                      ]}
    }
    clients.append({"id": "influencer", "name": "Wannabe Influencer", "nodes": influencer_nodes, "absurdity": 7, "resistance": 5})

    # Conspiracy Theorist
    conspiracy_nodes = {
        "start": {"text": "Conspiracy Guy: \"The government is putting sadness chemicals in the water supply which explains why I've been depressed since I moved next to that Starbucks\"",
                  "choices": [
                      {"text": "That's... one theory", "next": "deeper", "effects": None, "reply": "It's not a theory it's documented fact that corporate coffee chains are psychological warfare against independent thought"},
                      {"text": "What makes you think that", "next": "evidence", "effects": {"absurdity": -1}, "reply": "Ever notice how you feel empty inside after buying overpriced lattes that's not coincidence that's capitalism"},
                      {"text": "Maybe you're just stressed", "next": "defensive", "effects": {"absurdity": -1}, "reply": "Stressed is what they want you to call it when you're actually experiencing systematic oppression through beverage manipulation"}
                  ]},
        "deeper": {"text": "Conspiracy Guy: \"My therapist before you was obviously a government plant because she kept suggesting I try medication instead of researching fluoride mind control\"",
                   "choices": [
                       {"text": "What did you research", "next": None, "effects": None, "reply": "Turns out Big Pharma and Big Dental are basically the same company trying to make us compliant through chemical dependency"},
                       {"text": "How did that make you feel", "next": None, "effects": {"absurdity": -1}, "reply": "Validated that my paranoia is actually just pattern recognition but also disappointed that even therapy is compromised"}
                   ]},
        "evidence": {"text": "Conspiracy Guy: \"I have a spreadsheet tracking my mood versus proximity to corporate establishments and the correlation is undeniable proof of psychological manipulation\"",
                     "choices": [
                         {"text": "Show me the data", "next": None, "effects": {"absurdity": -1, "breakthrough": True}, "reply": "See this is why I like you most therapists don't appreciate good research methodology even when it exposes the truth"},
                         {"text": "Correlation isn't causation", "next": None, "effects": None, "reply": "That's exactly what someone who's been compromised by the mental health industrial complex would say"}
                     ]},
        "defensive": {"text": "Conspiracy Guy: \"You probably think I'm crazy but crazy is just what they call people who notice that everything is designed to make us miserable for profit\"",
                      "choices": [
                          {"text": "You're not crazy", "next": None, "effects": {"absurdity": -1}, "reply": "Finally someone who understands that questioning authority is actually mental health but they don't teach that in therapist school"},
                          {"text": "That sounds exhausting", "next": None, "effects": None, "reply": "Being awake to the truth is exhausting but ignorance is just comfortable slavery to corporate overlords"}
                      ]}
    }
    clients.append({"id": "conspiracy", "name": "Conspiracy Guy", "nodes": conspiracy_nodes, "absurdity": 6, "resistance": 7})

    # Failed Artist
    artist_nodes = {
        "start": {"text": "Failed Artist: \"I spent four years getting an art degree in Vienna just to learn that my parents were right about it being useless but at least my student debt has artistic value\"",
                  "choices": [
                      {"text": "Have you considered other careers", "next": "defensive", "effects": {"absurdity": -1}, "reply": "You mean selling out like everyone else who gave up on beauty just to afford basic human needs"}
                  ]},
        "defensive": {"text": "Failed Artist: \"I'd rather be a starving artist than a well-fed corporate slave but turns out you can be both broke and selling out if you're bad enough at art\"",
                      "choices": [
                          {"text": "That's rough", "next": None, "effects": {"absurdity": -1}, "reply": "Yeah I'm living proof that following your dreams is just expensive self-destruction with worse health insurance - my grandfather always said I should have gone into politics instead"},
                          {"text": "Maybe redefine success", "next": None, "effects": None, "reply": "Success is just what people call giving up on your values but with better marketing and dental coverage"}
                      ]}
    }
    clients.append({"id": "artist", "name": "Failed Artist", "nodes": artist_nodes, "absurdity": 6, "resistance": 5})

    # Anxious Parent
    parent_nodes = {
        "start": {"text": "Anxious Parent: \"I googled 'how to raise kids without traumatizing them' and got seventeen thousand conflicting articles so now I'm pretty sure I've already ruined everything\"",
                  "choices": [
                      {"text": "Parenting is hard", "next": "worry", "effects": {"absurdity": -1}, "reply": "Hard is an understatement it's like being responsible for not screwing up an entire human being while you're barely keeping yourself together"},
                      {"text": "What's your biggest fear", "next": "future", "effects": None, "reply": "That my kid will need therapy because of me and then their therapist will judge my parenting like you're probably doing right now"},
                      {"text": "Google isn't always helpful", "next": "research", "effects": {"absurdity": -1}, "reply": "Yeah but at least Dr Google doesn't charge me two hundred dollars to tell me I'm doing everything wrong"}
                  ]},
        "worry": {"text": "Anxious Parent: \"I bought seventeen parenting books and they all contradict each other so basically I'm just winging it and hoping my kid doesn't become a serial killer\"",
                  "choices": [
                      {"text": "Most kids turn out fine", "next": None, "effects": {"absurdity": -1}, "reply": "Define fine because if fine means functionally dysfunctional like the rest of us then sure I'm nailing it"},
                      {"text": "Trust your instincts", "next": None, "effects": None, "reply": "My instincts tell me to hide in the closet and eat ice cream so maybe not the best parenting strategy"}
                  ]},
        "future": {"text": "Anxious Parent: \"I lie awake at night wondering if I'm raising a future therapy patient or just creating someone who'll have really interesting stories for their therapist\"",
                   "choices": [
                       {"text": "Everyone needs therapy", "next": None, "effects": {"absurdity": -1, "breakthrough": True}, "reply": "That's weirdly comforting like at least I'm giving my kid job security in the mental health industry"},
                       {"text": "You care and that matters", "next": None, "effects": None, "reply": "Caring is just anxiety with good PR but I guess it's better than not giving a damn like my parents did"}
                   ]},
        "research": {"text": "Anxious Parent: \"According to the internet I should be a helicopter parent a free-range parent and a gentle parent simultaneously while also working full-time and maintaining my mental health\"",
                     "choices": [
                         {"text": "That's impossible", "next": None, "effects": {"absurdity": -1}, "reply": "Right like the internet expects me to be perfect at something that comes with no instruction manual and permanent consequences"},
                         {"text": "Just do your best", "next": None, "effects": None, "reply": "My best changes daily depending on how much coffee I've had and whether my kid decided to be a tiny terrorist today"}
                     ]}
    }
    clients.append({"id": "parent", "name": "Anxious Parent", "nodes": parent_nodes, "absurdity": 5, "resistance": 4})

    return clients

# ---------------------------
# Helper utility
# ---------------------------

def safe_int(v, default=0):
    try:
        return int(v)
    except:
        return default

# ---------------------------
# Main application class
# ---------------------------

class TherapyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Therapy Simulator 1987 — GUI")
        self.geometry("980x740")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_quit)

        # Game state variables
        self.player = None
        self.clients_data = build_clients_data()
        self.current_client_index = 0
        self.current_node = "start"
        self.log_lines = []
        self.type_speed = TYPE_SPEED_DEFAULT

        # UI layout
        self.create_widgets()
        self.show_intro()

        # For typewriter effect
        self._typewriter_text = ""
        self._typewriter_index = 0

    # ---------------------------
    # UI building
    # ---------------------------
    def create_widgets(self):
        # Top banner
        banner = tk.Frame(self, bg="#111827", height=56)
        banner.pack(fill=tk.X)
        tk.Label(banner, text="THERAPY SIMULATOR 1987", bg="#111827", fg="white", font=("Helvetica", 16, "bold")).pack(side=tk.LEFT, padx=12, pady=8)

        # Main frame
        main = tk.Frame(self, bg="#f3f4f6")
        main.pack(fill=tk.BOTH, expand=True)

        # Left pane: client area and choices
        left = tk.Frame(main, bg="#f9fafb", padx=10, pady=10)
        left.place(x=10, y=66, width=640, height=660)

        self.client_title = tk.Label(left, text="No client", font=("Helvetica", 14, "bold"), bg="#f9fafb")
        self.client_title.pack(anchor="w")

        self.client_text = tk.Text(left, height=6, wrap=tk.WORD, bg="#ffffff", font=("Helvetica", 11), state=tk.DISABLED)
        self.client_text.pack(fill=tk.X, pady=(6, 4))

        # choices frame
        self.choices_frame = tk.Frame(left, bg="#f9fafb")
        self.choices_frame.pack(fill=tk.BOTH, expand=True, pady=(6,4))

        # quick action buttons
        quick_frame = tk.Frame(left, bg="#f9fafb")
        quick_frame.pack(fill=tk.X, pady=(4,0))
        tk.Button(quick_frame, text="Use Item", command=self.on_use_item).pack(side=tk.LEFT, padx=2)
        tk.Button(quick_frame, text="Show Stats", command=self.on_show_stats).pack(side=tk.LEFT, padx=2)
        tk.Button(quick_frame, text="Check Progress", command=self.on_check_progress).pack(side=tk.LEFT, padx=2)
        tk.Button(quick_frame, text="End Day Early", command=self.on_end_day).pack(side=tk.RIGHT, padx=2)

        # Right pane: stats, inventory, log
        right = tk.Frame(main, bg="#fff", padx=10, pady=10)
        right.place(x=660, y=66, width=310, height=660)

        # Stats panel
        stats_label = tk.Label(right, text="Therapist Stats", font=("Helvetica", 12, "bold"), bg="#fff")
        stats_label.pack(anchor="w")
        self.stats_text = tk.Text(right, height=8, wrap=tk.WORD, bg="#f8fafc", state=tk.DISABLED)
        self.stats_text.pack(fill=tk.X, pady=(6,8))

        # Inventory
        inv_label = tk.Label(right, text="Inventory", font=("Helvetica", 12, "bold"), bg="#fff")
        inv_label.pack(anchor="w")
        self.inv_frame = tk.Frame(right, bg="#fff")
        self.inv_frame.pack(fill=tk.X, pady=(6,8))

        # Session log
        log_label = tk.Label(right, text="Session Log", font=("Helvetica", 12, "bold"), bg="#fff")
        log_label.pack(anchor="w")
        self.log_text = tk.Text(right, height=12, wrap=tk.WORD, bg="#f3f4f6", state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=(6,0))

        # Bottom controls: typewriter speed and stage selection
        bottom = tk.Frame(self, bg="#e5e7eb", height=44)
        bottom.pack(fill=tk.X, side=tk.BOTTOM)
        tk.Label(bottom, text="Typewriter speed:", bg="#e5e7eb").pack(side=tk.LEFT, padx=8)
        self.speed_slider = tk.Scale(bottom, from_=2, to=20, orient=tk.HORIZONTAL, bg="#e5e7eb", command=self.on_speed_change)
        self.speed_slider.set(TYPE_SPEED_DEFAULT)
        self.speed_slider.pack(side=tk.LEFT, padx=4)
        
        # Debate button
        tk.Button(bottom, text="Debate Client", command=self.open_debate_modal, bg="#d1d5db").pack(side=tk.LEFT, padx=8)
        
        # Stage selection button
        tk.Button(bottom, text="View Progress", command=self.show_stage_selection, bg="#d1d5db").pack(side=tk.RIGHT, padx=8)

    # ---------------------------
    # Intro and character creation
    # ---------------------------
    def show_intro(self):
        # Pop up a dialog to ask for name and class selection
        win = tk.Toplevel(self)
        win.transient(self)
        win.grab_set()
        win.title("New Day — Character Creation")
        win.geometry("600x380")
        tk.Label(win, text="THERAPY SIMULATOR 1987", font=("Helvetica", 14, "bold")).pack(pady=8)
        tk.Label(win, text="Enter your therapist name (press Enter for Dr. Finch):").pack()
        name_entry = tk.Entry(win, width=40)
        name_entry.pack(pady=6)
        name_entry.insert(0, "Dr. Finch")

        tk.Label(win, text="Choose your class (each affects game):").pack(pady=(12,4))
        cls_var = tk.StringVar(value="Empath")
        # radio buttons for classes
        for k, v in CLASS_TEMPLATES.items():
            rb = tk.Radiobutton(win, text=f"{k}: {v['desc']}", variable=cls_var, value=k)
            rb.pack(anchor="w", padx=20)

        def on_start():
            name = name_entry.get().strip() or "Dr. Finch"
            cls = cls_var.get()
            self.start_game(name, cls)
            win.destroy()

        tk.Button(win, text="Begin Day", command=on_start).pack(pady=12)
        win.protocol("WM_DELETE_WINDOW", self.on_quit)

    def start_game(self, name, cls):
        # initialize player
        base = CLASS_TEMPLATES[cls]["base"]
        self.player = {
            "name": name,
            "class": cls,
            "ability": CLASS_TEMPLATES[cls]["ability"],
            "stats": {"Patience": base["Patience"], "Empathy": base["Empathy"], "Insight": base["Insight"], "Composure": base["Composure"]},
            "inventory": {k: ITEMS[k]["uses"] for k in ITEMS},
            "xp": 0,
            "reputation": 10,
            "current_stage_index": 0,
            "clients_completed": 0,
            "flags": {"big_breakthroughs": 0, "melted_down": False, "joined_delusion": False}
        }
        # starter tweaks
        self.player["inventory"]["Coffee"] = 2
        self.player["inventory"]["Notepad"] = 1
        self.player["inventory"]["Meditation Guide"] = 1
        self.player["inventory"]["Energy Drink"] = 1

        # reset clients based on current stage
        self.clients = []
        current_stage_data = THERAPY_STAGES[self.player["current_stage_index"]]
        available_client_ids = current_stage_data["clients"]
        
        for c in self.clients_data:
            if c["id"] in available_client_ids:
                try:
                    # deep copy structure with mutable state
                    nodes_copy = {}
                    for nid, ndata in c["nodes"].items():
                        nodes_copy[nid] = {"text": ndata["text"], "choices": [dict(ch) for ch in ndata["choices"]]}
                    
                    # Apply location difficulty modifiers
                    location_effects = current_stage_data.get("location_effects", {})
                    modified_absurdity = c["absurdity"] + location_effects.get("difficulty_modifier", 0)
                    modified_resistance = c["resistance"] + location_effects.get("difficulty_modifier", 0)
                    
                    self.clients.append({"id": c["id"], "name": c["name"], "nodes": nodes_copy, 
                                       "absurdity": max(1, modified_absurdity), 
                                       "resistance": max(1, modified_resistance), 
                                       "node": "start"})
                except (KeyError, TypeError) as e:
                    self.append_log(f"Warning: Could not load client {c.get('id', 'unknown')}: {str(e)}")
        self.current_client_index = 0
        self.log_lines = []
        current_stage = THERAPY_STAGES[self.player["current_stage_index"]]
        self.append_log(f"Day start. Therapist: {self.player['name']} ({self.player['class']}) at {current_stage['name']}")
        self.render_stats()
        self.load_current_client()

    def append_log(self, s):
        self.log_lines.append(s)
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, s + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    # ---------------------------
    # Client flow
    # ---------------------------
    def load_current_client(self):
        try:
            if not self.clients or self.current_client_index >= len(self.clients):
                self.append_log("No more clients available in this location.")
                self.end_day()
                return
            self.current_client = self.clients[self.current_client_index]
            self.current_client["node"] = self.current_client.get("node", "start")
            self.client_title.configure(text=self.current_client["name"])
            self.display_client_node(self.current_client["node"])
        except Exception as e:
            self.append_log(f"Error loading client: Something went wrong")
            messagebox.showerror("Game Error", "Failed to load client. Ending session.")
            self.end_day()

    def display_client_node(self, node_key):
        try:
            if node_key not in self.current_client["nodes"]:
                self.append_log(f"Error: Invalid dialogue node '{node_key}'. Ending session.")
                self.end_day()
                return
                
            node = self.current_client["nodes"][node_key]
            self.clear_choices()
            # Typewriter the node text
            self.typewriter_write(node["text"])
            # After typing finishes, render choices
            delay_ms = max(300, len(node["text"]) * self.type_speed + 200)
            self.after(delay_ms, lambda: self.render_choices(node))
        except Exception as e:
            self.append_log("Error displaying client dialogue. Session terminated.")
            messagebox.showerror("Game Error", "Dialogue system error occurred.")
            self.end_day()

    def clear_choices(self):
        # Clear all choice buttons and ensure they can't be pressed
        try:
            for widget in self.choices_frame.winfo_children():
                try:
                    widget.destroy()
                except tk.TclError:
                    pass  # Widget already destroyed
            self.choices_frame.update_idletasks()
        except tk.TclError:
            pass  # Frame might be destroyed

    def render_choices(self, node):
        self.clear_choices()
        # Add a flag to prevent multiple rapid clicks
        self.choice_in_progress = getattr(self, 'choice_in_progress', False)
        if self.choice_in_progress:
            return
            
        # buttons for each choice - no hints or predictions
        for idx, ch in enumerate(node["choices"], start=1):
            choice_text = ch['text']
            
            btn = tk.Button(self.choices_frame, text=f"{idx}. {choice_text}", anchor="w", justify=tk.LEFT, wraplength=580,
                            command=lambda c=ch: self.on_choose_safe(c))
            btn.pack(fill=tk.X, pady=3)

    def on_choose_safe(self, choice):
        # Prevent multiple rapid clicks
        if getattr(self, 'choice_in_progress', False):
            return
        self.choice_in_progress = True
        self.on_choose(choice)

    def on_choose(self, choice):
        # Hide buttons immediately when choice is made
        self.clear_choices()
        
        # Get current location effects
        current_stage = THERAPY_STAGES[self.player["current_stage_index"]]
        location_effects = current_stage.get("location_effects", {})
        
        # Apply meaningful stat changes based on choice type and content with success rates
        choice_text = choice.get("text", "").lower()
        stat_changes = []
        
        # Empathetic responses
        if any(word in choice_text for word in ["listen", "validate", "understand", "care", "feel", "sorry", "support"]):
            old_emp = self.player["stats"]["Empathy"]
            self.player["stats"]["Empathy"] = min(15, self.player["stats"]["Empathy"] + 1)
            if self.player["stats"]["Empathy"] > old_emp:
                stat_changes.append("Empathy +1")
            
            # Stat-based success calculation
            empathy_effectiveness = max(1, self.player["stats"]["Empathy"] - 3)  # Higher empathy = better results
            base_reduction = 1
            total_reduction = base_reduction + (empathy_effectiveness // 2)
            
            self.current_client["absurdity"] = max(0, self.current_client["absurdity"] - total_reduction)
            if total_reduction > base_reduction:
                stat_changes.append(f"High Empathy: Extra effective (-{total_reduction} absurdity)")
            else:
                stat_changes.append(f"Empathy effect (-{total_reduction} absurdity)")
            
            # Apply location-specific empathy bonus
            if location_effects.get("empathy_bonus", 0) > 0:
                self.current_client["absurdity"] = max(0, self.current_client["absurdity"] - location_effects["empathy_bonus"])
                stat_changes.append(f"Location Bonus (-{location_effects['empathy_bonus']} absurdity)")
            
            # Empathy can drain composure sometimes
            if "overwhelming" in choice_text or self.current_client["absurdity"] > 6:
                old_comp = self.player["stats"]["Composure"]
                self.player["stats"]["Composure"] = max(1, self.player["stats"]["Composure"] - 1)
                if self.player["stats"]["Composure"] < old_comp:
                    stat_changes.append("Composure -1")
        
        # Analytical/probing responses  
        elif any(word in choice_text for word in ["ask", "explore", "why", "what", "how", "analyze", "think", "explain"]):
            old_ins = self.player["stats"]["Insight"]
            self.player["stats"]["Insight"] = min(15, self.player["stats"]["Insight"] + 1)
            if self.player["stats"]["Insight"] > old_ins:
                stat_changes.append("Insight +1")
            
            # Stat-based success calculation
            insight_effectiveness = max(1, self.player["stats"]["Insight"] - 3)
            base_reduction = 1
            total_reduction = base_reduction + (insight_effectiveness // 2)
            
            self.current_client["absurdity"] = max(0, self.current_client["absurdity"] - total_reduction)
            if total_reduction > base_reduction:
                stat_changes.append(f"High Insight: Breakthrough achieved (-{total_reduction} absurdity)")
            else:
                stat_changes.append(f"Insight effect (-{total_reduction} absurdity)")
            
            # Apply location-specific insight bonus
            if location_effects.get("insight_bonus", 0) > 0:
                self.current_client["absurdity"] = max(0, self.current_client["absurdity"] - location_effects["insight_bonus"])
                stat_changes.append(f"Location Bonus (-{location_effects['insight_bonus']} absurdity)")
            
            # Deep questions can be mentally taxing
            if self.current_client["resistance"] > 5:
                old_comp = self.player["stats"]["Composure"]
                self.player["stats"]["Composure"] = max(1, self.player["stats"]["Composure"] - 1)
                if self.player["stats"]["Composure"] < old_comp:
                    stat_changes.append("Composure -1")
        
        # Challenging/confrontational responses
        elif any(word in choice_text for word in ["challenge", "wrong", "stupid", "ridiculous", "stop", "enough", "reality"]):
            old_pat = self.player["stats"]["Patience"]
            self.player["stats"]["Patience"] = max(1, self.player["stats"]["Patience"] - 2)
            if self.player["stats"]["Patience"] < old_pat:
                stat_changes.append("Patience -2")
            old_comp = self.player["stats"]["Composure"]
            self.player["stats"]["Composure"] = max(1, self.player["stats"]["Composure"] - 1)
            if self.player["stats"]["Composure"] < old_comp:
                stat_changes.append("Composure -1")
        
        # Patient/waiting responses
        elif any(word in choice_text for word in ["wait", "time", "patient", "slow", "breathe", "calm", "okay", "mm-hmm"]):
            old_pat = self.player["stats"]["Patience"]
            self.player["stats"]["Patience"] = min(15, self.player["stats"]["Patience"] + 1)
            if self.player["stats"]["Patience"] > old_pat:
                stat_changes.append("Patience +1")
            
            # Stat-based success calculation
            patience_effectiveness = max(1, self.player["stats"]["Patience"] - 3)
            base_reduction = 1
            total_reduction = base_reduction + (patience_effectiveness // 2)
            
            self.current_client["absurdity"] = max(0, self.current_client["absurdity"] - total_reduction)
            if total_reduction > base_reduction:
                stat_changes.append(f"High Patience: Client calms down (-{total_reduction} absurdity)")
            else:
                stat_changes.append(f"Patience effect (-{total_reduction} absurdity)")
            
            # Apply location-specific patience bonus
            if location_effects.get("patience_bonus", 0) > 0:
                absurdity_reduction = location_effects["patience_bonus"]
                self.current_client["absurdity"] = max(0, self.current_client["absurdity"] - absurdity_reduction)
                stat_changes.append(f"Location Bonus (-{absurdity_reduction} absurdity)")
            
            # High patience restores composure
            if self.player["stats"]["Patience"] >= 8:
                old_comp = self.player["stats"]["Composure"]
                self.player["stats"]["Composure"] = min(15, self.player["stats"]["Composure"] + 1)
                if self.player["stats"]["Composure"] > old_comp:
                    stat_changes.append("Composure +1")
        
        # Dismissive/sarcastic responses
        elif any(word in choice_text for word in ["whatever", "sure", "right", "cool story", "interesting"]):
            old_comp = self.player["stats"]["Composure"]
            self.player["stats"]["Composure"] = min(15, self.player["stats"]["Composure"] + 1)
            if self.player["stats"]["Composure"] > old_comp:
                stat_changes.append("Composure +1")
            
            # Stat-based success calculation - composure helps with detachment
            composure_effectiveness = max(1, self.player["stats"]["Composure"] - 4)  # Slightly harder
            base_reduction = 1
            total_reduction = base_reduction + (composure_effectiveness // 3)  # Less effective than other approaches
            
            self.current_client["absurdity"] = max(0, self.current_client["absurdity"] - total_reduction)
            if total_reduction > base_reduction:
                stat_changes.append(f"High Composure: Professional detachment (-{total_reduction} absurdity)")
            else:
                stat_changes.append(f"Composure effect (-{total_reduction} absurdity)")
            
            # Apply location-specific composure bonus
            if location_effects.get("composure_bonus", 0) > 0:
                absurdity_reduction = location_effects["composure_bonus"]
                self.current_client["absurdity"] = max(0, self.current_client["absurdity"] - absurdity_reduction)
                stat_changes.append(f"Location Bonus (-{absurdity_reduction} absurdity)")
            
            # But might reduce empathy
            old_emp = self.player["stats"]["Empathy"]
            self.player["stats"]["Empathy"] = max(1, self.player["stats"]["Empathy"] - 1)
            if self.player["stats"]["Empathy"] < old_emp:
                stat_changes.append("Empathy -1")
        
        # Check for stat-based complications (low stats cause problems)
        if self.player["stats"]["Composure"] <= 2:
            self.player["stats"]["Composure"] = max(1, self.player["stats"]["Composure"] - 1)
            self.current_client["absurdity"] = min(12, self.current_client["absurdity"] + 1)
            stat_changes.append("⚠️ Low Composure: You're barely holding it together (+1 client absurdity)")
            
        if self.player["stats"]["Patience"] <= 2:
            # Impatient responses backfire
            if any(word in choice_text for word in ["ask", "explore", "challenge", "what", "why"]):
                self.current_client["resistance"] = min(10, self.current_client["resistance"] + 1)
                stat_changes.append("⚠️ Low Patience: Your impatience shows (+1 client resistance)")
        
        # Apply stat changes immediately and show feedback
        if stat_changes:
            self.render_stats()
            self.append_log(f"Choice effect: {', '.join(stat_changes)}")
        
        # apply immediate reply override if present
        reply = choice.get("reply")
        if reply:
            # Clean up reply text - remove parentheses and format as client speech
            clean_reply = reply.strip("()")
            
            # Make response contextual to the choice made
            choice_made = choice.get("text", "")
            if "nod" in choice_made.lower():
                context_reply = f"*{clean_reply}*"
            elif "ask" in choice_made.lower():
                context_reply = f"{self.current_client['name']}: \"{clean_reply}\""
            elif "offer" in choice_made.lower() or "suggest" in choice_made.lower():
                context_reply = f"*{self.current_client['name']} reacts: {clean_reply}*"
            else:
                context_reply = f"{self.current_client['name']}: {clean_reply}"
                
            self.typewriter_write(context_reply)
            
            # Show continue button and wait for user to proceed
            self.show_continue_button(choice)
            return

        # If no reply, continue immediately with effects processing
        self.continue_after_choice(choice)

    def continue_after_choice(self, choice):
        """Continue processing choice after typewriter delay"""
        if not choice:
            return
            
        # apply effects dict if present (absurdity changes or start_debate)
        effects = choice.get("effects")
        if effects:
            # handle dict keys
            if isinstance(effects, dict):
                if "absurdity" in effects:
                    self.current_client["absurdity"] = max(0, self.current_client["absurdity"] + effects["absurdity"])
                if effects.get("start_debate"):
                    # start debate modal
                    self.append_log("Debate initiated by client escalation.")
                    self.open_debate_modal()
                    return
                    
                # Store effects for session completion
                if not hasattr(self.current_client, "effects"):
                    self.current_client["effects"] = {}
                for key, value in effects.items():
                    if key not in ["absurdity", "start_debate"]:
                        self.current_client["effects"][key] = value

        # move to next node or end
        next_node = choice.get("next")
        if next_node is None:
            # session ends - calculate completion rewards
            self.complete_session()
            # advance after shorter pause
            self.after(1000, lambda: self.advance_client_safe())
            return
        else:
            # set node and display
            self.current_client["node"] = next_node
            # Continue immediately to next node
            self.display_client_node_safe(next_node)
            # update stats viewer
            self.render_stats()
            
        # Clear pending choice
        self.pending_choice = None

    def show_continue_button(self, choice):
        """Show a continue button and wait for user to click it"""
        # Create a frame for the continue button
        continue_frame = tk.Frame(self.choices_frame, bg="#e8f4fd", relief=tk.RAISED, bd=1)
        continue_frame.pack(fill=tk.X, pady=15, padx=30)
        
        # Add a simple continue button
        continue_button = tk.Button(continue_frame, text="Continue →", 
                                   command=lambda: self.on_continue_button_clicked(choice),
                                   bg="#2563eb", fg="white", font=("Helvetica", 11, "bold"),
                                   padx=20, pady=8)
        continue_button.pack(pady=10)
        
        # Store reference to remove later
        self.continue_frame = continue_frame
        self.continue_button = continue_button

    def on_continue_button_clicked(self, choice):
        """Handle continue button click"""
        # Remove the continue button
        if hasattr(self, 'continue_frame'):
            try:
                self.continue_frame.destroy()
            except tk.TclError:
                pass
            delattr(self, 'continue_frame')
        if hasattr(self, 'continue_button'):
            delattr(self, 'continue_button')
        
        # Continue with choice processing
        self.continue_after_choice(choice)

    def advance_client_safe(self):
        self.choice_in_progress = False
        self.advance_client()
        
    def display_client_node_safe(self, node_key):
        self.choice_in_progress = False
        self.display_client_node(node_key)
    
    def complete_session(self):
        """Handle session completion rewards and effects"""
        self.append_log(f"Session with {self.current_client['name']} completed.")
        
        # Base XP reward
        base_xp = 3
        bonus_xp = 0
        
        # Track special session outcomes for endings
        effects = self.current_client.get("effects", {})
        
        # Check for breakthroughs (special flag in choices)
        if effects.get("breakthrough"):
            bonus_xp += 3
            self.player["reputation"] += 2
            self.append_log("MAJOR BREAKTHROUGH! This client will remember this session forever. +3 bonus XP, +2 reputation")
            self.player["flags"]["life_changing_breakthroughs"] = self.player["flags"].get("life_changing_breakthroughs", 0) + 1
        
        # Regular performance bonuses
        elif self.current_client["absurdity"] <= 2:
            bonus_xp += 2
            self.player["reputation"] += 1
            self.append_log("Breakthrough achieved! +2 bonus XP, +1 reputation")
            self.player["flags"]["big_breakthroughs"] = self.player["flags"].get("big_breakthroughs", 0) + 1
            
        elif self.current_client["absurdity"] <= 4:
            bonus_xp += 1
            self.append_log("Good progress made! +1 bonus XP")
        
        # Track controversial methods
        if effects.get("heated_argument"):
            self.player["flags"]["heated_arguments"] = self.player["flags"].get("heated_arguments", 0) + 1
            self.player["reputation"] -= 1
            self.append_log("Client left angry. Your methods are questionable. -1 reputation")
        
        # Track unconventional successes  
        if effects.get("joined_delusion"):
            self.player["flags"]["joined_delusions"] = self.player["flags"].get("joined_delusions", 0) + 1
            self.append_log("You've embraced the client's worldview. Reality is overrated anyway.")
            
        # Composure recovery for successful sessions
        if self.current_client["absurdity"] <= 3:
            composure_heal = 1
            old_composure = self.player["stats"]["Composure"]
            self.player["stats"]["Composure"] = min(15, self.player["stats"]["Composure"] + composure_heal)
            actual_heal = self.player["stats"]["Composure"] - old_composure
            if actual_heal > 0:
                self.append_log(f"Successful session restores {actual_heal} Composure.")
        
        # Award total XP
        total_xp = base_xp + bonus_xp
        self.player["xp"] += total_xp
        self.append_log(f"Gained {total_xp} XP total.")
        
        # Better chance to find items based on performance
        item_chance = 0.15 + (0.05 if self.current_client["absurdity"] <= 3 else 0)
        if random.random() < item_chance:
            found = random.choice(list(ITEMS.keys()))
            self.player["inventory"][found] = self.player["inventory"].get(found, 0) + 1
            self.append_log(f"You find {found} left behind by a grateful client.")
            
        # Check for stat increases every 5 XP
        if self.player["xp"] >= 5 and self.player["xp"] % 5 == 0:
            self.level_up()
            
        # Check for stage unlocks
        self.check_stage_unlocks()
            
        # No more passive XP benefits needed with simplified system
            
        self.render_stats()
    
    def level_up(self):
        """Handle stat increases when player gains enough XP"""
        # Simple stat boost based on class
        cls = self.player["class"]
        if cls == "Empath":
            self.player["stats"]["Insight"] = min(15, self.player["stats"]["Insight"] + 1)
            self.append_log("Level up! You understand human suffering even better now. Insight +1.")
        elif cls == "Counselor":
            self.player["stats"]["Empathy"] = min(15, self.player["stats"]["Empathy"] + 1)
            self.append_log("Level up! You got better at faking that you care. Empathy +1.")
        elif cls == "Burnout":
            self.player["stats"]["Patience"] = min(15, self.player["stats"]["Patience"] + 1)
            self.append_log("Level up! Another piece of your soul died. Patience +1.")
            
        # Small composure boost
        self.player["stats"]["Composure"] = min(15, self.player["stats"]["Composure"] + 1)
        self.append_log("Experience hardens you against hope. Composure +1.")
        
    def check_stage_unlocks(self):
        """Check if player has unlocked new therapy stages - now automatic with progression"""
        # With automatic progression, stages unlock when clients_needed threshold is met
        # This function is maintained for compatibility but no longer performs unlocking
        pass
                
    def show_stage_selection(self):
        """Show current location progress and automatic advancement info - READ ONLY"""
        if not self.player:
            messagebox.showwarning("No Player", "No active player session.")
            return
            
        # Show current location and progress
        current_stage = THERAPY_STAGES[self.player["current_stage_index"]]
        progress_msg = f"📍 Current Location: {current_stage['name']}\n"
        progress_msg += f"📋 Description: {current_stage['desc']}\n"
        progress_msg += f"👥 Clients completed here: {self.player['clients_completed']}/{current_stage['clients_needed']}\n\n"
        
        # Show location effects
        location_effects = current_stage.get("location_effects", {})
        if location_effects.get("description"):
            progress_msg += f"🎯 Location Effect: {location_effects['description']}\n\n"
        
        # Show progression info
        if self.player["current_stage_index"] < len(THERAPY_STAGES) - 1:
            next_stage = THERAPY_STAGES[self.player["current_stage_index"] + 1]
            remaining = current_stage['clients_needed'] - self.player['clients_completed']
            if remaining > 0:
                progress_msg += f"🏢 Next location: {next_stage['name']}\n"
                progress_msg += f"⏳ Complete {remaining} more clients to advance automatically."
            else:
                progress_msg += f"✅ Ready to advance to: {next_stage['name']}\n"
                progress_msg += "🚀 Complete current session to move forward!"
        else:
            progress_msg += "🏆 You are at the final location!\n"
            remaining = current_stage['clients_needed'] - self.player['clients_completed']
            if remaining > 0:
                progress_msg += f"Complete {remaining} more clients to finish your journey."
            else:
                progress_msg += "Complete current session to finish your therapeutic career!"
        
        # Show all unlocked locations
        progress_msg += f"\n\n📊 Career Progress:\n"
        for i, stage in enumerate(THERAPY_STAGES):
            if i < self.player["current_stage_index"]:
                progress_msg += f"✅ {stage['name']} - Completed\n"
            elif i == self.player["current_stage_index"]:
                progress_msg += f"🔄 {stage['name']} - Current ({self.player['clients_completed']}/{stage['clients_needed']})\n"
            else:
                progress_msg += f"🔒 {stage['name']} - Locked\n"
            
        messagebox.showinfo("Location Progress", progress_msg)

    def advance_client(self):
        self.current_client_index += 1
        self.player["clients_completed"] += 1
        
        # Check if we should advance to next stage
        current_stage_data = THERAPY_STAGES[self.player["current_stage_index"]]
        if self.player["clients_completed"] >= current_stage_data["clients_needed"]:
            # Time to advance to next stage
            if self.player["current_stage_index"] < len(THERAPY_STAGES) - 1:
                old_stage_data = current_stage_data
                self.player["current_stage_index"] += 1
                self.player["clients_completed"] = 0  # Reset for new stage
                new_stage_data = THERAPY_STAGES[self.player["current_stage_index"]]
                
                # Apply stage advancement bonuses
                bonus = new_stage_data.get("stage_bonus", {})
                bonus_text = []
                if "all_stats" in bonus:
                    for stat in self.player["stats"]:
                        self.player["stats"][stat] = min(15, self.player["stats"][stat] + bonus["all_stats"])
                    bonus_text.append(f"All stats +{bonus['all_stats']}")
                if "reputation" in bonus:
                    self.player["reputation"] += bonus["reputation"]
                    bonus_text.append(f"Reputation +{bonus['reputation']}")
                if "xp" in bonus:
                    self.player["xp"] += bonus["xp"]
                    bonus_text.append(f"XP +{bonus['xp']}")
                
                # Add special items for the new location
                location_effects = new_stage_data.get("location_effects", {})
                special_items = location_effects.get("special_items", [])
                items_added = []
                for item in special_items:
                    if item in ITEMS:
                        self.player["inventory"][item] = self.player["inventory"].get(item, 0) + 1
                        items_added.append(item)
                
                # Show location change popup
                bonus_msg = f"\n\nAdvancement Bonuses:\n{chr(10).join(bonus_text)}" if bonus_text else ""
                items_msg = f"\n\nLocation Equipment:\n{', '.join(items_added)}" if items_added else ""
                effect_msg = f"\n\nLocation Effect:\n{location_effects.get('description', '')}" if location_effects.get('description') else ""
                popup_msg = f"🏢 LOCATION CHANGE! 🏢\n\nYou've successfully completed:\n{old_stage_data['name']}\n\nMoving to your next assignment:\n{new_stage_data['name']}\n\n{new_stage_data['desc']}{bonus_msg}{items_msg}{effect_msg}"
                messagebox.showinfo("Location Change", popup_msg)
                
                self.append_log(f"Moving to {new_stage_data['name']}! {new_stage_data['desc']}")
                self.render_stats()  # Update stats display after bonuses
                
                # Load new clients for the new stage
                self.clients = []
                available_client_ids = new_stage_data["clients"]
                
                for c in self.clients_data:
                    if c["id"] in available_client_ids:
                        # deep copy structure with mutable state
                        nodes_copy = {}
                        for nid, ndata in c["nodes"].items():
                            nodes_copy[nid] = {"text": ndata["text"], "choices": [dict(ch) for ch in ndata["choices"]]}
                        
                        # Apply location difficulty modifiers
                        location_effects = new_stage_data.get("location_effects", {})
                        modified_absurdity = c["absurdity"] + location_effects.get("difficulty_modifier", 0)
                        modified_resistance = c["resistance"] + location_effects.get("difficulty_modifier", 0)
                        
                        self.clients.append({"id": c["id"], "name": c["name"], "nodes": nodes_copy, 
                                           "absurdity": max(1, modified_absurdity), 
                                           "resistance": max(1, modified_resistance), 
                                           "node": "start"})
                
                self.current_client_index = 0
                self.load_current_client()
                return
        
        if self.current_client_index >= len(self.clients):
            self.end_day()
            return
        self.load_current_client()

    # ---------------------------
    # Items & Stats
    # ---------------------------
    def on_use_item(self):
        if not self.player:
            messagebox.showwarning("No Player", "No active player session.")
            return
        
        # Check if player has any items
        available_items = {k: v for k, v in self.player["inventory"].items() if v > 0}
        if not available_items:
            messagebox.showinfo("No Items", "You have no items to use.")
            return
        # open small dialog with item buttons
        win = tk.Toplevel(self)
        win.transient(self)
        win.grab_set()
        win.title("Use Item")
        tk.Label(win, text="Choose an item to use:", font=("Helvetica", 10, "bold")).pack(pady=6)
        for it_name, it_info in ITEMS.items():
            count = self.player["inventory"].get(it_name, 0)
            btn_text = f"{it_name} (x{count}) - {it_info['desc']}"
            b = tk.Button(win, text=btn_text, wraplength=380, justify=tk.LEFT,
                          state=(tk.NORMAL if count > 0 else tk.DISABLED),
                          command=lambda n=it_name, w=win: (self.apply_item(n), w.destroy()))
            b.pack(fill=tk.X, padx=8, pady=4)
        tk.Button(win, text="Cancel", command=win.destroy).pack(pady=6)

    def apply_item(self, item_name):
        if not hasattr(self, 'current_client') or not self.current_client:
            messagebox.showinfo("No session", "No active therapy session.")
            return
        if self.player["inventory"].get(item_name, 0) <= 0:
            messagebox.showinfo("No item", "You don't have that item.")
            return
        
        self.player["inventory"][item_name] -= 1
        
        # Clear choices while using item
        self.clear_choices()
        
        # Get item info
        item_info = ITEMS[item_name]
        stat_to_restore = item_info["stat"]
        
        # Apply stat restoration
        old_val = self.player["stats"][stat_to_restore]
        self.player["stats"][stat_to_restore] = min(15, self.player["stats"][stat_to_restore] + 2)
        gain = self.player["stats"][stat_to_restore] - old_val
        
        if stat_to_restore == "Composure":
            self.typewriter_write("*You drink an energy drink. Your mental energy surges back.*")
        elif stat_to_restore == "Patience":
            self.typewriter_write("*You take a coffee break. Your patience for difficult clients returns.*")
        elif stat_to_restore == "Empathy":
            self.typewriter_write("*You review your notes on human psychology. Your empathy for clients deepens.*")
        elif stat_to_restore == "Insight":
            self.typewriter_write("*You study the meditation guide. Your insight into human nature grows.*")
            
        self.append_log(f"Used {item_name}: +{gain} {stat_to_restore} restored.")
        
        # Show updated stats and restore choices after delay
        self.render_stats()
        self.after(2000, lambda: self.render_choices(self.current_client["nodes"][self.current_client["node"]]))

    def render_stats(self):
        # update stats_text and inventory UI
        if not self.player:
            return
        s = self.player["stats"]
        
        # Update stats text - show the main stats with change indicators
        stats_lines = []
        stats_lines.append(f"Dr. {self.player['name']} — {self.player['class']}")
        stats_lines.append("")
        stats_lines.append(f"🧘 Patience: {s['Patience']}")
        stats_lines.append(f"💝 Empathy: {s['Empathy']}")
        stats_lines.append(f"🧠 Insight: {s['Insight']}")
        stats_lines.append(f"🎯 Composure: {s['Composure']}")
        stats_lines.append("")
        stats_lines.append(f"XP: {self.player['xp']}  Rep: {self.player['reputation']}")
        
        # Show current location info
        current_stage = THERAPY_STAGES[self.player["current_stage_index"]]
        stats_lines.append("")
        stats_lines.append(f"📍 {current_stage['name']}")
        
        # Show current client status if available
        if hasattr(self, 'current_client') and self.current_client:
            stats_lines.append(f"Client Absurdity: {self.current_client['absurdity']}")
        
        # Show active location effects
        location_effects = current_stage.get("location_effects", {})
        if location_effects:
            effects_active = []
            if location_effects.get("empathy_bonus", 0) > 0:
                effects_active.append("Empathy Enhanced")
            if location_effects.get("insight_bonus", 0) > 0:
                effects_active.append("Analysis Enhanced")
            if location_effects.get("patience_bonus", 0) > 0:
                effects_active.append("Patience Enhanced")
            if location_effects.get("composure_bonus", 0) > 0:
                effects_active.append("Detachment Enhanced")
            if location_effects.get("difficulty_modifier", 0) > 0:
                effects_active.append(f"+{location_effects['difficulty_modifier']} Difficulty")
            if effects_active:
                stats_lines.append("🎯 " + " | ".join(effects_active))
        
        self.stats_text.configure(state=tk.NORMAL)
        self.stats_text.delete("1.0", tk.END)
        self.stats_text.insert(tk.END, "\n".join(stats_lines))
        self.stats_text.configure(state=tk.DISABLED)
        
        # Update inventory with clickable buttons
        for widget in self.inv_frame.winfo_children():
            widget.destroy()
        
        for k, v in self.player["inventory"].items():
            if v > 0:
                btn_text = f"{k} (x{v}) - {ITEMS[k]['desc']}"
                btn = tk.Button(self.inv_frame, text=btn_text, wraplength=280, 
                               justify=tk.LEFT, anchor="w", font=("Helvetica", 9),
                               command=lambda item=k: self.apply_item(item))
                btn.pack(fill=tk.X, pady=2)

    def on_show_stats(self):
        self.render_stats()
        messagebox.showinfo("Stats", self.stats_text.get("1.0", tk.END))
        
    def on_check_progress(self):
        if not self.player:
            return
        
        progress = []
        progress.append("ENDING PROGRESS:")
        progress.append("")
        
        p = self.player
        
        # Show progress toward major endings
        if p["flags"].get("life_changing_breakthroughs", 0) >= 1:
            progress.append(f"🌟 Life Changing Breakthroughs: {p['flags'].get('life_changing_breakthroughs', 0)}/2 (The Life Changer ending)")
        
        if p["flags"].get("big_breakthroughs", 0) >= 2:
            progress.append(f"✨ Big Breakthroughs: {p['flags'].get('big_breakthroughs', 0)}/4 (The Zen Master ending)")
            
        if p["reputation"] >= 10:
            progress.append(f"📈 Reputation: {p['reputation']}/16 (Celebrity Therapist ending)")
            
        if p["xp"] >= 15:
            progress.append(f"🎓 Experience: {p['xp']}/25 (Experienced Professional ending)")
            
        if p["flags"].get("heated_arguments", 0) >= 1:
            progress.append(f"🔥 Heated Arguments: {p['flags'].get('heated_arguments', 0)}/3 (The Provocateur ending)")
            
        if p["flags"].get("joined_delusions", 0) >= 1:
            progress.append(f"🌀 Joined Delusions: {p['flags'].get('joined_delusions', 0)}/2 (The Convert ending)")
            
        progress.append("")
        progress.append("HIGH STAT ENDINGS:")
        if p["stats"]["Patience"] >= 10:
            progress.append(f"🧘 Patience: {p['stats']['Patience']}/15 (The Unbreakable)")
        if p["stats"]["Empathy"] >= 10:
            progress.append(f"💝 Empathy: {p['stats']['Empathy']}/15 (The Heart Whisperer)")  
        if p["stats"]["Insight"] >= 10:
            progress.append(f"🧠 Insight: {p['stats']['Insight']}/15 (The Mind Reader)")
            
        if len(progress) <= 4:
            progress.append("Keep playing to unlock ending paths!")
            
        messagebox.showinfo("Ending Progress", "\n".join(progress))

    # ---------------------------
    # Turn-based Combat System (Therapy Battle)
    # ---------------------------
    def open_debate_modal(self):
        # Disable main choices while combat in progress
        self.clear_choices()
        dwin = tk.Toplevel(self)
        dwin.transient(self)
        dwin.grab_set()
        dwin.title("Psychological Combat")
        dwin.geometry("980x450")

        # Combat state
        player_hp = self.player["stats"]["Composure"] + 5  # Start with bonus sanity for battles
        client_hp = self.current_client["absurdity"] + self.current_client["resistance"]
        turn_count = 0
        
        # UI Elements
        tk.Label(dwin, text=f"Therapeutic Battle vs {self.current_client['name']}", font=("Helvetica", 12, "bold")).pack(pady=5)
        
        status_frame = tk.Frame(dwin, relief=tk.RAISED, bd=2)
        status_frame.pack(pady=10, padx=10, fill=tk.X)
        
        # Player health bar with solid blue background
        player_frame = tk.Frame(status_frame, bg="#4A90E2", relief=tk.SUNKEN, bd=2)
        player_frame.pack(side=tk.LEFT, padx=20, pady=5)
        player_label = tk.Label(player_frame, text="YOUR SANITY", font=("Helvetica", 10, "bold"), bg="#4A90E2", fg="white")
        player_label.pack()
        player_status = tk.Label(player_frame, text=f"{player_hp} / 20", font=("Helvetica", 14, "bold"), bg="#4A90E2", fg="white")
        player_status.pack(pady=5)
        
        # Client health bar with solid red background  
        client_frame = tk.Frame(status_frame, bg="#E94B3C", relief=tk.SUNKEN, bd=2)
        client_frame.pack(side=tk.RIGHT, padx=20, pady=5)
        client_label = tk.Label(client_frame, text="CLIENT CHAOS", font=("Helvetica", 10, "bold"), bg="#E94B3C", fg="white")
        client_label.pack()
        client_status = tk.Label(client_frame, text=f"{client_hp}", font=("Helvetica", 14, "bold"), bg="#E94B3C", fg="white")
        client_status.pack(pady=5)
        
        log_frame = tk.Frame(dwin)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        combat_log = tk.Text(log_frame, height=12, wrap=tk.WORD)
        combat_log.pack(fill=tk.BOTH, expand=True)
        
        def log_message(msg):
            combat_log.insert(tk.END, msg + "\n")
            combat_log.see(tk.END)
            
        log_message(f"Combat begins! {self.current_client['name']} is having a psychological breakdown!")
        
        def update_status():
            player_status.config(text=f"{player_hp} / 20")  # Update max to reflect bonus sanity
            client_status.config(text=f"{client_hp}")
            # Keep solid colors - no more random color changes
            player_frame.config(bg="#4A90E2")  # Solid blue for player
            player_status.config(bg="#4A90E2")
            player_label.config(bg="#4A90E2")
                
            client_frame.config(bg="#E94B3C")  # Solid red for client
            client_status.config(bg="#E94B3C")
            client_label.config(bg="#E94B3C")
            
        def player_action(action_type):
            nonlocal player_hp, client_hp, turn_count
            turn_count += 1
            
            # Player turn
            if action_type == "empathy":
                # Roll dice + empathy stat
                dice_roll = random.randint(1, 6)
                damage = dice_roll + (self.player["stats"]["Empathy"] // 2)
                client_hp -= damage
                log_message(f"Turn {turn_count}: You use empathy! Rolled {dice_roll}, dealt {damage} emotional damage!")
                
            elif action_type == "insight":
                # Roll dice + insight stat  
                dice_roll = random.randint(1, 6)
                damage = dice_roll + (self.player["stats"]["Insight"] // 2)
                client_hp -= damage
                log_message(f"Turn {turn_count}: You use psychological insight! Rolled {dice_roll}, dealt {damage} reality damage!")
                
            elif action_type == "patience":
                # Defensive action - heal + reduce incoming damage
                dice_roll = random.randint(1, 4)
                heal = dice_roll + (self.player["stats"]["Patience"] // 3)
                player_hp = min(20, player_hp + heal)  # Update max to reflect bonus sanity
                log_message(f"Turn {turn_count}: You endure patiently! Rolled {dice_roll}, restored {heal} sanity!")
                self.player["flags"]["defended"] = True
                
            elif action_type == "item":
                # Use item (simplified)
                available_items = [k for k, v in self.player["inventory"].items() if v > 0]
                if available_items:
                    item = random.choice(available_items)
                    self.player["inventory"][item] -= 1
                    if item == "Coffee":
                        player_hp = min(20, player_hp + 3)  # Update max to reflect bonus sanity
                        log_message(f"Turn {turn_count}: You drink coffee! Restored 3 sanity!")
                    elif item == "Energy Drink": 
                        player_hp = min(20, player_hp + 2)  # Update max to reflect bonus sanity
                        log_message(f"Turn {turn_count}: Energy drink! Restored 2 sanity!")
                else:
                    log_message(f"Turn {turn_count}: No items available!")
            
            # Check if client defeated
            if client_hp <= 0:
                log_message("Victory! The client has achieved emotional stability!")
                log_message("Client successfully treated through combat therapy!")
                self.player["stats"]["Empathy"] = min(15, self.player["stats"]["Empathy"] + 1)
                # Set client absurdity to 0 to mark as completed
                self.current_client["absurdity"] = 0
                self.render_stats()
                # Close combat window and return to main game after victory
                def after_victory():
                    dwin.destroy()
                    self.complete_session()
                    self.advance_client()  # Move to next client, don't end day
                dwin.after(3000, after_victory)
                return
                
            # Client's turn
            client_dice = random.randint(1, 6)
            client_damage = client_dice + (self.current_client["absurdity"] // 3)
            
            # Apply defense if player defended
            if self.player["flags"].get("defended"):
                client_damage = max(1, client_damage - 2)
                self.player["flags"]["defended"] = False
                log_message(f"Client attacks for {client_damage + 2} but your patience reduces it to {client_damage}!")
            else:
                log_message(f"Client attacks with chaos! Rolled {client_dice}, deals {client_damage} psychological damage!")
                
            player_hp = max(0, player_hp - client_damage)
            
            update_status()
            
            # Check if player defeated
            if player_hp <= 0:
                log_message("Defeat! Your sanity has shattered!")
                log_message("The client remains unstable. Restarting session...")
                # Restore some composure but don't set to 0
                self.player["stats"]["Composure"] = max(1, self.player["stats"]["Composure"] - 1)
                self.render_stats()
                # Close combat window and restart the same client
                def after_defeat():
                    dwin.destroy()
                    self.append_log("Combat defeat! Restarting client session...")
                    # Reset client to starting state
                    self.current_client["node"] = "start"
                    self.current_client["absurdity"] = max(1, self.current_client["absurdity"] + 1)  # Make slightly harder
                    self.load_current_client()  # Restart same client
                dwin.after(3000, after_defeat)
                return
        
        # Combat action buttons
        btn_frame = tk.Frame(dwin)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text=f"Emotional Support\n(Reduces client chaos)\nEmpathy: {self.player['stats']['Empathy']}", 
                 command=lambda: player_action("empathy"), width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text=f"Logical Analysis\n(Breaks client delusions)\nInsight: {self.player['stats']['Insight']}", 
                 command=lambda: player_action("insight"), width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text=f"Patient Listening\n(Heals your sanity)\nPatience: {self.player['stats']['Patience']}", 
                 command=lambda: player_action("patience"), width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Use Item\n(Various effects)\nFrom inventory", 
                 command=lambda: player_action("item"), width=15).pack(side=tk.LEFT, padx=5)



    # ---------------------------
    # Typewriter effect for client & replies
    # ---------------------------
    def typewriter_write(self, text):
        # write into self.client_text using after, not blocking UI
        # clear client_text first
        self.client_text.configure(state=tk.NORMAL)
        self.client_text.delete("1.0", tk.END)
        self.client_text.configure(state=tk.DISABLED)
        
        # Use after() method instead of threading for proper typewriter effect
        self._typewriter_text = text
        self._typewriter_index = 0
        self._do_typewriter_step()
        
        # append to log
        self.append_log(text)
    
    def _do_typewriter_step(self):
        if self._typewriter_index < len(self._typewriter_text):
            # Add one more character
            current_text = self._typewriter_text[:self._typewriter_index + 1]
            self._set_client_text(current_text)
            self._typewriter_index += 1
            # Schedule next character with current speed
            self.after(self.type_speed, self._do_typewriter_step)
        else:
            # Typewriter finished - keep text visible
            self._set_client_text(self._typewriter_text)

    def _set_client_text(self, s):
        self.client_text.configure(state=tk.NORMAL)
        self.client_text.delete("1.0", tk.END)
        self.client_text.insert(tk.END, s)
        self.client_text.configure(state=tk.DISABLED)

    # ---------------------------
    # Utility controls
    # ---------------------------
    def on_speed_change(self, v):
        self.type_speed = safe_int(v, TYPE_SPEED_DEFAULT)

    def ask_confirmation(self, text):
        return messagebox.askyesno("Confirm", text)

    def on_end_day(self):
        if not self.player:
            return
        if self.ask_confirmation("End the day early?"):
            self.end_day()

    def end_day(self):
        # compute ending based on flags & stats
        if not self.player:
            messagebox.showinfo("No day", "No session played.")
            self.quit()
            return
        
        p = self.player
        ending, msg, flavor = self.determine_ending(p)
        
        # Show ending with flavor text
        full_msg = f"{msg}\n\n{flavor}\n\nEnding: {ending}"
        messagebox.showinfo("Day End", full_msg)
        self.append_log("Day ended: " + ending)
        
        # reset or exit: ask to play again
        if messagebox.askyesno("Play again?", "Start a new day with a different approach?"):
            self.show_intro()
        else:
            self.quit()
            
    def determine_ending(self, p):
        """Determine ending based on player choices and stats"""
        
        # Catastrophic endings (highest priority)
        if p["flags"].get("melted_down") or p["stats"]["Composure"] <= 0:
            return ("Mental Breakdown", 
                   "You completely lose it during a session and have to be escorted out by security.",
                   "The last thing you remember is screaming about how the clients were right all along. You're banned from practicing therapy and take up professional yodeling instead.")
        
        # Controversial/Chaotic endings
        if p["flags"].get("heated_arguments", 0) >= 3:
            return ("The Provocateur", 
                   "Your aggressive therapeutic methods make you famous... for all the wrong reasons.",
                   "You start a controversial practice called 'Combat Therapy' where you literally debate clients into submission. It's surprisingly effective, but the ethics board is not amused.")
        
        if p["flags"].get("joined_delusions", 0) >= 2:
            return ("The Convert", 
                   "You've embraced your clients' alternative realities so completely that you forget which world is real.",
                   "Last seen having philosophical discussions with kitchen appliances while leading a support group for people who believe furniture has feelings. You're very happy, but also completely insane.")
        
        # Excellent endings
        if p["flags"].get("life_changing_breakthroughs", 0) >= 2:
            return ("The Life Changer", 
                   "Your sessions don't just help clients - they fundamentally transform lives.",
                   "Three clients send you thank-you cards every month. One names their firstborn after you. Another writes a bestselling book about their breakthrough. You frame the good reviews and hide the death threats.")
        
        if p["flags"].get("big_breakthroughs", 0) >= 4 and p["stats"]["Composure"] >= 5:
            return ("The Zen Master", 
                   "You've achieved perfect therapeutic balance - wise, calm, and impossibly effective.",
                   "Other therapists study your techniques. You mostly just nod a lot and ask really good questions. Somehow this makes you internationally famous. You write a book called 'Therapeutic Nodding: An Art Form.'")
        
        # Success endings
        if p["reputation"] >= 16:
            return ("The Celebrity Therapist", 
                   "Your reputation precedes you. Everyone wants a session with the legendary Dr. " + p["name"] + ".",
                   "You get your own TV show called 'Therapy Time' where you help celebrities work through their issues with kitchen appliances. It's surprisingly popular.")
        
        if p["xp"] >= 25:
            return ("The Experienced Professional", 
                   "Years of dealing with impossible situations have made you unflappable and wise.",
                   "You open a training school for new therapists. Your first lesson: 'When a client says their toaster is sentient, just roll with it.' Student evaluations are excellent.")
        
        # Stat-based specialized endings
        if p["stats"]["Patience"] >= 15:
            return ("The Unbreakable", 
                   "Nothing phases you anymore. You could mediate a fight between hurricanes.",
                   "You become the go-to therapist for the most difficult cases. Your waiting room has a sign: 'If they're too weird for everyone else, they're perfect for Dr. " + p["name"] + ".' Business is booming.")
        
        if p["stats"]["Empathy"] >= 15:
            return ("The Heart Whisperer", 
                   "Your ability to understand and connect with anyone is genuinely supernatural.",
                   "You can make emotional breakthroughs with people through simple conversation. Even the office plants seem happier after talking to you. This concerns the janitor.")
        
        if p["stats"]["Insight"] >= 15:
            return ("The Mind Reader", 
                   "Your ability to see through problems and find solutions borders on telepathic.",
                   "You solve clients' issues so quickly they sometimes leave confused about why they came. Your sessions are booked solid, mostly by people curious about your mysterious powers.")
        
        # Middle-ground endings
        if p["reputation"] >= 12:
            return ("The Reliable Professional", 
                   "You're not famous, but you're good at what you do and people trust you.",
                   "You build a steady practice helping normal people with normal problems. It's surprisingly fulfilling, even if no one asks you to communicate with their appliances.")
        
        if p["stats"]["Composure"] >= 8:
            return ("The Steady Hand", 
                   "Whatever chaos your clients bring, you remain calm and focused.",
                   "You develop a reputation as the therapist who never loses their cool. This attracts the weirdest cases, but somehow you handle them all with grace and only mild day-drinking.")
        
        # Default/neutral endings
        if p["reputation"] >= 8:
            return ("The Decent Therapist", 
                   "You help some people, confuse others, but generally do more good than harm.",
                   "You continue working as a therapist, occasionally wondering if that client's toaster really was trying to communicate. Some questions are better left unanswered.")
        
        # Poor performance endings
        if p["reputation"] <= 5:
            return ("The Questionable Professional", 
                   "Your methods are... unconventional. The licensing board keeps a file on you.",
                   "You keep your license, barely. Your clients are an interesting mix of people who appreciate your unique approach and those who come to see what all the fuss is about.")
        
        # Final fallback
        return ("The Quiet Exit", 
               "You complete your sessions and go home, wondering what it all means.",
               "You lock your office and walk into the sunset, pondering the nature of sanity and whether you've been helping people or just enabling their delusions. Either way, it's been a day.")

    def on_quit(self):
        if messagebox.askokcancel("Quit", "Quit the game?"):
            self.destroy()

# ---------------------------
# Run app
# ---------------------------
if __name__ == "__main__":
    random.seed()
    app = TherapyApp()
    app.mainloop()
