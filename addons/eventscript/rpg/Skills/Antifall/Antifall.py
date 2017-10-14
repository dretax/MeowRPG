# Antifall-Skill by Rennnyyy
#
# Version 1.0


# Imports

# Python-Imports
import random

# ES-Imports
import es

# RPG-Imports
from rpg.rpg import playerlist


# Script
skillname = 'Antifall'


def player_falldamage(ev):  
    player = playerlist[ev['userid']]
    level = player.GetSkillLevel(skillname)
    if level > 0:
        if random.randint(1,10) <= level * 2:
            player = player.player
            player.setHealth(player.getHealth() + int(ev['dmg_health']))     