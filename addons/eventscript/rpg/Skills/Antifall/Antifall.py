# Antifall-Skill by *meow*
#
# Version 1.0


# Imports

# Python-Imports
import random

# ES-Imports
import es

# RPG-Imports
from meowrpg import playerlist, config



# Script
skillname = 'Antifall'


# Load config values
rpgAntifallChance = config.GetInt('rpgAntifallChance') 


# Events
def player_falldamage(ev):  
    player = playerlist[ev['userid']]
    level = player.GetSkillLevel(skillname)
    if level > 0:
        if random.randint(1,100) <= level * rpgAntifallChance:
            player = player.player
            player.setHealth(player.getHealth() + int(float(ev['damage'])))     