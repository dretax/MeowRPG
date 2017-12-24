# Regeneration-Skill by *meow*
#
# Version 1.0


# Imports

# ES-Imports
import playerlib
import gamethread

# RPG-Imports
from meowrpg import playerlist, config



# Script
skillname = 'Regeneration'


# Load config values
rpgRegenerationValue = config.GetInt('rpgRegenerationValue')  
rpgRegenerationInterval = config.GetFloat('rpgRegenerationInterval')


# Events        
def unload():
    gamethread.cancelDelayed('rpg_regeneration')    

def round_start(ev):
    gamethread.delayedname(rpgRegenerationInterval, 'rpg_regeneration', rpg_regeneration, ())
    
def round_end(ev):
    gamethread.cancelDelayed('rpg_regeneration') 
        
def rpg_regeneration():
    gamethread.delayedname(rpgRegenerationInterval, 'rpg_regeneration', rpg_regeneration, ())
    for i in playerlib.getPlayerList('#alive'):
        # Get the player's maxhealth, level of this skill and it's playerlib instance
        player = playerlist[i]
        level = player.GetSkillLevel(skillname)
        maxHealth = player.properties['maxHealth'] 
        player = player.player
      
        # Calculate new hp and set it 
        hp = player.getHealth() + level * rpgRegenerationValue
        if hp < maxHealth:
            player.setHealth(hp)  
        else:
            player.setHealth(maxHealth)   