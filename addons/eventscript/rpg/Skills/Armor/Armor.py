# Armor-Skill by *meow*
#
# Version 1.0


# Imports

# ES-Imports
import es

# RPG-Imports
from meowrpg import playerlist, config



# Script
skillname = 'Armor'


# Load config values
rpgArmorValue = config.GetInt('rpgArmorValue') 


# Events 
def rpg_player_spawn(ev):  
    player = playerlist[ev['userid']]
    level = player.GetSkillLevel(skillname)
    player = player.player
    if level > 0:
        armor = level * rpgArmorValue
        if player.getArmor() < armor:
            player.setArmor(armor)      