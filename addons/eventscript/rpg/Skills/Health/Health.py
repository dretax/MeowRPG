# Health-Skill by *meow*
#
# Version 1.0


# Imports

# ES-Imports
import es

# RPG-Imports
from meowrpg import playerlist, config



# Script
skillname = 'Health'


# Load config values
rpgHealthValue = config.GetInt('rpgHealthValue') 


# Events
def unload():
    for i in playerlist.GetPlayerlist():
        try:
            del i.properties['maxHealth']
        except:
            pass 


def rpg_player_spawn(ev):
    # Get player and his maximal health
    player = playerlist[ev['userid']]
    maxHealth = 100 + player.GetSkillLevel(skillname) * rpgHealthValue
    
    # Set the player's "maxhealth" property (used by medic, regeneration and shop)   
    player.properties['maxHealth'] = maxHealth 
    player.player.setHealth(maxHealth)
    

def rpg_skill_level_changed(ev):
    if ev['skill'] == skillname:
        playerlist[ev['userid']].properties['maxHealth'] += (int(ev['level']) - int(ev['old_level'])) * rpgHealthValue